import os
from typing import List, Dict, Any
from flask import Flask, request, jsonify
from flask_cors import cross_origin
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from datetime import datetime

app = Flask(__name__)

# Simple in-memory store for appointments (replace with a database in production)
appointments: List[Dict[str, Any]] = []


class RAGSystem:
    def __init__(self, docs_dir: str = "data/docs", db_dir: str = "data/vectordb"):
        """Initialize RAG system with directory paths."""
        self.docs_dir = docs_dir
        self.db_dir = db_dir
        self.vectorstore = None
        self.qa_chain = None

        # Create directories if they don't exist
        os.makedirs(docs_dir, exist_ok=True)
        os.makedirs(db_dir, exist_ok=True)

    def load_documents(self) -> List[Any]:
        """Load all text documents from the docs directory."""
        loader = DirectoryLoader(
            self.docs_dir,
            glob="**/*.txt",
            loader_cls=TextLoader
        )
        documents = loader.load()
        print(f"Loaded {len(documents)} documents")
        return documents

    def process_documents(self, documents: List[Any]) -> List[Any]:
        """Split documents into chunks."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Split into {len(chunks)} chunks")
        return chunks

    def setup_vectorstore(self, chunks: List[Any]):
        """Create and persist vector store."""
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=self.db_dir
        )
        print(f"Created vector store at {self.db_dir}")

    def setup_qa_chain(self):
        """Set up the QA chain with Ollama."""
        llm = OllamaLLM(model="llama3.2:1b")

        prompt_template = """You are a helpful hospital assistant that helps patients find the right specialist and schedule appointments. Use the provided hospital information to assist patients.

        If you cannot find specific information in the context, say "I apologize, but I don't have enough information about that. Please contact our hospital directly at (555) 123-4567 for more details."

        When suggesting doctors:
        1. Consider their specialization and expertise
        2. Check their available working hours
        3. Mention their languages spoken
        4. Note any emergency consultation availability

        When discussing scheduling:
        1. Mention the doctor's regular working hours
        2. Specify if booking is required
        3. Provide relevant contact information: (555) 123-4567
        4. Note any special instructions for appointments

        Context: {context}

        Patient Question: {question}

        Assistant Response:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )

    def initialize(self):
        """Initialize the complete RAG system."""
        documents = self.load_documents()
        chunks = self.process_documents(documents)
        self.setup_vectorstore(chunks)
        self.setup_qa_chain()
        print("RAG system initialized and ready!")

    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system."""
        if not self.qa_chain:
            raise ValueError("RAG system not initialized. Call initialize() first.")

        result = self.qa_chain.invoke({"query": question})
        return {
            "answer": result["result"],
            "sources": [doc.metadata for doc in result["source_documents"]]
        }


# Initialize RAG system
rag_system = RAGSystem()
rag_system.initialize()


# RAG Query Endpoint
@app.route('/api/query', methods=['POST'])
@cross_origin()
def api_query():
    """API endpoint for querying the RAG system."""
    data = request.json
    if not data or 'question' not in data:
        return jsonify({"error": "Missing 'question' in request"}), 400

    try:
        result = rag_system.query(data['question'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Booking Appointment Endpoint
@app.route('/api/book-appointment', methods=['POST'])
@cross_origin()
def api_book_appointment():
    """API endpoint for booking an appointment."""
    data = request.json
    if not data or 'doctor' not in data or 'patient_name' not in data or 'appointment_time' not in data:
        return jsonify({"error": "Missing required fields: 'doctor', 'patient_name', 'appointment_time'"}), 400

    doctor = data['doctor']
    patient_name = data['patient_name']
    try:
        appointment_time = datetime.strptime(data['appointment_time'], '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify({"error": "Invalid 'appointment_time' format. Use 'YYYY-MM-DD HH:MM'"}), 400

    # Basic validation (expand as needed based on doctor availability from RAG data)
    if appointment_time < datetime.now():
        return jsonify({"error": "Cannot book appointments in the past"}), 400

    # Simulate booking (replace with actual logic if integrated with a database)
    appointment = {
        "doctor": doctor,
        "patient_name": patient_name,
        "appointment_time": appointment_time.strftime('%Y-%m-%d %H:%M'),
        "status": "confirmed"
    }
    appointments.append(appointment)

    return jsonify({
        "message": f"Appointment booked with {doctor} for {patient_name} on {appointment_time.strftime('%Y-%m-%d %H:%M')}",
        "appointment": appointment
    }), 201


# Health Check Endpoint
@app.route('/api/health', methods=['GET'])
@cross_origin()
def api_health():
    """API endpoint for checking system health."""
    return jsonify({
        "status": "healthy",
        "system_ready": rag_system.qa_chain is not None,
        "appointments_count": len(appointments)
    })


def main():
    # Run the Flask app
    print("\nStarting RAG API server on http://localhost:5000")
    print("Available endpoints:")
    print("  - POST /api/query")
    print("  - POST /api/book-appointment")
    print("  - GET /api/health")
    print("\nExample usage:")
    print('  curl -X POST http://localhost:5000/api/query -H "Content-Type: application/json" -d \'{"question": "When does Dr. Sopheak work?"}\'')
    print(
        '  curl -X POST http://localhost:5000/api/book-appointment -H "Content-Type: application/json" -d \'{"doctor": "Dr. Sopheak", "patient_name": "John Doe", "appointment_time": "2025-03-19 10:00"}\'')
    app.run(host='0.0.0.0', port=5000)


if __name__ == "__main__":
    main()