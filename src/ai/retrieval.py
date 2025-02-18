from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

# Load ChromaDB
vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # Retrieve top 3 relevant chunks

def retrieve_relevant_text(query: str):
    """Retrieves relevant transcript sections based on query."""
    results = retriever.get_relevant_documents(query)
    return [doc.page_content for doc in results]

if __name__ == "__main__":
    query = "What were the patient's primary symptoms?"
    response = retrieve_relevant_text(query)
    print("Retrieved text:", response)