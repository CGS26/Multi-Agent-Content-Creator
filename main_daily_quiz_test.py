from agents.DailyQuizGenerator import DailyQuizGenerator
from logger.config import logger
from dotenv import load_dotenv
import os

load_dotenv()
logger.info(
    f"Starting daily quiz generation system with ENV: {os.getenv('ENV', 'dev')}"
)

try:
    # Initialize the daily quiz generator
    orchestrator = DailyQuizGenerator()

    # Option 1: Process PDF and generate SQL (complete pipeline)
    logger.info("Starting complete PDF to daily quiz pipeline...")
    results = orchestrator.process_pdf_to_quiz(
        pdf_path="data/lesson1.pdf",
        quiz_type="daily-practice",
        max_chunks=2,  # Process first 2 chunks/sections for testing
    )
    print(results)

    # Save results to SQL file
    if results:
        sql_file = orchestrator.save_quizzes_to_sql(
            quizzes=results,
            output_file="output/generated_daily_quizzes.sql",
            class_id=None,  # Optional: can be set if you have a specific class
            subject_id=None,  # Optional: can be set if you have a specific subject
        )
        if sql_file:
            logger.info(f"Daily quizzes saved to SQL file: {sql_file}")
        else:
            logger.error("Failed to save daily quizzes to SQL file")

except Exception as e:
    logger.exception(f"Error in daily quiz generation system: {e}")
    raise
