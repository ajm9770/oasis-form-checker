# Using ChromaDB
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=".chroma_db"
))

collection = client.create_collection("patient_docs")