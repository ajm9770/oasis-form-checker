# Using ChromaDB
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
import os
import getpass

if not os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
  os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass.getpass("Enter API key for HuggingFace: ")

# embeddings = HuggingFaceEmbeddings(
#     model_name="HuggingFaceH4/zephyr-7b-beta",
#     model_kwargs={
#       "device": "cpu",
#     },
#     encode_kwargs={'normalize_embeddings': False}
# )

# vector_store = Chroma(
#     collection_name="patient_ids",
#     embedding_function=embeddings,
#     persist_directory="../../database/chroma_langchain_test"  # Where to save data locally, remove if not necessary
# )

import chromadb
# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
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
    query_texts=["I was born in 1954", "I was born in 1991"],
    n_results=2,
    # where={"metadata_field": "is_equal_to_this"}, # optional filter
    # where_document={"$contains":"search_string"}  # optional filter
)
print(results)