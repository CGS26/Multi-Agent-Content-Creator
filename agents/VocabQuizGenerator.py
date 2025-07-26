from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.schema import Document
from langchain.output_parsers import PydanticOutputParser
from langchain.output_parsers import OutputFixingParser
import json
import re
from pathlib import Path

from models.quiz import VocabQuiz
from logger.config import logger
import uuid
from datetime import datetime

PROMPT_PATH = Path("prompts/SystemPrompts/vocab_practice.txt")


class VocabQuizGenerator:
    def __init__(self, model_name="llama3.1:8b", temperature=0):
        self.llm = ChatOllama(model=model_name, temperature=temperature)
        self.system_message = SystemMessage(PROMPT_PATH.read_text())
        self.parser = PydanticOutputParser(pydantic_object=VocabQuiz)
        self.system_prompt = SystemMessagePromptTemplate.from_template(
            PROMPT_PATH.read_text()
        )

    def generate(self, quizType: str, chunk: Document):
        logger.info(f"Generating Quiz for {quizType} for chunk: {chunk}")
        try:
            human_message = HumanMessage(
                content=f"""Using the following content, generate a {quizType} quiz:
            
\"\"\"
{chunk.page_content}   
\"\"\"
Ensure the questions are relevant to the context and follow the format defined in the system instructions.
        {self.parser.get_format_instructions()}"""
            )

            messages = [self.system_message, human_message]
            llm_response = self.llm.invoke(messages)
            print(llm_response)
            return llm_response

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None

    def process_pdf_to_quiz(
        self,
        pdf_path: str,
        quiz_type: str = "vocabulary-practice",
        max_chunks: int | None = None,
        num_sections: int | None = None,
    ):
        """
        Complete pipeline: PDF → Text Extraction → Chunking → Quiz Generation
        Args:
            pdf_path: Path to the PDF file
            quiz_type: Type of quiz to generate for each chunk
            max_chunks: Maximum number of chunks to process (optional)
            num_sections: Number of sections to split the PDF into (optional)
        Returns:
            Dict[str, Any]: Results containing quizzes and metadata
        """
        from services.pdf_loader import PDFLoader
        from services.document_splitter import DocumentSplitter

        try:
            pdf = PDFLoader(pdf_path)
            raw_text = pdf.extract_text()
            metadata = pdf.get_metadata()

            # Split PDF into sections
            if num_sections is not None and num_sections > 0:
                length = len(raw_text)
                avg = length // num_sections
                section_texts = [
                    raw_text[i * avg : (i + 1) * avg] for i in range(num_sections - 1)
                ]
                section_texts.append(raw_text[(num_sections - 1) * avg :])
                documents = [
                    Document(page_content=section, metadata=metadata)
                    for section in section_texts
                ]
            else:
                splitter = DocumentSplitter(chunk_size=1000, chunk_overlap=100)
                documents = splitter.split(raw_text, metadata)

            if max_chunks:
                logger.info(f"Limiting to {max_chunks} chunks")
                documents = documents[:max_chunks]

            quizzes = []
            for i, doc in enumerate(documents):
                logger.info(f"Generating quiz for chunk/section {i+1}/{len(documents)}")
                quiz = self.generate(quiz_type, doc)
                quizzes.append(self.parser.parse(quiz.content))

            return quizzes
        except Exception as e:
            logger.error(f"Error in quiz generation pipeline: {e}")
            return None

    def save_quizzes_to_sql(
        self,
        quizzes: list[VocabQuiz],
        output_file: str = "vocab_quiz_inserts.sql",
        class_id: str = None,
    ):
        """
        Save quiz results as SQL INSERT statements
        Args:
            quizzes: List of VocabQuiz objects to save
            output_file: Output SQL file path
            class_id: Optional class ID for the quizzes
        """
        try:
            sql_statements = []

            for quiz in quizzes:
                class_id_value = f"'{class_id}'" if class_id else "NULL"

                # Escape single quotes in strings
                title = quiz.title.replace("'", "''")
                description = (
                    quiz.description.replace("'", "''") if quiz.description else ""
                )

                # Convert questions to JSON format
                questions_json = []
                for question in quiz.questions:
                    question_dict = {
                        "id": question.id,
                        "type": question.type.value,
                        "question": question.question,
                        "hint": question.hint,
                        "explanation": question.explanation,
                        "correctAnswer": question.correctAnswer,
                    }

                    if question.options:
                        question_dict["options"] = [
                            {"id": opt.id, "text": opt.text} for opt in question.options
                        ]

                    questions_json.append(question_dict)

                # Convert to JSON string and escape for SQL
                questions_json_str = json.dumps(questions_json).replace("'", "''")

                # Create INSERT statement - let Supabase generate UUID automatically
                sql_statement = f"""INSERT INTO vocab_practice_quizzes (title, description, questions, class_id, created_at) 
VALUES ('{title}', '{description}', '{questions_json_str}', {class_id_value}, NOW());"""

                sql_statements.append(sql_statement)

            # Write to file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("-- Generated Vocabulary Practice Quiz INSERT statements\n")
                f.write(f"-- Generated on: {datetime.now().isoformat()}\n")
                f.write(f"-- Total quizzes: {len(quizzes)}\n\n")

                for statement in sql_statements:
                    f.write(statement + "\n\n")

            logger.info(f"Successfully saved {len(quizzes)} quizzes to {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error saving quizzes to SQL: {e}")
            return None
