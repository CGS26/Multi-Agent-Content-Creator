from typing import List
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.schema import Document
from dotenv import load_dotenv
from logger.config import logger
from prompts.content_creation_prompt import content_creation_template
from models.content.text import TextContent  # Use TextContent directly instead of ContentUnion
from langchain_ollama.llms import OllamaLLM
from langchain_core.runnables import RunnableSequence
from langchain_ollama import ChatOllama
from langchain.schema.messages import SystemMessage, HumanMessage

import json

load_dotenv()


# def extract_json_from_code_block(text: str) -> str:
#     # Strip markdown-style triple backticks and optional `json` tags
#     if text.strip().startswith("```"):
#         return "\n".join([
#             line for line in text.strip().splitlines()
#             if not line.strip().startswith("```")
#         ]).strip()
#     return text.strip()


import re

def extract_json_from_code_block(text: str) -> str:
    """
    Extracts the first JSON object or array from the text, ignoring any <think>, markdown, or commentary.
    """
    # Remove <think> and </think> blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # Remove markdown backticks if present
    text = re.sub(r"```(?:json)?", "", text).strip()

    # Try to locate the first JSON object or array
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Fallback: return raw cleaned text (still likely to fail)
    return text.strip()



# class ContentGenerator:
#     def __init__(self):
#         self.llm = OllamaLLM(
#             # model="deepseek-r1",
#             model="gemma3n:e4b",
#             temperature=0,
#         )
#         self.prompt = PromptTemplate(
#             input_variables=["subject", "chunk"],
#             template=content_creation_template
#         )
#         self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        
    

    
#     def generate(self, subject: str, document: Document) -> List[ContentUnion]:
#         chunk_text = document.page_content
#         metadata = document.metadata
#         logger.info(f"Generating structured content for subject {subject} from Document {metadata}")


#         try:
#             response = self.chain.invoke({"subject":subject, "data":chunk_text})
#             logger.debug(f"LLM raw response: {response}")
#             raw_text = response.get("text", "").strip()
#             logger.debug(f"LLM raw raw_text: {raw_text}")
#             clean_text = extract_json_from_code_block(raw_text)
#             logger.debug(f"Cleaned raw_text: {clean_text[:300]}")
#             parsed = json.loads(clean_text)


#             if isinstance(parsed, dict) and "content" in parsed and parsed["content"].strip().startswith("["):
#                 inner_json = extract_json_from_code_block(parsed["content"])
#                 parsed = json.loads(inner_json)

#             if isinstance(parsed, list):
#                 return [ContentUnion(**item) for item in parsed if isinstance(item, dict)]

#             elif isinstance(parsed, dict):
#                 return [ContentUnion(**parsed)]

#         except (json.JSONDecodeError, ValueError, TypeError) as e:
#             logger.error(f"Parsing failed. Error: {e}")
#             return [ContentUnion(
#                 section_title="Unknown",
#                 type="text",
#                 title="error",
#                 content=clean_text
#             )]
#         # try:
#         #     response = self.chain.invoke({"subject":subject, "data":chunk_text})
#         #     logger.debug(f"LLM raw response: {response}")
#         #     raw_text = response.get("text", "").strip()
#         #     logger.debug(f"LLM raw raw_text: {raw_text}")

#         #     parsed = json.loads(raw_text)

#         #     # Case 1: Parsed is a list of content blocks
#         #     if isinstance(parsed, list):
#         #         # Return first for now — or extend to return list later
#         #         logger.debug(f"Parsed {len(parsed)} content blocks from LLM.")
#         #         # return ContentUnion(**parsed[0])
#         #         return [ContentUnion(**item) for item in parsed if isinstance(item, dict)]


#         #     # Case 2: Parsed is a single content block
#         #     elif isinstance(parsed, dict):
#         #         return [ContentUnion(**parsed)]        
#         #     # raw_text = response["text"]  
#         #     # logger.debug(f"LLM raw Raw Text: {raw_text}")
#         #     # parsed = json.loads(raw_text)
#         #     # return ContentUnion(**parsed)

#         # except json.JSONDecodeError as e:
#         #     logger.error(f"JSON parsing failed for document: {metadata}. Error: {e}")
#         #     return [ContentUnion(
#         #         section_title="Unknown",
#         #         type="text",
#         #         title='error',
#         #         content=raw_text.strip()
#         #     )]



class ContentGenerator:
    def __init__(self):
        self.llm = ChatOllama(  # for multi-message support
            model="deepseek-r1",  
            temperature=0,
        )

        self.system_message = SystemMessage(
            content="""You are an expert AI tutor transforming raw educational content into structured JSON suitable for a learning app.

Output must strictly follow this JSON format only (no markdown, no <think>, no explanations):

{
  "type": "text",
  "title": "Short title of the section",
  "content": "Concise, structured, educational content explaining the concept, using examples, analogies, and real-world relevance. Clear and progressive."
}
"""
        )

    def extract_json_from_code_block(self, text: str) -> str:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        text = re.sub(r"```(?:json)?", "", text).strip()
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()

    def generate(self, subject: str, document: Document) -> List[TextContent]:
        chunk_text = document.page_content
        metadata = document.metadata
        logger.info(f"Generating structured content for subject {subject} from Document {metadata}")

        try:
            messages = [
                self.system_message,
                HumanMessage(content=f"Subject: {subject}\n\nSource:\n{chunk_text}")
            ]

            response = self.llm.invoke(messages)
            logger.info(f"Response of mode {response}")
            
            if hasattr(response, 'content'):
                raw_text = str(response.content)
            elif isinstance(response, str):
                raw_text = response
            else:
                raw_text = str(response)
            
            raw_text = raw_text.strip()
            logger.debug(f"Raw response: {raw_text}")

            clean_text = self.extract_json_from_code_block(raw_text)
            parsed = json.loads(clean_text)

            if isinstance(parsed, dict):
                return [TextContent(**parsed)]
            elif isinstance(parsed, list):
                return [TextContent(**item) for item in parsed if isinstance(item, dict)]
            else:
                # Fallback return for unexpected parsed type
                return [TextContent(
                    type="text",
                    title="Unknown",
                    content=str(parsed)
                )]

        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            error_content = "Error occurred during content generation"
            if 'raw_text' in locals():
                error_content = str(raw_text)
            return [TextContent(
                type="text",
                title="error",
                content=error_content
            )]
