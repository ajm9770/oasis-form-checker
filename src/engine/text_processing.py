from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

embedder = OpenAIEmbeddings(model="text-embedding-3-small")

def process_document(text, patient_id, doc_type):
    chunks = text_splitter.split_text(text)
    embeddings = embedder.embed_documents(chunks)
    
    # Store in Chroma
    collection.add(
        ids=[f"{patient_id}_{doc_type}_{i}" for i in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{
            "patient_id": patient_id,
            "doc_type": doc_type,
            "chunk_num": i
        } for i in range(len(chunks))]
    )