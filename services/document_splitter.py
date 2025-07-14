import tiktoken
from typing import List, Optional
from logger.config import logger
from langchain.schema import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentSplitter:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.default_separators = [
            "\n\n",  # Paragraphs
            "\n",  # Lines
            " ",  # Words
            "",  # Characters
        ]
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=separators or self.default_separators,  # Added this line

        )
        logger.info(
            f"DocumentSplitter initialized with chunk_size={chunk_size}, overlap={chunk_overlap}"
        )

    def split(
        self, raw_text: str, source_metadata: Optional[dict] = None
    ) -> list[Document]:
        logger.info(
            f"Splitting text of length {len(raw_text)} characters into Documents"
        )
        
        documents = self.text_splitter.create_documents([raw_text], metadatas=[source_metadata or {}])
        return documents

    def split_text(
        self, raw_text: str, source_metadata: Optional[dict] = None
    ) -> list[str]:
        logger.info(f"Splitting text of length {len(raw_text)} characters")
        return self.text_splitter.split_text(raw_text)
