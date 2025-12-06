"""Document retrieval for OASIS form context."""

from typing import List, Dict, Optional
from langchain.schema import Document

from src.ai.embeddings import DocumentEmbedder
from src.config.settings import CHROMA_COLLECTION_NAME


class ContextRetriever:
    """Retrieves relevant context for OASIS form filling."""

    def __init__(self, collection_name: str = CHROMA_COLLECTION_NAME):
        """Initialize the context retriever."""
        self.embedder = DocumentEmbedder(collection_name=collection_name)

    def retrieve_for_query(
        self,
        query: str,
        patient_id: Optional[str] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Retrieve relevant documents for a specific query.

        Args:
            query: The question or topic to search for
            patient_id: Optional patient ID to filter results
            k: Number of documents to retrieve

        Returns:
            List of relevant document chunks
        """
        retriever = self.embedder.get_retriever(patient_id=patient_id, k=k)
        documents = retriever.get_relevant_documents(query)
        return documents

    def retrieve_patient_context(
        self,
        patient_id: str,
        queries: Optional[List[str]] = None
    ) -> Dict[str, List[Document]]:
        """
        Retrieve comprehensive context for a patient.

        Args:
            patient_id: Patient identifier
            queries: Optional list of specific queries to retrieve context for

        Returns:
            Dictionary mapping query topics to relevant documents
        """
        if queries is None:
            # Default queries for OASIS form sections
            queries = [
                "patient demographics age gender",
                "primary diagnosis medical conditions",
                "cognitive function mental status confusion memory",
                "activities of daily living bathing dressing grooming toileting",
                "mobility ambulation walking fall risk assistive devices",
                "medications prescriptions drug regimen",
                "living situation caregiver support home environment",
                "pain symptoms functional limitations"
            ]

        context = {}
        for query in queries:
            docs = self.retrieve_for_query(query, patient_id=patient_id, k=3)
            context[query] = docs

        return context

    def format_context_for_llm(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into a context string for LLM.

        Args:
            documents: List of document chunks

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("doc_type", "unknown")
            content = doc.page_content.strip()
            context_parts.append(f"[Source {i} - {source}]:\n{content}")

        return "\n\n".join(context_parts)

    def get_full_patient_context(self, patient_id: str) -> str:
        """
        Get comprehensive formatted context for a patient.

        Args:
            patient_id: Patient identifier

        Returns:
            Formatted context string with all relevant information
        """
        context_dict = self.retrieve_patient_context(patient_id)

        formatted_sections = []
        for query, docs in context_dict.items():
            if docs:
                section = f"## Context for: {query}\n"
                section += self.format_context_for_llm(docs)
                formatted_sections.append(section)

        return "\n\n---\n\n".join(formatted_sections)


def retrieve_relevant_context(
    patient_id: str,
    specific_query: Optional[str] = None
) -> str:
    """
    Convenience function to retrieve and format patient context.

    Args:
        patient_id: Patient identifier
        specific_query: Optional specific query, otherwise retrieves comprehensive context

    Returns:
        Formatted context string
    """
    retriever = ContextRetriever()

    if specific_query:
        docs = retriever.retrieve_for_query(specific_query, patient_id=patient_id, k=5)
        return retriever.format_context_for_llm(docs)
    else:
        return retriever.get_full_patient_context(patient_id)


if __name__ == "__main__":
    # Test retrieval
    patient_id = "PAT-2024-001"

    print("Testing context retrieval...")
    print("=" * 80)

    retriever = ContextRetriever()

    # Test specific query
    print("\n1. Testing specific query retrieval:")
    print("-" * 80)
    query = "What are the patient's mobility limitations and fall risk?"
    docs = retriever.retrieve_for_query(query, patient_id=patient_id, k=3)
    print(f"Query: {query}")
    print(f"Retrieved {len(docs)} documents")
    print("\nFormatted context:")
    print(retriever.format_context_for_llm(docs))

    # Test comprehensive context
    print("\n\n2. Testing comprehensive patient context retrieval:")
    print("-" * 80)
    full_context = retriever.get_full_patient_context(patient_id)
    print(f"Retrieved comprehensive context ({len(full_context)} characters)")
    print("\nFirst 500 characters:")
    print(full_context[:500] + "...")
