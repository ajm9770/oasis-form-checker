from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize OpenAI Embedding Model
embedding_model = OpenAIEmbeddings()

# Initialize ChromaDB
CHROMA_DB_DIR = "../../data/chroma_db"
vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embedding_model)

def embed_and_store_text(document_path: str):
    """Reads, embeds, and stores a medical transcript in ChromaDB."""
    loader = TextLoader(document_path)
    docs = loader.load()

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)

    # Store in vector database
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    print("Embeddings stored successfully!")

if __name__ == "__main__":
    embed_and_store_text("path/to/transcript.txt")