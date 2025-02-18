from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from src.ai.retrieval import retrieve_relevant_text

# Initialize OpenAI Model
llm = OpenAI(temperature=0)

def generate_oasis_response(query: str):
    """Generates AI-powered OASIS form responses."""
    context = retrieve_relevant_text(query)  # Retrieve relevant data
    prompt = f"Based on the following patient transcript:\n\n{context}\n\nAnswer the question: {query}"
    
    response = llm.predict(prompt)
    return response

if __name__ == "__main__":
    query = "Summarize the patient's mobility limitations."
    response = generate_oasis_response(query)
    print("🤖 AI Response:", response)