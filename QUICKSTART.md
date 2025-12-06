# OASIS Form Automation - Quick Start Guide

Welcome to the OASIS Form Automation prototype! This guide will help you get started quickly.

## What Is This?

This prototype demonstrates AI-powered automation for filling OASIS (Outcome and Assessment Information Set) forms used in home healthcare. It uses:

- **Claude AI** for intelligent form extraction
- **Vector Database (ChromaDB)** for context retrieval
- **RAG Pipeline** for context-aware responses
- **Streamlit** for web interface

## Prerequisites

1. **Python 3.9+** installed
2. **API Keys**:
   - Anthropic API key (for Claude)
   - OpenAI API key (for embeddings)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:

```
ANTHROPIC_API_KEY=sk-ant-...your-key-here
OPENAI_API_KEY=sk-...your-key-here
```

### 3. Verify Installation

Run the demo script to verify everything works:

```bash
python demo.py
```

Expected output:
- ✓ All requirements met
- Successfully embeds sample documents
- Generates OASIS form with AI
- Saves results to `output/` directory

## Usage Options

### Option 1: Command-Line Demo (Quickest)

```bash
python demo.py
```

This runs a complete end-to-end demonstration using sample patient data.

**What it does:**
1. Embeds sample patient transcript and history
2. Retrieves relevant context using vector search
3. Generates OASIS form using Claude
4. Validates and saves results

**Output:** JSON files in `output/` directory

---

### Option 2: Web Interface (Best for testing)

```bash
streamlit run src/frontend/app.py
```

Then open your browser to http://localhost:8501

**Features:**
- Interactive web UI
- Use sample data or upload custom files
- View generated forms in formatted layout
- Download results as JSON
- View source documents

---

### Option 3: Python API (For integration)

Use the prototype programmatically:

```python
from src.ai.embeddings import embed_patient_documents
from src.ai.form_filler import OASISFormFiller

# 1. Embed patient documents
patient_id = "PAT-001"
embed_patient_documents(
    patient_id,
    "path/to/transcript.txt",
    "path/to/history.txt"
)

# 2. Generate OASIS form
filler = OASISFormFiller()
form_data, validation = filler.generate_with_validation(patient_id)

# 3. Access structured data
print(f"Primary Diagnosis: {form_data.primary_diagnosis.diagnosis_description}")
print(f"Fall Risk: {form_data.safety_assessment.fall_risk_level}")
```

## Sample Data

The prototype includes realistic sample data in `data/raw/`:

- **sample_transcript.txt**: Complete patient visit transcript
  - Patient: Margaret Thompson, 79-year-old female
  - Primary diagnosis: Osteoarthritis
  - Includes cognitive assessment, ADL evaluation, fall risk

- **sample_patient_history.txt**: Comprehensive medical history
  - Previous OASIS assessments
  - Medication list
  - Hospitalization history
  - Specialist consultations

## Understanding the Output

### OASIS Form Structure

The generated form includes:

1. **Demographics** (patient_id, age, gender)
2. **Primary Diagnosis** (diagnosis, ICD-10 code)
3. **Cognitive Status** (M1700, M1710 scores)
4. **ADL Status** (bathing, dressing, ambulation, etc.)
5. **Medications** (count, high-risk drugs, compliance)
6. **Living Situation** (who they live with, caregiver)
7. **Safety Assessment** (fall risk, assistive devices)

### OASIS Score Values

**Cognitive Functioning (M1700):**
- `"0"` = Alert/oriented
- `"1"` = Requires prompting
- `"2"` = Requires assistance
- `"3"` = Considerable assistance needed
- `"4"` = Totally dependent

**ADL Assistance Levels:**
- `"0"` = Independent
- `"1"` = Setup help only
- `"2"` = Supervision
- `"3"` = Partial assistance
- `"4"` = Total dependence

**Ambulation (M1860):**
- `"0"` = Walks independently
- `"1"` = Uses device (walker/cane)
- `"2"` = Needs supervision
- `"3"` = Chairfast
- `"4"` = Bedfast

## Validation & Confidence Scoring

The system provides:

- **Confidence Score** (0.0-1.0): AI's confidence in extracted data
- **Completeness %**: Percentage of fields populated
- **Missing Fields**: List of fields not found in transcript
- **Structural Validation**: Checks required fields
- **Clinical Consistency**: AI reviews for logical consistency

## Troubleshooting

### "API Key not set" error

**Solution:** Make sure `.env` file exists and contains valid API keys.

```bash
# Check if .env exists
ls -la .env

# Verify format
cat .env
```

### "Sample data files not found"

**Solution:** Ensure you're in the project root directory.

```bash
# Check current directory
pwd

# Should see data/raw/ directory
ls data/raw/
```

### ChromaDB errors

**Solution:** Clear the vector database and re-embed:

```bash
# Remove existing database
rm -rf data/chroma_db/

# Re-run demo
python demo.py
```

### Import errors

**Solution:** Ensure all dependencies are installed:

```bash
pip install -r requirements.txt --upgrade
```

## Project Structure

```
oasis-form-checker/
├── src/
│   ├── ai/                    # AI/ML components
│   │   ├── embeddings.py      # Document embedding
│   │   ├── retrieval.py       # Context retrieval
│   │   ├── form_filler.py     # OASIS form generation
│   │   └── validation.py      # Form validation
│   ├── models/
│   │   └── oasis_schema.py    # Pydantic models
│   ├── config/
│   │   ├── settings.py        # Configuration
│   │   └── prompts.py         # AI prompts
│   └── frontend/
│       └── app.py             # Streamlit web app
├── data/
│   ├── raw/                   # Input data
│   └── chroma_db/             # Vector database
├── output/                    # Generated forms
├── demo.py                    # End-to-end demo
├── requirements.txt           # Dependencies
└── .env                       # API keys (create this)
```

## Next Steps

1. **Run the demo** to see it in action
2. **Try the web interface** for interactive testing
3. **Upload custom data** (patient transcripts)
4. **Review the code** in `src/` to understand the architecture
5. **Customize prompts** in `src/config/prompts.py` for your use case

## Production Considerations

This is a **prototype**. For production use, you'll need:

- [ ] HIPAA-compliant infrastructure
- [ ] Proper authentication and authorization
- [ ] EHR integration
- [ ] Audit logging
- [ ] Real-time transcription (Whisper API, etc.)
- [ ] Human-in-the-loop review workflow
- [ ] Production-grade database (PostgreSQL + pgvector)
- [ ] Monitoring and alerting
- [ ] Error handling and retry logic
- [ ] Rate limiting and cost controls

## Support

For issues or questions:

1. Check the main README.md
2. Review the code comments
3. Run demo.py to verify setup
4. Check API key configuration

## License

See LICENSE file for details.

---

**Ready to get started?** Run `python demo.py` to see the prototype in action!
