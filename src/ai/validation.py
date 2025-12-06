"""OASIS form validation and quality checking."""

import json
from typing import Dict, List, Any, Tuple
from anthropic import Anthropic

from src.models.oasis_schema import OASISFormData
from src.config.settings import ANTHROPIC_API_KEY, LLM_MODEL
from src.config.prompts import VALIDATION_PROMPT


class OASISValidator:
    """Validates OASIS form data for completeness and clinical consistency."""

    def __init__(self):
        """Initialize the validator."""
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

    def validate_structure(self, form_data: OASISFormData) -> Dict[str, Any]:
        """
        Validate the structural completeness of OASIS form.

        Args:
            form_data: OASISFormData object to validate

        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        completeness_score = 0
        total_fields = 0

        # Check demographics
        if form_data.demographics:
            total_fields += 3
            if form_data.demographics.patient_id:
                completeness_score += 1
            else:
                issues.append("Patient ID is required")
            if form_data.demographics.age:
                completeness_score += 1
            else:
                warnings.append("Patient age not documented")
            if form_data.demographics.gender:
                completeness_score += 1
            else:
                warnings.append("Patient gender not documented")

        # Check primary diagnosis
        if form_data.primary_diagnosis:
            total_fields += 2
            if form_data.primary_diagnosis.diagnosis_description:
                completeness_score += 1
            else:
                issues.append("Primary diagnosis is required")
            if form_data.primary_diagnosis.icd10_code:
                completeness_score += 1
            else:
                warnings.append("ICD-10 code not documented")

        # Check cognitive status
        if form_data.cognitive_status:
            total_fields += 2
            if form_data.cognitive_status.cognitive_functioning:
                completeness_score += 1
            else:
                warnings.append("Cognitive functioning (M1700) not assessed")
            if form_data.cognitive_status.confusion_frequency:
                completeness_score += 1
            else:
                warnings.append("Confusion frequency (M1710) not assessed")

        # Check ADL status
        if form_data.adl_status:
            adl_fields = ['grooming', 'bathing', 'toileting', 'transferring', 'ambulation']
            for field in adl_fields:
                total_fields += 1
                if getattr(form_data.adl_status, field):
                    completeness_score += 1
                else:
                    warnings.append(f"ADL - {field} not assessed")

        # Check safety assessment
        if form_data.safety_assessment:
            total_fields += 2
            if form_data.safety_assessment.fall_risk_level:
                completeness_score += 1
            else:
                warnings.append("Fall risk level not assessed")
            if form_data.safety_assessment.fall_history is not None:
                completeness_score += 1
            else:
                warnings.append("Fall history not documented")

        # Calculate completeness percentage
        completeness_pct = (completeness_score / total_fields * 100) if total_fields > 0 else 0

        return {
            "valid": len(issues) == 0,
            "completeness_score": completeness_pct,
            "fields_completed": completeness_score,
            "total_fields": total_fields,
            "issues": issues,
            "warnings": warnings
        }

    def validate_clinical_consistency(
        self,
        form_data: OASISFormData,
        context: str
    ) -> Dict[str, Any]:
        """
        Validate clinical consistency using AI review.

        Args:
            form_data: OASISFormData object
            context: Original patient context/documents

        Returns:
            Dictionary with AI validation results
        """
        if not self.client:
            return {
                "ai_validation_available": False,
                "message": "AI validation not available (ANTHROPIC_API_KEY not set)"
            }

        # Prepare prompt
        form_json = json.dumps(form_data.model_dump(), indent=2, default=str)
        prompt = VALIDATION_PROMPT.format(
            form_data=form_json,
            context=context[:3000]  # Limit context length
        )

        try:
            # Call Claude for validation
            message = self.client.messages.create(
                model=LLM_MODEL,
                max_tokens=2048,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            # Try to parse JSON response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                validation_result = json.loads(response_text[json_start:json_end].strip())
            else:
                validation_result = json.loads(response_text.strip())

            validation_result["ai_validation_available"] = True
            return validation_result

        except Exception as e:
            return {
                "ai_validation_available": False,
                "error": str(e),
                "message": "AI validation failed"
            }

    def generate_validation_report(
        self,
        form_data: OASISFormData,
        context: str = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.

        Args:
            form_data: OASISFormData object
            context: Optional patient context for clinical validation

        Returns:
            Complete validation report
        """
        report = {
            "validation_timestamp": form_data.assessment_date,
            "patient_id": form_data.demographics.patient_id if form_data.demographics else "Unknown"
        }

        # Structural validation
        structural = self.validate_structure(form_data)
        report["structural_validation"] = structural

        # AI validation if context provided
        if context and self.client:
            clinical = self.validate_clinical_consistency(form_data, context)
            report["clinical_validation"] = clinical
        else:
            report["clinical_validation"] = {
                "ai_validation_available": False,
                "message": "Clinical validation not performed"
            }

        # Overall assessment
        report["overall_valid"] = (
            structural["valid"] and
            structural["completeness_score"] >= 70.0
        )

        report["overall_score"] = structural["completeness_score"]

        return report


def validate_oasis_form(form_data: OASISFormData, context: str = None) -> Dict[str, Any]:
    """
    Convenience function to validate OASIS form.

    Args:
        form_data: OASISFormData object to validate
        context: Optional patient context for clinical validation

    Returns:
        Validation report
    """
    validator = OASISValidator()
    return validator.generate_validation_report(form_data, context)


if __name__ == "__main__":
    # Test validation
    from src.models.oasis_schema import (
        OASISFormData,
        PatientDemographics,
        PrimaryDiagnosis,
        CognitiveStatus
    )

    # Create test form data
    test_form = OASISFormData(
        demographics=PatientDemographics(
            patient_id="TEST-001",
            age=75,
            gender="Female"
        ),
        primary_diagnosis=PrimaryDiagnosis(
            diagnosis_description="Hypertension",
            icd10_code="I10"
        ),
        cognitive_status=CognitiveStatus(
            cognitive_functioning="1",
            confusion_frequency="0"
        )
    )

    validator = OASISValidator()
    report = validator.generate_validation_report(test_form)

    print("Validation Report:")
    print(json.dumps(report, indent=2, default=str))
