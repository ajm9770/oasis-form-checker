"""Prompts for OASIS form extraction and generation."""

OASIS_EXTRACTION_PROMPT = """You are an expert home healthcare documentation specialist. Your task is to extract OASIS (Outcome and Assessment Information Set) form data from patient visit transcripts and medical history.

# Patient Context
{context}

# Task
Based on the patient context provided above, extract and structure all relevant OASIS assessment data into a JSON format. This assessment is for patient ID: {patient_id}, assessment date: {assessment_date}.

# OASIS Field Definitions

## Demographics
- patient_id: Patient identifier
- age: Patient age in years
- gender: Patient gender

## Primary Diagnosis (M1021/M1023)
- diagnosis_description: Primary diagnosis in plain language
- icd10_code: ICD-10 code if available
- severity: Severity assessment if noted

## Cognitive Status (M1700-M1745)
- cognitive_functioning: "0" (alert/oriented), "1" (requires prompting), "2" (requires assistance), "3" (considerable assistance), "4" (totally dependent)
- confusion_frequency: "0" (never), "1" (new situations only), "2" (awakening/night), "3" (day/evening not constant), "4" (constantly)
- anxiety_level: Description of anxiety or behavioral concerns

## ADL Status (M1800-M1870)
For each ADL (grooming, dressing_upper, dressing_lower, bathing, toileting, transferring):
- "0": Independent
- "1": Setup help only
- "2": Supervision or touching assistance
- "3": Partial/moderate assistance
- "4": Total dependence
- "UK": Activity did not occur

ambulation:
- "0": Independent walk on even/uneven surfaces
- "1": Requires device (cane, walker)
- "2": Requires supervision/assistance
- "3": Chairfast
- "4": Bedfast

## Medications (M2001-M2020)
- total_medications: Number of medications
- high_risk_drugs: List of high-risk medications
- medication_compliance: Patient's ability to manage meds

## Living Situation (M1100)
- living_arrangement: Who patient lives with
- primary_caregiver: Primary caregiver if applicable
- home_safety_concerns: List of safety hazards

## Safety Assessment
- fall_risk_level: "low", "moderate", or "high"
- fall_history: true/false - falls in past 90 days
- assistive_devices: List of devices used (walker, cane, etc.)

# Instructions
1. Carefully read through all the context provided
2. Extract information for each OASIS field
3. Use the exact enum values specified above
4. If information is not clearly stated, set the field to null
5. Track which fields could not be determined in missing_fields array
6. Provide a confidence_score (0.0-1.0) for the overall assessment
7. Add any important clinical notes to assessor_notes

# Output Format
Return ONLY a valid JSON object with this structure:

```json
{{
  "demographics": {{
    "patient_id": "{patient_id}",
    "age": <integer or null>,
    "gender": "<string or null>"
  }},
  "primary_diagnosis": {{
    "diagnosis_description": "<string>",
    "icd10_code": "<string or null>",
    "severity": "<string or null>"
  }},
  "cognitive_status": {{
    "cognitive_functioning": "<enum value or null>",
    "confusion_frequency": "<enum value or null>",
    "anxiety_level": "<string or null>"
  }},
  "adl_status": {{
    "grooming": "<enum value or null>",
    "dressing_upper": "<enum value or null>",
    "dressing_lower": "<enum value or null>",
    "bathing": "<enum value or null>",
    "toileting": "<enum value or null>",
    "transferring": "<enum value or null>",
    "ambulation": "<enum value or null>"
  }},
  "medication_status": {{
    "total_medications": <integer or null>,
    "high_risk_drugs": [<list of strings>],
    "medication_compliance": "<string or null>"
  }},
  "living_situation": {{
    "living_arrangement": "<string or null>",
    "primary_caregiver": "<string or null>",
    "home_safety_concerns": [<list of strings>]
  }},
  "safety_assessment": {{
    "fall_risk_level": "<low/moderate/high or null>",
    "fall_history": <boolean or null>,
    "assistive_devices": [<list of strings>]
  }},
  "assessment_date": "{assessment_date}",
  "assessor_notes": "<string with important clinical observations>",
  "confidence_score": <float 0.0-1.0>,
  "missing_fields": [<list of field names that could not be determined>]
}}
```

IMPORTANT: Return ONLY the JSON object, no additional text or explanation.
"""


VALIDATION_PROMPT = """You are a clinical documentation quality reviewer. Review the following OASIS form data for:

1. Clinical consistency
2. Completeness
3. Accuracy based on source documents
4. Any red flags or concerns

# OASIS Form Data
{form_data}

# Source Context
{context}

# Review Checklist
- Are cognitive scores consistent with described behavior?
- Do ADL scores match the functional descriptions in the transcript?
- Is fall risk assessment appropriate given history and mobility?
- Are medications documented completely?
- Are there any contradictions in the data?

Provide a structured review with:
1. Overall quality score (0-10)
2. List of potential issues or concerns
3. Recommendations for improvement
4. Missing critical information

Return your review as a JSON object.
"""
