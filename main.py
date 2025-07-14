from agents.MultiAgentOrchestrator import MultiAgentOrchestrator
from logger.config import logger
from dotenv import load_dotenv
import os

load_dotenv()
logger.info(f"Starting multi-agent SQL generation system with ENV: {os.getenv('ENV', 'dev')}")

try:
    # Initialize the multi-agent orchestrator
    orchestrator = MultiAgentOrchestrator()
    
    # Prompt user for number of sections
    num_sections_input = input("Enter number of sections to split the PDF into (leave blank for default): ")
    try:
        num_sections = int(num_sections_input) if num_sections_input.strip() else None
        if num_sections is not None and num_sections <= 0:
            num_sections = None
    except ValueError:
        num_sections = None

    # Option 1: Process PDF and generate SQL (complete pipeline)
    logger.info("Starting complete PDF to SQL pipeline...")
    results = orchestrator.process_pdf_to_sql(
        pdf_path="data/lesson1.pdf",
        subject="Mathematics",
        course_id=None,  # Will be auto-generated
        max_chunks=10,   # Process first 10 chunks/sections for testing
        num_sections=num_sections
    )
    
    print(f"\n=== Pipeline Results ===")
    print(f"Subject: {results['subject']}")
    print(f"Total sections processed: {results['total_sections']}")
    print(f"Single lesson created with all sections: {results['total_lessons']}")
    print(f"SQL query generated: {results['total_sql_queries']}")
    print(f"Files created:")
    print(f"  - Structured sections: {results['structured_sections_file']}")
    print(f"  - Lessons data: {results['lessons_file']}")
    print(f"  - SQL queries: {results['sql_file']}")
    
    # Option 2: Generate SQL from existing data (alternative approach)
    # Uncomment the following lines if you want to process existing JSON data
    # logger.info("Generating SQL from existing structured data...")
    # existing_results = orchestrator.generate_sql_from_existing_data(
    #     json_file_path="output/structured_sections_maths.json",
    #     course_id=None
    # )
    # print(f"\n=== Existing Data Results ===")
    # print(f"SQL queries generated: {existing_results['total_sql_queries']}")
    # print(f"SQL file: {existing_results['sql_file']}")

except Exception as e:
    logger.exception(f"Error in multi-agent system: {e}")
    raise
