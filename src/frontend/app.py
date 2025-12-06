"""Streamlit web application for OASIS Form Automation prototype."""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.embeddings import embed_patient_documents, DocumentEmbedder
from src.ai.form_filler import OASISFormFiller
from src.config.settings import RAW_DATA_DIR, ANTHROPIC_API_KEY, OPENAI_API_KEY


def check_api_keys():
    """Check if required API keys are configured."""
    issues = []
    if not ANTHROPIC_API_KEY:
        issues.append("ANTHROPIC_API_KEY not set")
    if not OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY not set")
    return issues


def main():
    st.set_page_config(
        page_title="OASIS Form Automation",
        page_icon="<å",
        layout="wide"
    )

    st.title("<å OASIS Form Automation Prototype")
    st.markdown("*AI-Powered Home Healthcare Documentation*")

    # Check API keys
    api_issues = check_api_keys()
    if api_issues:
        st.error(f"  Configuration Issues: {', '.join(api_issues)}")
        st.info("Please set your API keys in a .env file:\n- ANTHROPIC_API_KEY\n- OPENAI_API_KEY")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("™ Configuration")

        mode = st.radio(
            "Select Mode:",
            ["Use Sample Data", "Upload Custom Files"],
            help="Start with sample data or upload your own patient documents"
        )

        st.divider()

        if mode == "Upload Custom Files":
            st.subheader("Upload Documents")
            patient_id = st.text_input("Patient ID", "PAT-CUSTOM-001")
            transcript_file = st.file_uploader("Patient Transcript", type=["txt"])
            history_file = st.file_uploader("Patient History", type=["txt"])
        else:
            patient_id = st.text_input("Patient ID", "PAT-2024-001", disabled=True)
            st.info("Using sample data for Margaret Thompson")

        assessment_date = st.date_input(
            "Assessment Date",
            value=datetime.now()
        )

    # Main content
    tab1, tab2, tab3 = st.tabs(["=Ë Generate Form", "=Ä View Documents", "9 About"])

    with tab1:
        st.header("Generate OASIS Form")

        col1, col2 = st.columns([2, 1])

        with col1:
            if mode == "Upload Custom Files":
                if not (transcript_file and history_file):
                    st.warning("Please upload both transcript and history files in the sidebar.")
                    st.stop()
            else:
                st.success(" Sample data loaded and ready")

        with col2:
            if st.button("=€ Generate OASIS Form", type="primary", use_container_width=True):
                generate_form(patient_id, assessment_date, mode, transcript_file if mode == "Upload Custom Files" else None, history_file if mode == "Upload Custom Files" else None)

    with tab2:
        st.header("View Patient Documents")
        display_documents(patient_id, mode)

    with tab3:
        st.header("About This Prototype")
        st.markdown("""
        ### Features
        - **NLP-Powered Extraction**: Uses Claude AI to extract clinical data from transcripts
        - **RAG Pipeline**: Vector database retrieval for context-aware form filling
        - **Structured Outputs**: Pydantic models ensure data validation
        - **Confidence Scoring**: AI provides confidence ratings for extracted data

        ### Architecture
        1. **Document Embedding**: Patient transcripts and history are chunked and embedded
        2. **Context Retrieval**: Relevant context is retrieved for each OASIS section
        3. **AI Extraction**: Claude processes context and fills OASIS fields
        4. **Validation**: Pydantic validates data structure and types

        ### Technology Stack
        - **AI**: Anthropic Claude (form filling), OpenAI (embeddings)
        - **Vector DB**: ChromaDB
        - **Framework**: LangChain
        - **Frontend**: Streamlit
        - **Validation**: Pydantic

        ### Sample Data
        The prototype includes realistic sample data for a 79-year-old patient with:
        - Osteoarthritis (primary diagnosis)
        - Hypertension and hyperlipidemia
        - Fall risk concerns
        - ADL limitations requiring assistance
        """)


def generate_form(patient_id, assessment_date, mode, transcript_file=None, history_file=None):
    """Generate OASIS form from patient data."""

    with st.spinner("= Processing patient data..."):
        try:
            # Step 1: Embed documents
            st.info("Step 1/3: Embedding patient documents...")

            if mode == "Use Sample Data":
                transcript_path = RAW_DATA_DIR / "sample_transcript.txt"
                history_path = RAW_DATA_DIR / "sample_patient_history.txt"

                if not (transcript_path.exists() and history_path.exists()):
                    st.error("Sample data files not found. Please check data/raw/ directory.")
                    return

                embedder = embed_patient_documents(
                    patient_id,
                    str(transcript_path),
                    str(history_path)
                )
            else:
                # Save uploaded files temporarily
                temp_dir = RAW_DATA_DIR / "temp"
                temp_dir.mkdir(exist_ok=True)

                transcript_path = temp_dir / f"{patient_id}_transcript.txt"
                history_path = temp_dir / f"{patient_id}_history.txt"

                transcript_path.write_text(transcript_file.read().decode())
                history_path.write_text(history_file.read().decode())

                embedder = embed_patient_documents(
                    patient_id,
                    str(transcript_path),
                    str(history_path)
                )

            st.success(" Documents embedded successfully")

            # Step 2: Generate form
            st.info("Step 2/3: Generating OASIS form with AI...")

            filler = OASISFormFiller()
            form_data, validation = filler.generate_with_validation(
                patient_id,
                assessment_date.strftime("%Y-%m-%d")
            )

            st.success(" OASIS form generated successfully")

            # Step 3: Display results
            st.info("Step 3/3: Validating and displaying results...")

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Confidence Score", f"{form_data.confidence_score:.1%}" if form_data.confidence_score else "N/A")
            with col2:
                st.metric("Fields Populated", validation["total_fields_populated"])
            with col3:
                missing_count = len(form_data.missing_fields or [])
                st.metric("Missing Fields", missing_count)
            with col4:
                st.metric("Assessment Date", assessment_date.strftime("%m/%d/%Y"))

            # Display form sections
            st.divider()
            st.subheader("=Ê OASIS Form Data")

            # Demographics
            with st.expander("=d Demographics", expanded=True):
                if form_data.demographics:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Patient ID:** {form_data.demographics.patient_id}")
                    with col2:
                        st.write(f"**Age:** {form_data.demographics.age or 'N/A'}")
                    with col3:
                        st.write(f"**Gender:** {form_data.demographics.gender or 'N/A'}")

            # Primary Diagnosis
            with st.expander("<å Primary Diagnosis"):
                if form_data.primary_diagnosis:
                    st.write(f"**Diagnosis:** {form_data.primary_diagnosis.diagnosis_description}")
                    st.write(f"**ICD-10 Code:** {form_data.primary_diagnosis.icd10_code or 'Not documented'}")
                    if form_data.primary_diagnosis.severity:
                        st.write(f"**Severity:** {form_data.primary_diagnosis.severity}")

            # Cognitive Status
            with st.expander(">à Cognitive Status"):
                if form_data.cognitive_status:
                    st.write(f"**Cognitive Functioning (M1700):** {form_data.cognitive_status.cognitive_functioning or 'N/A'}")
                    st.write(f"**Confusion Frequency (M1710):** {form_data.cognitive_status.confusion_frequency or 'N/A'}")
                    if form_data.cognitive_status.anxiety_level:
                        st.write(f"**Anxiety:** {form_data.cognitive_status.anxiety_level}")

            # ADL Status
            with st.expander("=¶ Activities of Daily Living (ADL)"):
                if form_data.adl_status:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Grooming:** {form_data.adl_status.grooming or 'N/A'}")
                        st.write(f"**Dressing Upper:** {form_data.adl_status.dressing_upper or 'N/A'}")
                        st.write(f"**Dressing Lower:** {form_data.adl_status.dressing_lower or 'N/A'}")
                        st.write(f"**Bathing:** {form_data.adl_status.bathing or 'N/A'}")
                    with col2:
                        st.write(f"**Toileting:** {form_data.adl_status.toileting or 'N/A'}")
                        st.write(f"**Transferring:** {form_data.adl_status.transferring or 'N/A'}")
                        st.write(f"**Ambulation:** {form_data.adl_status.ambulation or 'N/A'}")

            # Medications
            with st.expander("=Š Medications"):
                if form_data.medication_status:
                    st.write(f"**Total Medications:** {form_data.medication_status.total_medications or 'N/A'}")
                    if form_data.medication_status.high_risk_drugs:
                        st.write(f"**High Risk Drugs:** {', '.join(form_data.medication_status.high_risk_drugs)}")
                    if form_data.medication_status.medication_compliance:
                        st.write(f"**Compliance:** {form_data.medication_status.medication_compliance}")

            # Living Situation
            with st.expander("<à Living Situation"):
                if form_data.living_situation:
                    st.write(f"**Living Arrangement:** {form_data.living_situation.living_arrangement or 'N/A'}")
                    st.write(f"**Primary Caregiver:** {form_data.living_situation.primary_caregiver or 'N/A'}")
                    if form_data.living_situation.home_safety_concerns:
                        st.write(f"**Safety Concerns:** {', '.join(form_data.living_situation.home_safety_concerns)}")

            # Safety Assessment
            with st.expander("  Safety & Fall Risk"):
                if form_data.safety_assessment:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Fall Risk Level:** {form_data.safety_assessment.fall_risk_level or 'N/A'}")
                        st.write(f"**Fall History (90 days):** {'Yes' if form_data.safety_assessment.fall_history else 'No' if form_data.safety_assessment.fall_history is not None else 'N/A'}")
                    with col2:
                        if form_data.safety_assessment.assistive_devices:
                            st.write(f"**Assistive Devices:** {', '.join(form_data.safety_assessment.assistive_devices)}")

            # Clinical Notes
            if form_data.assessor_notes:
                with st.expander("=Ý Clinical Notes"):
                    st.write(form_data.assessor_notes)

            # Missing Fields Warning
            if form_data.missing_fields:
                st.warning(f"  Missing Fields: {', '.join(form_data.missing_fields)}")

            # Download JSON
            st.divider()
            json_data = json.dumps(form_data.model_dump(), indent=2, default=str)
            st.download_button(
                label="=å Download OASIS Form (JSON)",
                data=json_data,
                file_name=f"oasis_form_{patient_id}_{assessment_date.strftime('%Y%m%d')}.json",
                mime="application/json"
            )

        except Exception as e:
            st.error(f"L Error generating form: {str(e)}")
            st.exception(e)


def display_documents(patient_id, mode):
    """Display source documents."""
    if mode == "Use Sample Data":
        transcript_path = RAW_DATA_DIR / "sample_transcript.txt"
        history_path = RAW_DATA_DIR / "sample_patient_history.txt"

        if transcript_path.exists():
            with st.expander("=Ä Patient Visit Transcript", expanded=False):
                st.text(transcript_path.read_text())

        if history_path.exists():
            with st.expander("=Ë Patient Medical History", expanded=False):
                st.text(history_path.read_text())
    else:
        st.info("Upload files in the sidebar to view them here.")


if __name__ == "__main__":
    main()
