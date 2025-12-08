#!/usr/bin/env python3
"""
End-to-end demonstration of OASIS Form Automation prototype.

This script demonstrates the complete workflow:
1. Embedding patient documents
2. Retrieving relevant context
3. Generating OASIS form with AI
4. Validating the results
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai.embeddings import embed_patient_documents
from src.ai.retrieval import ContextRetriever
from src.ai.form_filler import OASISFormFiller
from src.ai.validation import OASISValidator
from src.config.settings import RAW_DATA_DIR, ANTHROPIC_API_KEY


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def check_requirements():
    """Check if all requirements are met."""
    print_section("CHECKING REQUIREMENTS")

    issues = []

    # Check API key
    if not ANTHROPIC_API_KEY:
        issues.append("❌ ANTHROPIC_API_KEY not set")
    else:
        print("✓ ANTHROPIC_API_KEY configured")

    print("✓ Using local embeddings (no additional API key required)")

    # Check sample data
    transcript_path = RAW_DATA_DIR / "sample_transcript.txt"
    history_path = RAW_DATA_DIR / "sample_patient_history.txt"

    if not transcript_path.exists():
        issues.append(f"❌ Sample transcript not found: {transcript_path}")
    else:
        print(f"✓ Sample transcript found: {transcript_path}")

    if not history_path.exists():
        issues.append(f"❌ Sample history not found: {history_path}")
    else:
        print(f"✓ Sample patient history found: {history_path}")

    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print("\nPlease fix these issues before running the demo.")
        print("\nTo set your API key, create a .env file with:")
        print("  ANTHROPIC_API_KEY=your_key_here")
        return False

    print("\n✓ All requirements met!")
    return True


def run_demo():
    """Run the complete demonstration."""

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    patient_id = "PAT-2024-001"
    transcript_path = RAW_DATA_DIR / "sample_transcript.txt"
    history_path = RAW_DATA_DIR / "sample_patient_history.txt"

    # Step 1: Embed documents
    print_section("STEP 1: EMBEDDING PATIENT DOCUMENTS")
    print(f"Patient ID: {patient_id}")
    print(f"Transcript: {transcript_path.name}")
    print(f"History: {history_path.name}\n")

    try:
        embedder = embed_patient_documents(
            patient_id,
            str(transcript_path),
            str(history_path)
        )
        print("\n✓ Documents embedded successfully!")
    except Exception as e:
        print(f"\n❌ Error embedding documents: {e}")
        sys.exit(1)

    # Step 2: Retrieve context (demonstration)
    print_section("STEP 2: DEMONSTRATING CONTEXT RETRIEVAL")

    retriever = ContextRetriever()

    demo_queries = [
        "What is the patient's fall risk?",
        "What are the patient's cognitive limitations?",
        "What medications is the patient taking?"
    ]

    for query in demo_queries:
        print(f"\nQuery: {query}")
        docs = retriever.retrieve_for_query(query, patient_id=patient_id, k=2)
        print(f"Retrieved {len(docs)} relevant document chunks")

        if docs:
            print(f"Sample content: {docs[0].page_content[:150]}...")

    print("\n✓ Context retrieval working!")

    # Step 3: Generate OASIS form
    print_section("STEP 3: GENERATING OASIS FORM WITH AI")

    print("Calling Claude AI to extract OASIS data...")
    print("(This may take 10-30 seconds)\n")

    try:
        filler = OASISFormFiller()
        form_data, validation_info = filler.generate_with_validation(patient_id)

        print("✓ OASIS form generated successfully!\n")

        # Display summary
        print("GENERATION SUMMARY:")
        print(f"  Patient ID: {validation_info['patient_id']}")
        print(f"  Assessment Date: {validation_info['assessment_date']}")
        print(f"  Confidence Score: {validation_info['confidence_score']:.1%}" if validation_info.get('confidence_score') else "  Confidence Score: N/A")
        print(f"  Fields Populated: {validation_info['total_fields_populated']}")

        if form_data.missing_fields:
            print(f"  Missing Fields: {len(form_data.missing_fields)}")

    except Exception as e:
        print(f"\n❌ Error generating form: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 4: Validate results
    print_section("STEP 4: VALIDATING RESULTS")

    try:
        validator = OASISValidator()
        validation_report = validator.generate_validation_report(form_data)

        print("VALIDATION RESULTS:")
        structural = validation_report["structural_validation"]
        print(f"  Overall Valid: {'✓ YES' if validation_report['overall_valid'] else '❌ NO'}")
        print(f"  Completeness: {structural['completeness_score']:.1f}%")
        print(f"  Fields Completed: {structural['fields_completed']}/{structural['total_fields']}")

        if structural['issues']:
            print(f"\n  Issues:")
            for issue in structural['issues']:
                print(f"    - {issue}")

        if structural['warnings']:
            print(f"\n  Warnings:")
            for warning in structural['warnings'][:5]:  # Show first 5
                print(f"    - {warning}")
            if len(structural['warnings']) > 5:
                print(f"    ... and {len(structural['warnings']) - 5} more")

        print("\n✓ Validation complete!")

    except Exception as e:
        print(f"\n❌ Error during validation: {e}")

    # Step 5: Display sample results
    print_section("STEP 5: SAMPLE OASIS FORM DATA")

    print("DEMOGRAPHICS:")
    if form_data.demographics:
        print(f"  Patient ID: {form_data.demographics.patient_id}")
        print(f"  Age: {form_data.demographics.age}")
        print(f"  Gender: {form_data.demographics.gender}")

    print("\nPRIMARY DIAGNOSIS:")
    if form_data.primary_diagnosis:
        print(f"  Diagnosis: {form_data.primary_diagnosis.diagnosis_description}")
        print(f"  ICD-10: {form_data.primary_diagnosis.icd10_code or 'Not documented'}")

    print("\nCOGNITIVE STATUS:")
    if form_data.cognitive_status:
        print(f"  Cognitive Functioning (M1700): {form_data.cognitive_status.cognitive_functioning}")
        print(f"  Confusion Frequency (M1710): {form_data.cognitive_status.confusion_frequency}")

    print("\nADL STATUS:")
    if form_data.adl_status:
        print(f"  Bathing: {form_data.adl_status.bathing}")
        print(f"  Dressing Upper: {form_data.adl_status.dressing_upper}")
        print(f"  Ambulation: {form_data.adl_status.ambulation}")

    print("\nSAFETY ASSESSMENT:")
    if form_data.safety_assessment:
        print(f"  Fall Risk: {form_data.safety_assessment.fall_risk_level}")
        print(f"  Fall History (90 days): {form_data.safety_assessment.fall_history}")
        if form_data.safety_assessment.assistive_devices:
            print(f"  Assistive Devices: {', '.join(form_data.safety_assessment.assistive_devices)}")

    # Step 6: Save results
    print_section("STEP 6: SAVING RESULTS")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Save form data
    form_file = output_dir / f"oasis_form_{patient_id}.json"
    with open(form_file, 'w') as f:
        json.dump(form_data.model_dump(), f, indent=2, default=str)
    print(f"✓ OASIS form saved: {form_file}")

    # Save validation report
    validation_file = output_dir / f"validation_report_{patient_id}.json"
    with open(validation_file, 'w') as f:
        json.dump(validation_report, f, indent=2, default=str)
    print(f"✓ Validation report saved: {validation_file}")

    # Final summary
    print_section("DEMO COMPLETE!")

    print("✓ Successfully demonstrated:")
    print("  1. Document embedding with ChromaDB")
    print("  2. Context retrieval with vector search")
    print("  3. OASIS form generation with Claude AI")
    print("  4. Structured data validation")
    print("  5. Results export to JSON\n")

    print("Next steps:")
    print("  - Review the generated files in the output/ directory")
    print("  - Run the Streamlit app: streamlit run src/frontend/app.py")
    print("  - Experiment with custom patient data\n")

    print("For questions or issues:")
    print("  - Check README.md for detailed documentation")
    print("  - Review the code in src/ directory")
    print("  - Ensure API keys are correctly configured\n")


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
