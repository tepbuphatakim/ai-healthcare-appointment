import os
from typing import List, Dict, Any
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

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
        self.vectorstore.persist()
        print(f"Created vector store at {self.db_dir}")

    def setup_qa_chain(self):
        """Set up the QA chain with Ollama."""
        # Initialize Ollama with the specified model
        llm = Ollama(model="llama3.2:1b")
        
        # Create prompt template
        prompt_template = """
        Answer the question based on the provided context. If you cannot find 
        the answer in the context, say "I don't have enough information to answer this question."
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create the chain
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
        
        result = self.qa_chain({"query": question})
        return {
            "answer": result["result"],
            "sources": [doc.metadata for doc in result["source_documents"]]
        }

def main():
    # Initialize the RAG system
    rag = RAGSystem()
    
    # Create a sample document if none exists
    # if not os.path.exists("data/docs/sample.txt"):
    #     os.makedirs("data/docs", exist_ok=True)
    #     with open("data/docs/sample.txt", "w") as f:
    #         f.write("""
    #         Artificial Intelligence (AI) is the simulation of human intelligence by machines.
    #         Machine Learning is a subset of AI that enables systems to learn from data.
    #         Deep Learning is a type of Machine Learning that uses neural networks with multiple layers.
    #         Natural Language Processing (NLP) is a branch of AI that helps machines understand human language.
    #         Computer Vision is an AI field that enables machines to derive information from visual data.
    #         """)

    # Initialize the system
    rag.initialize()
    
    # Interactive query loop
    print("\nRAG System Ready! Type 'exit' to quit.")
    while True:
        question = input("\nEnter your question: ")
        if question.lower() == "exit":
            break
            
        try:
            result = rag.query(question)
            print("\nAnswer:", result["answer"])
            print("\nSources:", result["sources"])
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 