from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.schema import Document
from langchain.output_parsers import PydanticOutputParser
from langchain.output_parsers import OutputFixingParser
import json
import re
from pathlib import Path

from models.quiz import MixedQuiz
from logger.config import logger
import uuid
from datetime import datetime

PROMPT_PATH = Path("prompts/SystemPrompts/mixed_test.txt")


class MixedQuizGenerator:
    def __init__(self, model_name="llama3.1:8b", temperature=0):
        self.llm = ChatOllama(model_name=model_name, temperature=temperature)
        self.system_message = SystemMessage(PROMPT_PATH.read_text())
        self.parser = PydanticOutputParser(pydantic_object=MixedQuiz)
        self.system_prompt = SystemMessagePromptTemplate.from_template(
            PROMPT_PATH.read_text()
        )

    def generate(self, quizType: str, chunk: Document):
        logger.info(f"Generating Quiz for {quizType} for chun: {chunk}")
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
