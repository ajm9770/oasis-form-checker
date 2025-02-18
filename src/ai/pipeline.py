from oasis_form_checker.ai.embeddings import embed_and_store_text
from oasis_form_checker.ai.generator import generate_oasis_response
from oasis_form_checker.ai.validation import validate_oasis_response

def run_full_pipeline(query: str, transcript_path: str):
    """Runs the end-to-end AI workflow."""
    print("Step 1: Embedding medical transcript...")
    embed_and_store_text(transcript_path)

    print("Step 2: Generating OASIS response...")
    ai_response = generate_oasis_response(query)

    print("Step 3: Validating AI output...")
    validation_status = validate_oasis_response(ai_response)

    return {"response": ai_response, "validation": validation_status}

if __name__ == "__main__":
    query = "Summarize the patient's fall risk assessment."
    transcript_path = "path/to/patient_transcript.txt"
    
    result = run_full_pipeline(query, transcript_path)
    print("Final AI Output:\n", result)