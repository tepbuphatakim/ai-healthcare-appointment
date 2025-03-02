# RAG System with Llama 3

A Retrieval-Augmented Generation (RAG) system built with LangChain and Llama 3, designed to answer questions based on your text documents.

## Features

- 📚 Document loading and processing from text files
- 🔄 Automatic text chunking with overlap
- 💾 Persistent vector storage using Chroma DB
- 🤖 Powered by Llama 3 (1b) through Ollama
- 🔍 Semantic search using Sentence Transformers
- 📝 Source tracking for answers

## Prerequisites

1. Python 3.8 or higher
2. [Ollama](https://ollama.ai/) installed and running
3. At least 8GB RAM recommended
4. About 4GB free disk space for models

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd <repo-directory>
```

2. Install Ollama and pull the Llama 3 model:
```bash
# Install Ollama from https://ollama.ai/
ollama pull llama3.2:1b
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. **Prepare Your Documents**
   - Place your .txt files in the `data/docs` directory
   - By default, a sample AI-related text file will be created if none exists

2. **Run the System**
```bash
python rag_system.py
```

3. **Ask Questions**
   - Type your questions when prompted
   - Type 'exit' to quit

Example interaction:
```
RAG System Ready! Type 'exit' to quit.

Enter your question: What is Machine Learning?

Answer: Machine Learning is a subset of AI that enables systems to learn from data.

Sources: [{'source': 'data/docs/sample.txt'}]
```

## Project Structure

```
.
├── data/
│   ├── docs/          # Your text documents go here
│   └── vectordb/      # Vector database storage
├── rag_system.py      # Main RAG implementation
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Customization

You can modify the following parameters in `rag_system.py`:

- `chunk_size`: Size of text chunks (default: 500)
- `chunk_overlap`: Overlap between chunks (default: 50)
- `k`: Number of retrieved documents (default: 3)
- Model settings in `setup_qa_chain()`

## Troubleshooting

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check if the model is downloaded: `ollama list`

2. **Memory Issues**
   - Reduce `chunk_size` in `process_documents()`
   - Process fewer documents at once

3. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

## License

MIT License - feel free to use and modify for your needs.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 