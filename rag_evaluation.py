import os
import json
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from rouge import Rouge
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import nltk
from langchain_huggingface import HuggingFaceEmbeddings
from rag_system import RAGSystem

# Download NLTK data
try:
    nltk.download('punkt')
except:
    pass

class RAGEvaluator:
    def __init__(self, rag_system: RAGSystem, ground_truth_file: str = "evaluation/ground_truth.json"):
        """Initialize the RAG evaluator with a RAG system and ground truth data."""
        self.rag_system = rag_system
        self.ground_truth_file = ground_truth_file
        self.ground_truth = self._load_ground_truth()
        self.rouge = Rouge()
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    def _load_ground_truth(self) -> List[Dict[str, str]]:
        """Load ground truth data from a JSON file."""
        if not os.path.exists(self.ground_truth_file):
            os.makedirs(os.path.dirname(self.ground_truth_file), exist_ok=True)
            # Create sample ground truth if file doesn't exist
            sample_data = [
                {
                    "question": "What are Dr. Sopheak Rith's working hours?",
                    "answer": "Dr. Sopheak Rith works Monday-Friday, 8:00 AM - 4:00 PM."
                },
                {
                    "question": "What languages does Dr. Maria Santos speak?",
                    "answer": "Dr. Maria Santos speaks English and Spanish."
                },
                {
                    "question": "What is Dr. Sopheak's specialization?",
                    "answer": "Dr. Sopheak Rith is a Chief Cardiologist specializing in Interventional Cardiology."
                }
            ]
            with open(self.ground_truth_file, 'w') as f:
                json.dump(sample_data, f, indent=2)
            
            print(f"Created sample ground truth file at {self.ground_truth_file}")
            print("Please update this file with accurate question-answer pairs before evaluation.")
            return sample_data
        
        with open(self.ground_truth_file, 'r') as f:
            return json.load(f)
    
    def evaluate_all(self) -> Dict[str, Any]:
        """Run all evaluations and return combined results."""
        results = {
            "exact_match": self.evaluate_exact_match(),
            "semantic_similarity": self.evaluate_semantic_similarity(),
            "rouge": self.evaluate_rouge(),
            "bleu": self.evaluate_bleu(),
            "retrieval_precision": self.evaluate_retrieval_precision()
        }
        
        # Calculate overall score (weighted average)
        overall = (
            results["exact_match"]["score"] * 0.1 +
            results["semantic_similarity"]["score"] * 0.3 +
            results["rouge"]["rouge-l"]["f"] * 0.3 +
            results["bleu"]["score"] * 0.1 +
            results["retrieval_precision"]["score"] * 0.2
        )
        
        results["overall"] = overall
        return results
    
    def evaluate_exact_match(self) -> Dict[str, Any]:
        """Evaluate exact match accuracy."""
        correct = 0
        results = []
        
        for item in self.ground_truth:
            question = item["question"]
            expected = item["answer"].lower().strip()
            
            # Get RAG response
            response = self.rag_system.query(question)
            actual = response["answer"].lower().strip()
            
            # Check exact match
            is_match = expected == actual
            if is_match:
                correct += 1
            
            results.append({
                "question": question,
                "expected": expected,
                "actual": actual,
                "match": is_match
            })
        
        score = correct / len(self.ground_truth) if self.ground_truth else 0
        return {
            "score": score,
            "details": results
        }
    
    def evaluate_semantic_similarity(self) -> Dict[str, Any]:
        """Evaluate semantic similarity between expected and actual answers."""
        similarities = []
        results = []
        
        for item in self.ground_truth:
            question = item["question"]
            expected = item["answer"]
            
            # Get RAG response
            response = self.rag_system.query(question)
            actual = response["answer"]
            
            # Get embeddings
            expected_embedding = self.embeddings.embed_query(expected)
            actual_embedding = self.embeddings.embed_query(actual)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                [expected_embedding], 
                [actual_embedding]
            )[0][0]
            
            similarities.append(similarity)
            results.append({
                "question": question,
                "expected": expected,
                "actual": actual,
                "similarity": similarity
            })
        
        avg_similarity = np.mean(similarities) if similarities else 0
        return {
            "score": avg_similarity,
            "details": results
        }
    
    def evaluate_rouge(self) -> Dict[str, Any]:
        """Evaluate using ROUGE metrics."""
        all_expected = []
        all_actual = []
        results = []
        
        for item in self.ground_truth:
            question = item["question"]
            expected = item["answer"]
            
            # Get RAG response
            response = self.rag_system.query(question)
            actual = response["answer"]
            
            all_expected.append(expected)
            all_actual.append(actual)
            
            # Calculate individual ROUGE scores
            try:
                rouge_scores = self.rouge.get_scores(actual, expected)[0]
                results.append({
                    "question": question,
                    "expected": expected,
                    "actual": actual,
                    "rouge-1": rouge_scores["rouge-1"],
                    "rouge-2": rouge_scores["rouge-2"],
                    "rouge-l": rouge_scores["rouge-l"]
                })
            except:
                # Handle cases where ROUGE calculation fails
                results.append({
                    "question": question,
                    "expected": expected,
                    "actual": actual,
                    "error": "Failed to calculate ROUGE scores"
                })
        
        # Calculate average ROUGE scores
        try:
            avg_scores = self.rouge.get_scores(all_actual, all_expected, avg=True)
            return {
                "rouge-1": avg_scores["rouge-1"],
                "rouge-2": avg_scores["rouge-2"],
                "rouge-l": avg_scores["rouge-l"],
                "details": results
            }
        except:
            # Fallback if average calculation fails
            return {
                "rouge-1": {"f": 0, "p": 0, "r": 0},
                "rouge-2": {"f": 0, "p": 0, "r": 0},
                "rouge-l": {"f": 0, "p": 0, "r": 0},
                "details": results,
                "error": "Failed to calculate average ROUGE scores"
            }
    
    def evaluate_bleu(self) -> Dict[str, Any]:
        """Evaluate using BLEU score."""
        scores = []
        results = []
        smoothing = SmoothingFunction().method1
        
        for item in self.ground_truth:
            question = item["question"]
            expected = item["answer"]
            
            # Get RAG response
            response = self.rag_system.query(question)
            actual = response["answer"]
            
            # Tokenize
            reference = [expected.split()]
            candidate = actual.split()
            
            # Calculate BLEU score
            try:
                bleu_score = sentence_bleu(reference, candidate, smoothing_function=smoothing)
                scores.append(bleu_score)
                results.append({
                    "question": question,
                    "expected": expected,
                    "actual": actual,
                    "bleu": bleu_score
                })
            except:
                results.append({
                    "question": question,
                    "expected": expected,
                    "actual": actual,
                    "error": "Failed to calculate BLEU score"
                })
        
        avg_bleu = np.mean(scores) if scores else 0
        return {
            "score": avg_bleu,
            "details": results
        }
    
    def evaluate_retrieval_precision(self) -> Dict[str, Any]:
        """Evaluate retrieval precision by checking if the correct documents were retrieved."""
        # This is a simplified version - ideally you would have ground truth for which documents should be retrieved
        results = []
        retrieval_scores = []
        
        for item in self.ground_truth:
            question = item["question"]
            
            # Get RAG response with source documents
            response = self.rag_system.query(question)
            sources = response["sources"]
            
            # For simplicity, we'll just check if any sources were retrieved
            # In a real evaluation, you would check if the correct sources were retrieved
            retrieval_score = 1.0 if sources else 0.0
            retrieval_scores.append(retrieval_score)
            
            results.append({
                "question": question,
                "sources": sources,
                "score": retrieval_score
            })
        
        avg_score = np.mean(retrieval_scores) if retrieval_scores else 0
        return {
            "score": avg_score,
            "details": results
        }

def main():
    # Initialize RAG system
    rag_system = RAGSystem()
    rag_system.initialize()
    
    # Initialize evaluator
    evaluator = RAGEvaluator(rag_system)
    
    # Run evaluation
    results = evaluator.evaluate_all()
    
    # Print results
    print("\n=== RAG System Evaluation Results ===\n")
    print(f"Overall Score: {results['overall']:.4f}\n")
    
    print(f"Exact Match Accuracy: {results['exact_match']['score']:.4f}")
    print(f"Semantic Similarity: {results['semantic_similarity']['score']:.4f}")
    print(f"ROUGE-L F1 Score: {results['rouge']['rouge-l']['f']:.4f}")
    print(f"BLEU Score: {results['bleu']['score']:.4f}")
    print(f"Retrieval Precision: {results['retrieval_precision']['score']:.4f}")
    
    # Save detailed results
    os.makedirs("evaluation", exist_ok=True)
    with open("evaluation/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to evaluation/results.json")

if __name__ == "__main__":
    main() 