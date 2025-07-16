from agents.MultiAgentOrchestrator import MultiAgentOrchestrator
from agents.MathQuizGenerator import MathQuizGenerator
from logger.config import logger
from dotenv import load_dotenv
import os

load_dotenv()
logger.info(
    f"Starting multi-agent SQL generation system with ENV: {os.getenv('ENV', 'dev')}"
)

try:
    # Initialize the multi-agent orchestrator
    orchestrator = MathQuizGenerator()  # MultiAgentOrchestrator()

    # Prompt user for number of sections
    # num_sections_input = input("Enter number of sections to split the PDF into (leave blank for default): ")
    # try:
    #     num_sections = int(num_sections_input) if num_sections_input.strip() else None
    #     if num_sections is not None and num_sections <= 0:
    #         num_sections = None
    # except ValueError:
    #     num_sections = None

    # Option 1: Process PDF and generate SQL (complete pipeline)
    logger.info("Starting complete PDF to SQL pipeline...")
    results = orchestrator.process_pdf_to_quiz(
        pdf_path="data/lesson1.pdf",
        # subject="Mathematics",
        quiz_type="Mathematics",
        # course_id=None,  # Will be auto-generated
        max_chunks=2,  # Process first 10 chunks/sections for testing
        # num_sections=num_sections
    )
    print(results)

    # Save results to SQL file
    if results:
        sql_file = orchestrator.save_quizzes_to_sql(
            quizzes=results, output_file="output/generated_quizzes.sql"
        )
        if sql_file:
            logger.info(f"Quizzes saved to SQL file: {sql_file}")
        else:
            logger.error("Failed to save quizzes to SQL file")

    # print(f"\n=== Pipeline Results ===")
    # print(f"PDF Path: {results['pdf_path']}")
    # print(f"Total sections processed: {results['total_sections']}")
    # print(f"Total quizzes generated: {results['total_quizzes']}")
    # print(f"Metadata: {results['metadata']}")
    # print(f"\nSample Quiz Output:")
    # for quiz_info in results['quizzes']:
    #     # print(f"Section {quiz_info['chunk_index']}:")
    #     # print(type(quiz_info))
    #     # print(quiz_info['quiz'])
    #     print(quiz_info['quiz'].content)
    # print("-" * 40)
    # print(type(quiz_info))

except Exception as e:
    logger.exception(f"Error in multi-agent system: {e}")
    raise
