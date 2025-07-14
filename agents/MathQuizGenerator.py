from langchain.schema.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
import json
import re
from pathlib import Path
from langchain.schema import Document


from models.quiz import Quiz
from logger.config import logger

PROMPT_PATH = Path("./prompts/SystemPrompts/math.txt")


class MathQuizGenerator:
    def __init__(self, model_name="deepseek-r1", temperature=0):
        self.llm = ChatOllama(model=model_name, temperature=temperature)
        self.system_message = SystemMessage(PROMPT_PATH.read_text())

        logger.info(
            f"Maths Quiz Generator Initialized with Model: {model_name} and Temperature: {temperature} "
        )

    def generate(self, quizType: str, chunk: Document):
        logger.info(f"Generating Quiz for {quizType} for chunk: {chunk}")
        try:
            messages = [
                self.system_message,
                HumanMessage(
                    content=f"""Using the following context, generate a {quizType} quiz:

\"\"\"
{chunk.page_content}
\"\"\"

Ensure the questions are relevant to the context and follow the format defined in the system instructions."""
                ),
            ]

            llm_response = self.llm.invoke(messages)
            return llm_response  

        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return None 
