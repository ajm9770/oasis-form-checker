"""Simplified OASIS Form Schema using Pydantic models.

This is a prototype version covering key OASIS assessment areas:
- Demographics
- Primary Diagnosis
- Cognitive/Mental Status
- ADL/IADL Functioning
- Medications
- Living Situation
- Prior Medical History
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class CognitiveFunctioning(str, Enum):
    """M1700 - Cognitive Functioning"""
    ALERT_ORIENTED = "0"  # Alert/oriented, able to focus and shift attention
    MILD_IMPAIRMENT = "1"  # Requires prompting (cuing, repetition, reminders)
    MODERATE_IMPAIRMENT = "2"  # Requires assistance and some direction
    SEVERE_IMPAIRMENT = "3"  # Requires considerable assistance
    TOTALLY_DEPENDENT = "4"  # Totally dependent due to disturbances


class ConfusionFrequency(str, Enum):
    """M1710 - When Confused"""
    NEVER = "0"  # Never
    NEW_SITUATIONS = "1"  # In new or complex situations only
    AWAKENING = "2"  # On awakening or at night only
    DURING_DAY_EVENING = "3"  # During the day and evening, but not constantly
    CONSTANTLY = "4"  # Constantly


class ADLAssistance(str, Enum):
    """Activity of Daily Living Assistance Levels"""
    INDEPENDENT = "0"  # Able to perform activity without assistance
    SETUP_HELP = "1"  # With setup or clean-up assistance
    SUPERVISION = "2"  # Supervision or touching assistance
    PARTIAL_ASSISTANCE = "3"  # Partial/moderate assistance
    TOTAL_ASSISTANCE = "4"  # Total dependence
    ACTIVITY_NOT_OCCUR = "UK"  # Activity itself did not occur during assessment


class AmbulatoryStatus(str, Enum):
    """M1860 - Ambulation/Locomotion"""
    INDEPENDENT = "0"  # Able to independently walk on even/uneven surfaces
    MINIMAL_HELP = "1"  # Requires use of device (cane, walker)
    SUPERVISION = "2"  # Able to walk with supervision or assistance
    CHAIRFAST = "3"  # Chairfast, unable to ambulate
    BEDFAST = "4"  # Bedfast, unable to ambulate or be up in chair


class FallRisk(str, Enum):
    """Fall Risk Assessment"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class PatientDemographics(BaseModel):
    """Basic patient information"""
    patient_id: str = Field(description="Unique patient identifier")
    age: Optional[int] = Field(None, description="Patient age in years", ge=0, le=120)
    gender: Optional[str] = Field(None, description="Patient gender")


class PrimaryDiagnosis(BaseModel):
    """M1021/M1023 - Primary Diagnosis and ICD-10 Code"""
    diagnosis_description: str = Field(description="Primary diagnosis in plain language")
    icd10_code: Optional[str] = Field(None, description="ICD-10 code if mentioned")
    severity: Optional[str] = Field(None, description="Severity assessment if noted")


class CognitiveStatus(BaseModel):
    """M1700-M1745 - Cognitive, Behavioral, and Psychiatric Symptoms"""
    cognitive_functioning: Optional[CognitiveFunctioning] = Field(
        None, description="Overall cognitive functioning level"
    )
    confusion_frequency: Optional[ConfusionFrequency] = Field(
        None, description="Frequency of confusion"
    )
    anxiety_level: Optional[str] = Field(
        None, description="Anxiety level or behavioral concerns"
    )


class ADLStatus(BaseModel):
    """M1800-M1870 - Activities of Daily Living"""
    grooming: Optional[ADLAssistance] = Field(None, description="Ability to groom self")
    dressing_upper: Optional[ADLAssistance] = Field(None, description="Ability to dress upper body")
    dressing_lower: Optional[ADLAssistance] = Field(None, description="Ability to dress lower body")
    bathing: Optional[ADLAssistance] = Field(None, description="Ability to bathe self")
    toileting: Optional[ADLAssistance] = Field(None, description="Ability to use toilet")
    transferring: Optional[ADLAssistance] = Field(None, description="Ability to transfer (bed/chair)")
    ambulation: Optional[AmbulatoryStatus] = Field(None, description="Ambulation/locomotion status")


class MedicationStatus(BaseModel):
    """M2001-M2020 - Drug Regimen Review"""
    total_medications: Optional[int] = Field(None, description="Total number of medications", ge=0)
    high_risk_drugs: Optional[List[str]] = Field(
        default_factory=list, description="List of high-risk medications mentioned"
    )
    medication_compliance: Optional[str] = Field(
        None, description="Patient's ability to manage medications"
    )


class LivingSituation(BaseModel):
    """M1100 - Patient Living Situation"""
    living_arrangement: Optional[str] = Field(
        None, description="Who patient lives with (alone, family, caregiver, etc.)"
    )
    primary_caregiver: Optional[str] = Field(
        None, description="Primary caregiver if applicable"
    )
    home_safety_concerns: Optional[List[str]] = Field(
        default_factory=list, description="Home safety hazards or concerns"
    )


class SafetyAssessment(BaseModel):
    """Fall risk and safety assessment"""
    fall_risk_level: Optional[FallRisk] = Field(None, description="Overall fall risk assessment")
    fall_history: Optional[bool] = Field(None, description="History of falls in past 90 days")
    assistive_devices: Optional[List[str]] = Field(
        default_factory=list, description="Assistive devices used (walker, cane, etc.)"
    )


class OASISFormData(BaseModel):
    """Complete simplified OASIS assessment form"""
    demographics: PatientDemographics
    primary_diagnosis: Optional[PrimaryDiagnosis] = None
    cognitive_status: Optional[CognitiveStatus] = None
    adl_status: Optional[ADLStatus] = None
    medication_status: Optional[MedicationStatus] = None
    living_situation: Optional[LivingSituation] = None
    safety_assessment: Optional[SafetyAssessment] = None

    # Metadata
    assessment_date: Optional[str] = Field(None, description="Date of assessment (YYYY-MM-DD)")
    assessor_notes: Optional[str] = Field(None, description="Additional clinical notes")
    confidence_score: Optional[float] = Field(
        None, description="AI confidence in extracted data (0.0-1.0)", ge=0.0, le=1.0
    )
    missing_fields: Optional[List[str]] = Field(
        default_factory=list, description="Fields that could not be determined from transcript"
    )
