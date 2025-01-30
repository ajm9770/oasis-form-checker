# Using ChromaDB
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
import getpass

if not os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
  os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass.getpass("Enter API key for HuggingFace: ")

embeddings = HuggingFaceEmbeddings(
    model_name="HuggingFaceH4/zephyr-7b-beta",
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
