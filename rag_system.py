import os
import uuid
from typing import List, Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from fpdf import FPDF

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

DOCTOR_AVAILABILITY = {
    "Dr. Sopheak": {
        "specialization": "Cardiology",
        "languages": ["English", "Khmer"],
        "working_hours": {
            "2025-03-18": ["10:00 AM", "11:00 AM", "2:00 PM"],
            "2025-03-19": ["9:00 AM", "1:00 PM", "3:00 PM"]
        },
        "emergency_available": True
    },
    "Dr. Leakena": {
        "specialization": "Pediatrics",
        "languages": ["English", "Khmer"],
        "working_hours": {
            "2025-03-18": ["9:00 AM", "12:00 PM"],
            "2025-03-19": ["10:00 AM", "2:00 PM"]
        },
        "emergency_available": False
    }
}

booking_sessions: Dict[str, Dict[str, Any]] = {}

class RAGSystem:
    def __init__(self, docs_dir: str = "data/docs", db_dir: str = "data/vectordb"):
        self.docs_dir = docs_dir
        self.db_dir = db_dir
        self.vectorstore = None
        self.qa_chain = None
        os.makedirs(docs_dir, exist_ok=True)
        os.makedirs(db_dir, exist_ok=True)

    def load_documents(self) -> List[Any]:
        try:
            loader = DirectoryLoader(self.docs_dir, glob="**/*.txt", loader_cls=TextLoader)
            documents = loader.load()
            print(f"Loaded {len(documents)} documents from {self.docs_dir}")
            return documents
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []

    def process_documents(self, documents: List[Any]) -> List[Any]:
        if not documents:
            print("No documents to process")
            return []
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        print(f"Split into {len(chunks)} chunks")
        return chunks

    def setup_vectorstore(self, chunks: List[Any]):
        if not chunks:
            print("No chunks available for vectorstore creation")
            return
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=self.db_dir
        )
        print(f"Vector store created at {self.db_dir}")

    def setup_qa_chain(self):
        if not self.vectorstore:
            print("Vectorstore not initialized, skipping QA chain setup")
            return
        llm = OllamaLLM(model="llama3.2:1b")
        prompt_template = """You are a helpful hospital assistant. Use the provided hospital information to assist patients.

        If you cannot find specific information, say "I apologize, but I don't have enough information about that. Please contact our hospital at (555) 123-4567."

        Context: {context}

        Patient Question: {question}

        Assistant Response:"""
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )

    def initialize(self):
        documents = self.load_documents()
        chunks = self.process_documents(documents)
        self.setup_vectorstore(chunks)
        self.setup_qa_chain()
        status = "fully" if self.qa_chain else "partially"
        print(f"RAG system initialized {status}!")

    def query(self, question: str) -> Dict[str, Any]:
        if not self.qa_chain:
            return {"answer": "RAG system not fully initialized.", "sources": []}
        try:
            result = self.qa_chain.invoke({"query": question})
            return {
                "answer": result["result"],
                "sources": [doc.metadata for doc in result["source_documents"]]
            }
        except Exception as e:
            print(f"Query error: {e}")
            return {"answer": f"Error processing query: {str(e)}", "sources": []}

    def generate_booking_confirmation(self, name: str, doctor: str, date: str, time: str) -> str:
        question = f"Generate a confirmation message for {name} booking an appointment with {doctor} on {date} at {time}."
        result = self.query(question)
        return result["answer"]

rag_system = RAGSystem()
rag_system.initialize()

@app.route('/api/book-appointment', methods=['POST'])
def api_book_appointment():
    data = request.get_json() or {}
    session_id = data.get('session_id')

    if not session_id:
        session_id = str(uuid.uuid4())
        booking_sessions[session_id] = {"step": 1}
        return jsonify({
            "session_id": session_id,
            "message": "Hello! Let's book your appointment. What is your name?"
        }), 200

    if session_id not in booking_sessions:
        return jsonify({"error": "Invalid or expired session ID"}), 400

    session = booking_sessions[session_id]
    step = session.get("step")

    if step == 1:
        name = data.get("name", "").strip()
        if len(name) < 2:
            return jsonify({"message": "Please provide a valid name (at least 2 characters)."}), 400
        session["name"] = name
        session["step"] = 2
        doctors = ", ".join(DOCTOR_AVAILABILITY.keys())
        return jsonify({
            "session_id": session_id,
            "message": f"Nice to meet you, {name}! Which doctor would you like to book with? Available: {doctors}."
        }), 200

    elif step == 2:
        doctor_input = (data.get("doctor") or data.get("input", "")).strip().lower()
        print(f"Received data: {data}")
        print(f"Doctor input: '{doctor_input}'")
        doctor = None
        for key in DOCTOR_AVAILABILITY.keys():
            print(f"Checking against: '{key.lower()}' or '{key.lower().replace('dr.', '').strip()}'")
            if doctor_input == key.lower() or doctor_input == key.lower().replace("dr.", "").strip():
                doctor = key
                break
        if not doctor:
            doctors = ", ".join(DOCTOR_AVAILABILITY.keys())
            print(f"No match found, returning error: {doctors}")
            return jsonify({"message": f"Please choose a valid doctor: {doctors}."}), 400
        session["doctor"] = doctor
        session["step"] = 3
        dates = ", ".join(DOCTOR_AVAILABILITY[doctor]["working_hours"].keys())
        return jsonify({
            "session_id": session_id,
            "message": f"Great! Dr. {doctor} is available on: {dates}. Please choose a date (YYYY-MM-DD)."
        }), 200

    elif step == 3:
        date = (data.get("date") or data.get("input", "")).strip()
        doctor = session["doctor"]
        print(f"Step 3 - Received data: {data}")
        print(f"Session: {session}")
        print(f"Doctor: '{doctor}', Date input: '{date}'")
        print(f"Available dates: {list(DOCTOR_AVAILABILITY[doctor]['working_hours'].keys())}")
        if date not in DOCTOR_AVAILABILITY[doctor]["working_hours"]:
            dates = ", ".join(DOCTOR_AVAILABILITY[doctor]["working_hours"].keys())
            print(f"Date '{date}' not found in available dates")
            return jsonify({"message": f"Please choose a valid date for Dr. {doctor}: {dates}."}), 400
        session["date"] = date
        session["step"] = 4
        times = ", ".join(DOCTOR_AVAILABILITY[doctor]["working_hours"][date])
        return jsonify({
            "session_id": session_id,
            "message": f"On {date}, Dr. {doctor} is available at: {times}. Please choose a time."
        }), 200

    elif step == 4:
        time = data.get("time", "").strip()
        doctor = session["doctor"]
        date = session["date"]
        if time not in DOCTOR_AVAILABILITY[doctor]["working_hours"][date]:
            times = ", ".join(DOCTOR_AVAILABILITY[doctor]["working_hours"][date])
            return jsonify({"message": f"Please choose a valid time for {date}: {times}."}), 400

        name = session["name"]
        confirmation_text = rag_system.generate_booking_confirmation(name, doctor, date, time)

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, confirmation_text)
            filename = f"appointment_{name}_{doctor}_{date}_{time.replace(':', '-')}.pdf"
            pdf_output_path = os.path.join("bookings", filename)
            pdf.output(pdf_output_path)
        except Exception as e:
            print(f"Failed to generate PDF: {e}")
            filename = None

        DOCTOR_AVAILABILITY[doctor]["working_hours"][date].remove(time)
        if not DOCTOR_AVAILABILITY[doctor]["working_hours"][date]:
            del DOCTOR_AVAILABILITY[doctor]["working_hours"][date]

        del booking_sessions[session_id]

        response = {"message": "Appointment booked successfully", "confirmation": confirmation_text}
        if filename:
            response["document"] = filename
        return jsonify(response), 200

    return jsonify({"error": "Unknown step"}), 500

if __name__ == "__main__":
    os.makedirs("bookings", exist_ok=True)
    app.run(host="127.0.0.1", port=5000, debug=True)