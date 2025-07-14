from logger.config import logger
from pathlib import Path
import fitz

class PDFLoader:
    def __init__(self,file_path:str):
        self.file_path=Path(file_path)
        self._validate()

    def _validate(self):
        if not self.file_path.exists():
            logger.error(f"Pdf not found in file Path : {self.file_path}")
            raise FileNotFoundError(f"File {self.file_path} does not exist")
        if self.file_path.suffix.lower() !='.pdf':
            logger.error(f"Invalid File Name: {self.file_path}")
            raise Exception("Only PDf's Are Allowed")       

    def extract_text(self)->str:
        logger.info(f"Extracting text form PDF {self.file_path}")
        with fitz.open(self.file_path) as doc:
            return chr(12).join([page.get_text() for page in doc])  #type: ignore[attr-defined]

    def get_metadata(self)->dict:
        with fitz.open(self.file_path) as doc:
            return {
                "source": str(self.file_path),
                "title": doc.metadata.get("title", ""),
                "page_count": doc.page_count,
                "file_size": self.file_path.stat().st_size
            }    

        




