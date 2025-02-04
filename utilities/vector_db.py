# Using ChromaDB
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
import getpass

if not os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
  os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass.getpass("Enter API key for HuggingFace: ")

embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={
      "device": "cpu",
    },
    encode_kwargs={'normalize_embeddings': False}
)

vector_store = Chroma(
    collection_name="patient_ids",
    embedding_function=embeddings,
    persist_directory="../../database/chroma_langchain_test"  # Where to save data locally, remove if not necessary
)

import chromadb
# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
from langchain_text_splitters import AI21SemanticTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

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
client = chromadb.Client()

# Create collection. get_collection, get_or_create_collection, delete_collection also available!
collection = client.create_collection("patient_ids")

current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the raw data directory
raw_data_dir = os.path.join(current_dir, "..", "data", "raw")
documents = []
metadatas=[]
ids=[]
for filename in os.listdir(raw_data_dir):
    # Check if the file is a text file
    if filename.endswith(".txt"):
        # Extract the patient number from the filename
        file_id = filename.split(".")[0]
        source_type = "history" if "hist" in filename else "transcript"
        with open(os.path.join(raw_data_dir, filename), "r") as f:
            document = f.read()
        documents.append(document)
        metadatas.append({"source": source_type})
        ids.append(file_id)

# Add docs to the collection. Can also update and delete. Row-based API coming soon!
collection.add(
    documents=documents, # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
    metadatas=metadatas, # filter on these!
    ids=ids, # unique for each doc
)

# Query/search 2 most similar results. You can also .get by id
results = collection.query(
    query_texts=["What is the most common care plan?"],
    n_results=2,
    # where={"metadata_field": "is_equal_to_this"}, # optional filter
    # where_document={"$contains":"search_string"}  # optional filter
)
print(results)