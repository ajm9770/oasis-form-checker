"""Document embedding and vector storage for patient data."""

from pathlib import Path
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from src.config.settings import (
    CHROMA_DB_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL
)


class DocumentEmbedder:
    """Handles document embedding and storage in ChromaDB."""

    def __init__(self, collection_name: str = CHROMA_COLLECTION_NAME):
        """Initialize the document embedder with ChromaDB and local embeddings."""
        # Use local HuggingFace embeddings (no API key required)
        self.embedding_function = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DB_DIR)
        )

        # Initialize vector store
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=collection_name,
            embedding_function=self.embedding_function
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def embed_file(self, file_path: str, patient_id: str, doc_type: str = "transcript") -> int:
        """
        Load, chunk, and embed a document file.

        Args:
            file_path: Path to the document file
            patient_id: Patient identifier
            doc_type: Type of document (transcript, history, etc.)

        Returns:
            Number of chunks created and stored
        """
        # Load document
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()

        # Add metadata
        for doc in documents:
            doc.metadata.update({
                "patient_id": patient_id,
                "doc_type": doc_type,
                "source": file_path
            })

        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)

        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i

        # Store in vector database
        self.vectorstore.add_documents(chunks)

        print(f"✓ Embedded {len(chunks)} chunks from {file_path}")
        return len(chunks)

    def embed_text(self, text: str, patient_id: str, doc_type: str = "note") -> int:
        """
        Embed raw text directly.

        Args:
            text: Text content to embed
            patient_id: Patient identifier
            doc_type: Type of document

        Returns:
            Number of chunks created and stored
        """
        # Create document
        doc = Document(
            page_content=text,
            metadata={
                "patient_id": patient_id,
                "doc_type": doc_type
            }
        )

        # Split into chunks
        chunks = self.text_splitter.split_documents([doc])

        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i

        # Store in vector database
        self.vectorstore.add_documents(chunks)

        print(f"✓ Embedded {len(chunks)} chunks of {doc_type}")
        return len(chunks)

    def clear_patient_data(self, patient_id: str):
        """Remove all documents for a specific patient."""
        # Note: This requires querying and deleting by metadata
        # ChromaDB's delete by metadata is limited, so this is a simplified version
        print(f"⚠ Warning: Patient data cleanup not fully implemented for {patient_id}")
        # In production, you'd want to implement proper document ID tracking

    def get_retriever(self, patient_id: Optional[str] = None, k: int = 5):
        """
        Get a retriever for similarity search.

        Args:
            patient_id: Optional patient ID to filter results
            k: Number of documents to retrieve

        Returns:
            LangChain retriever object
        """
        search_kwargs = {"k": k}

        if patient_id:
            search_kwargs["filter"] = {"patient_id": patient_id}

        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)


def embed_patient_documents(patient_id: str, transcript_path: str, history_path: str) -> DocumentEmbedder:
    """
    Convenience function to embed all patient documents.

    Args:
        patient_id: Patient identifier
        transcript_path: Path to transcript file
        history_path: Path to patient history file

    Returns:
        Configured DocumentEmbedder instance
    """
    embedder = DocumentEmbedder()

    print(f"Embedding documents for patient {patient_id}...")
    embedder.embed_file(transcript_path, patient_id, "transcript")
    embedder.embed_file(history_path, patient_id, "history")

    print("✓ All documents embedded successfully!")
    return embedder


if __name__ == "__main__":
    # Test with sample data
    from src.config.settings import RAW_DATA_DIR

    patient_id = "PAT-2024-001"
    transcript = RAW_DATA_DIR / "sample_transcript.txt"
    history = RAW_DATA_DIR / "sample_patient_history.txt"

    if transcript.exists() and history.exists():
        embedder = embed_patient_documents(patient_id, str(transcript), str(history))
        print("\n✓ Embedding test completed!")
    else:
        print("❌ Sample data files not found")
