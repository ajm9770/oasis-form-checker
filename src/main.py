from datetime import datetime
from core.ingestion.file_manager import FileManager
from core.vector_db.chroma_client import VectorDBManager
from services.oasis_form_filler import OASISFormFiller

class OASISAutomationPipeline:
    def __init__(self):
        self.file_manager = FileManager()
        self.vector_db = VectorDBManager()
        self.form_filler = OASISFormFiller()
    
    def process_patient(self, patient_id: str, transcript: str, history: str):
        # 1. Store raw files
        transcript_meta = self.file_manager.store_patient_file(
            patient_id, transcript, "transcript"
        )
        history_meta = self.file_manager.store_patient_file(
            patient_id, history, "history"
        )
        
        # 2. Process and vectorize documents
        processed_data = self._process_documents(
            patient_id,
            [transcript, history],
            [transcript_meta, history_meta]
        )
        
        # 3. Generate OASIS form
        form_results = self.form_filler.generate_form(
            patient_id=patient_id,
            context=processed_data['context_chunks'],
            current_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        return form_results
    
    def _process_documents(self, patient_id: str, texts: List[str], metadata: List[Dict]):
        # Document processing and embedding logic
        pass