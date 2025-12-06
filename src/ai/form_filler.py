"""OASIS Form Filler using Claude with structured outputs."""

import json
from typing import Optional, Dict, Any
from datetime import datetime
from anthropic import Anthropic

from src.models.oasis_schema import OASISFormData, PatientDemographics
from src.ai.retrieval import ContextRetriever
from src.config.settings import ANTHROPIC_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from src.config.prompts import OASIS_EXTRACTION_PROMPT


class OASISFormFiller:
    """Fills OASIS forms using Claude AI with structured outputs."""

    def __init__(self, model: str = LLM_MODEL):
        """Initialize the form filler with Claude client."""
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = model
        self.retriever = ContextRetriever()

    def generate_form(
        self,
        patient_id: str,
        assessment_date: Optional[str] = None
    ) -> OASISFormData:
        """
        Generate complete OASIS form from patient documents.

        Args:
            patient_id: Patient identifier
            assessment_date: Date of assessment (defaults to today)

        Returns:
            Completed OASISFormData object
        """
        # Retrieve context
        print(f"Retrieving context for patient {patient_id}...")
        context = self.retriever.get_full_patient_context(patient_id)

        if assessment_date is None:
            assessment_date = datetime.now().strftime("%Y-%m-%d")

        # Prepare the prompt
        prompt = OASIS_EXTRACTION_PROMPT.format(
            context=context,
            assessment_date=assessment_date,
            patient_id=patient_id
        )

        # Call Claude with structured output
        print("Generating OASIS form with Claude...")
        response = self._call_claude_structured(prompt)

        # Parse response into Pydantic model
        form_data = self._parse_response(response, patient_id, assessment_date)

        return form_data

    def _call_claude_structured(self, prompt: str) -> Dict[str, Any]:
        """
        Call Claude API with structured JSON output request.

        Args:
            prompt: The prompt to send to Claude

        Returns:
            Parsed JSON response
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=LLM_TEMPERATURE,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract text content
        response_text = message.content[0].text

        # Parse JSON from response
        try:
            # Try to find JSON in the response
            if "```json" in response_text:
                # Extract JSON from markdown code block
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                # Assume the entire response is JSON
                json_str = response_text.strip()

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response text: {response_text[:500]}...")
            raise

    def _parse_response(
        self,
        response_data: Dict[str, Any],
        patient_id: str,
        assessment_date: str
    ) -> OASISFormData:
        """
        Parse Claude's response into OASISFormData model.

        Args:
            response_data: Raw JSON response from Claude
            patient_id: Patient identifier
            assessment_date: Assessment date

        Returns:
            Validated OASISFormData object
        """
        # Ensure patient_id is in demographics
        if "demographics" not in response_data:
            response_data["demographics"] = {}

        response_data["demographics"]["patient_id"] = patient_id
        response_data["assessment_date"] = assessment_date

        # Validate and parse with Pydantic
        try:
            form_data = OASISFormData(**response_data)
            return form_data
        except Exception as e:
            print(f"Error validating OASIS form data: {e}")
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            raise

    def generate_with_validation(
        self,
        patient_id: str,
        assessment_date: Optional[str] = None
    ) -> tuple[OASISFormData, Dict[str, Any]]:
        """
        Generate form and return both form data and validation metadata.

        Args:
            patient_id: Patient identifier
            assessment_date: Date of assessment

        Returns:
            Tuple of (form_data, validation_info)
        """
        form_data = self.generate_form(patient_id, assessment_date)

        # Generate validation info
        validation_info = {
            "patient_id": patient_id,
            "assessment_date": form_data.assessment_date,
            "confidence_score": form_data.confidence_score,
            "missing_fields": form_data.missing_fields or [],
            "total_fields_populated": self._count_populated_fields(form_data),
            "generated_at": datetime.now().isoformat()
        }

        return form_data, validation_info

    def _count_populated_fields(self, form_data: OASISFormData) -> int:
        """Count how many fields were successfully populated."""
        count = 0

        # Convert to dict and recursively count non-None values
        def count_non_none(obj):
            if obj is None:
                return 0
            if isinstance(obj, dict):
                return sum(count_non_none(v) for v in obj.values())
            if isinstance(obj, list):
                return len(obj) if obj else 0
            return 1

        data_dict = form_data.model_dump(exclude_none=True)
        return count_non_none(data_dict)


def fill_oasis_form(patient_id: str) -> OASISFormData:
    """
    Convenience function to fill OASIS form for a patient.

    Args:
        patient_id: Patient identifier

    Returns:
        Completed OASISFormData object
    """
    filler = OASISFormFiller()
    return filler.generate_form(patient_id)


if __name__ == "__main__":
    # Test the form filler
    patient_id = "PAT-2024-001"

    print("=" * 80)
    print("OASIS Form Filler Test")
    print("=" * 80)

    filler = OASISFormFiller()
    form_data, validation = filler.generate_with_validation(patient_id)

    print("\n✓ OASIS form generated successfully!")
    print("\nValidation Info:")
    print(json.dumps(validation, indent=2))

    print("\nGenerated Form Data:")
    print(json.dumps(form_data.model_dump(), indent=2, default=str))
