import re

def validate_oasis_response(response: str):
    """Validates AI-generated responses against OASIS structure."""
    required_fields = ["Diagnosis", "Medications", "Symptoms"]
    missing_fields = [field for field in required_fields if field.lower() not in response.lower()]

    # Basic validation checks
    if missing_fields:
        return f"Warning: Missing fields - {missing_fields}"
    if not re.search(r"\d{4}-\d{2}-\d{2}", response):  # Ensures dates are formatted
        return "Warning: Missing or incorrect date format (YYYY-MM-DD expected)."
    
    return "Response is OASIS-compliant."

if __name__ == "__main__":
    test_response = "Diagnosis: Hypertension. Symptoms: Fatigue. Medications: None."
    print(validate_oasis_response(test_response))