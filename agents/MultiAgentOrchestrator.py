from typing import List, Dict, Any
from agents.ContentGenerator import ContentGenerator
from agents.DataTransformer import DataTransformer
from agents.SQLGenerator import SQLGenerator
from logger.config import logger
import json
import os
import datetime


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents to generate SQL queries from PDF content
    """
    
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.data_transformer = DataTransformer()
        self.sql_generator = SQLGenerator()
        logger.info("MultiAgentOrchestrator initialized with all agents")
    
    def _split_text_into_n_sections(self, text: str, n: int) -> list:
        """
        Split text into n contiguous, non-overlapping sections by character count.
        """
        length = len(text)
        avg = length // n
        sections = [text[i*avg:(i+1)*avg] for i in range(n-1)]
        sections.append(text[(n-1)*avg:])  
        return sections

    def process_pdf_to_sql(self, pdf_path: str, subject: str = "Mathematics", 
                          course_id: str = "1243", max_chunks: int | None = None, num_sections: int | None = None) -> Dict[str, Any]:
        """
        Complete pipeline: PDF → Content Generation → Data Transformation → SQL Generation
        
        Args:
            pdf_path: Path to the PDF file
            subject: Subject name for content generation
            course_id: UUID string for course_id (optional)
            max_chunks: Maximum number of chunks to process (optional)
            num_sections: Number of sections to split the PDF into (optional)
        
        Returns:
            Dict[str, Any]: Results containing SQL queries and metadata
        """
        try:
            logger.info(f"Starting complete pipeline for PDF: {pdf_path}")
            
            from services.pdf_loader import PDFLoader
            from services.document_splitter import DocumentSplitter
            
            pdf = PDFLoader(pdf_path)
            raw_text = pdf.extract_text()
            metadata = pdf.get_metadata()

            # Step 2: Split PDF into sections
            if num_sections is not None and num_sections > 0:
                logger.info(f"Splitting PDF into {num_sections} sections by character count")
                section_texts = self._split_text_into_n_sections(raw_text, num_sections)
                documents = []
                for i, section_text in enumerate(section_texts):
                    # Wrap in a Document-like dict for compatibility
                    doc = {'page_content': section_text, 'metadata': metadata}
                    documents.append(doc)
                logger.info(f"PDF split into {len(documents)} sections")
            else:
                splitter = DocumentSplitter(chunk_size=1000, chunk_overlap=250)
                documents = splitter.split(raw_text, metadata)
                logger.info(f"PDF split into {len(documents)} chunks")
            
            if max_chunks:
                documents = documents[:max_chunks]
                logger.info(f"Processing first {len(documents)} chunks/sections")
            
            structured_sections = []
            for i, doc in enumerate(documents):
                logger.info(f"Processing chunk/section {i+1}/{len(documents)}")
                document_content = doc['page_content'] if isinstance(doc, dict) else doc
                structured = self.content_generator.generate(subject=subject, document=document_content)
                structured_sections.extend(structured)
            
            logger.info(f"Generated {len(structured_sections)} structured sections")
            
            lessons_list = self.data_transformer.transform_sections_to_lessons(
                structured_sections, course_id
            )
            
            valid_lessons = []
            for lesson in lessons_list:
                if self.data_transformer.validate_lesson_data(lesson):
                    valid_lessons.append(lesson)
                else:
                    logger.warning(f"Skipping invalid lesson: {lesson.title}")
            
            logger.info(f"Validated {len(valid_lessons)} lessons out of {len(lessons_list)}")
            
            sql_queries = self.sql_generator.generate_batch_insert_queries(valid_lessons)
            
            results = self._save_results(structured_sections, lessons_list, sql_queries, subject)
            
            logger.info("Complete pipeline finished successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in complete pipeline: {e}")
            raise
    
    def generate_sql_from_existing_data(self, json_file_path: str, course_id: str | None = None) -> Dict[str, Any]:
        """
        Generate SQL queries from existing structured data JSON file
        
        Args:
            json_file_path: Path to existing JSON file with structured sections
            course_id: UUID string for course_id (optional)
            
        Returns:
            Dict[str, Any]: Results containing SQL queries and metadata
        """
        try:
            logger.info(f"Generating SQL from existing data: {json_file_path}")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                structured_sections = json.load(f)
            
            logger.info(f"Loaded {len(structured_sections)} structured sections from {json_file_path}")
            
            lessons_list = self.data_transformer.transform_sections_to_lessons(
                structured_sections, course_id if course_id else "default_course"
            )
            
            valid_lessons = []
            for lesson in lessons_list:
                if self.data_transformer.validate_lesson_data(lesson):
                    valid_lessons.append(lesson)
                else:
                    logger.warning(f"Skipping invalid lesson: {lesson.title}")
            
            sql_queries = self.sql_generator.generate_batch_insert_queries(valid_lessons)
            
            
            subject = "Mathematics"  # Default, could be extracted from filename
            results = self._save_results(structured_sections, lessons_list, sql_queries, subject)
            
            logger.info("SQL generation from existing data completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error generating SQL from existing data: {e}")
            raise
    
    def process_folder_to_sql(self, folder_path: str, course_id: str, 
                             max_docs: int | None = None, subject: str = "Mathematics", 
                             max_chunks_per_doc: int | None = None, output_dir: str = "output") -> Dict[str, Any]:
        """
        Process all PDFs in a folder and generate a single SQL file
        
        Args:
            folder_path: Path to folder containing PDFs
            course_id: Course ID for all PDFs
            max_docs: Maximum number of PDFs to process
            subject: Subject name
            max_chunks_per_doc: Maximum chunks to process per PDF
            output_dir: Directory to save the combined SQL file
            
        Returns:
            Dict with file paths and summary
        """
        try:
            import glob
            from pathlib import Path
            
            folder_path_obj = Path(folder_path)
            if not folder_path_obj.exists():
                raise FileNotFoundError(f"Folder {folder_path} does not exist")
            
            pdf_files = list(folder_path_obj.glob("*.pdf"))
            if not pdf_files:
                raise ValueError(f"No PDF files found in {folder_path}")
            
            logger.info(f"Found {len(pdf_files)} PDF files in {folder_path}")
            
            if max_docs:
                pdf_files = pdf_files[:max_docs]
                logger.info(f"Processing first {len(pdf_files)} PDF files")
            
            all_sql_queries = []
            processed_files = []
            failed_files = []
            
            for i, pdf_file in enumerate(pdf_files, 1):
                try:
                    logger.info(f"Processing PDF {i}/{len(pdf_files)}: {pdf_file.name}")
                    
                    results = self.process_pdf_to_sql(
                        pdf_path=str(pdf_file),
                        subject=subject,
                        course_id=course_id,
                        max_chunks=max_chunks_per_doc,  
                        num_sections=None  
                    )
                    
                    sql_file_path = results.get('sql_file')
                    if sql_file_path and os.path.exists(sql_file_path):
                        with open(sql_file_path, 'r', encoding='utf-8') as f:
                            sql_content = f.read()
                            all_sql_queries.append(f"-- SQL for {pdf_file.name}")
                            all_sql_queries.append(sql_content)
                            all_sql_queries.append("")  
                    
                    processed_files.append(pdf_file.name)
                    logger.info(f"Successfully processed {pdf_file.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to process {pdf_file.name}: {e}")
                    failed_files.append(pdf_file.name)
            
            os.makedirs(output_dir, exist_ok=True)
            combined_sql_file = os.path.join(output_dir, f"combined_sql_queries_{subject.lower()}.sql")
            
            with open(combined_sql_file, 'w', encoding='utf-8') as f:
                f.write(f"-- Combined SQL queries for course_id: {course_id}\n")
                f.write(f"-- Subject: {subject}\n")
                f.write(f"-- Total PDFs processed: {len(processed_files)}\n")
                f.write(f"-- Generated on: {datetime.datetime.now()}\n\n")
                f.write('\n'.join(all_sql_queries))
            
            logger.info(f"Combined SQL file saved: {combined_sql_file}")
            
            # Return results
            results = {
                "combined_sql_file": combined_sql_file,
                "total_pdfs_processed": len(processed_files),
                "total_pdfs_failed": len(failed_files),
                "processed_files": processed_files,
                "failed_files": failed_files,
                "course_id": course_id,
                "subject": subject
            }
            
            logger.info(f"Folder processing completed. Processed: {len(processed_files)}, Failed: {len(failed_files)}")
            return results
            
        except Exception as e:
            logger.error(f"Error in folder processing: {e}")
            raise
    
    def _save_results(self, structured_sections: List, 
                     lessons_list: List, sql_queries: List[str], subject: str) -> Dict[str, Any]:
        """
        Save all results to files and return metadata
        
        Args:
            structured_sections: Original structured sections (ContentUnion objects)
            lessons_list: Transformed lesson objects
            sql_queries: Generated SQL queries
            subject: Subject name
            
        Returns:
            Dict[str, Any]: Results metadata
        """
        try:
            os.makedirs("output", exist_ok=True)
            
            sections_file = f"output/structured_sections_{subject.lower()}.json"
            sections_dict = [section.model_dump() for section in structured_sections]
            with open(sections_file, "w", encoding="utf-8") as f:
                json.dump(sections_dict, f, indent=2, ensure_ascii=False)
            
            lessons_file = f"output/lessons_{subject.lower()}.json"
            lessons_dict = [lesson.model_dump() for lesson in lessons_list]
            with open(lessons_file, "w", encoding="utf-8") as f:
                json.dump(lessons_dict, f, indent=2, ensure_ascii=False, default=str)
            
            sql_file = f"output/sql_queries_{subject.lower()}.sql"
            self.sql_generator.save_queries_to_file(sql_queries, f"sql_queries_{subject.lower()}.sql")
            
            results = {
                "structured_sections_file": sections_file,
                "lessons_file": lessons_file,
                "sql_file": sql_file,
                "total_sections": len(structured_sections),
                "total_lessons": len(lessons_list),
                "total_sql_queries": len(sql_queries),
                "subject": subject
            }
            
            logger.info(f"Results saved: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise 