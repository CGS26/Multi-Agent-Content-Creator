from agents.MixedQuizGenerator import MixedQuizGenerator
from logger.config import logger
from dotenv import load_dotenv
import os

load_dotenv()
logger.info(
    f"Starting mixed quiz generation system with ENV: {os.getenv('ENV', 'dev')}"
)

try:
    # Initialize the mixed quiz generator
    orchestrator = MixedQuizGenerator()

    # Option 1: Process PDF and generate SQL (complete pipeline)
    logger.info("Starting complete PDF to mixed quiz pipeline...")
    results = orchestrator.process_pdf_to_quiz(
        pdf_path="data/lesson1.pdf",
        quiz_type="mixed",
        max_chunks=2,  # Process first 2 chunks/sections for testing
    )
    print(results)

    # Save results to SQL file
    if results:
        sql_file = orchestrator.save_quizzes_to_sql(
            quizzes=results, output_file="output/generated_mixed_quizzes.sql"
        )
        if sql_file:
            logger.info(f"Mixed quizzes saved to SQL file: {sql_file}")
        else:
            logger.error("Failed to save mixed quizzes to SQL file")

except Exception as e:
    logger.exception(f"Error in mixed quiz generation system: {e}")
    raise
