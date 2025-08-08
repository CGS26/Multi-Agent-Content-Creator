# from agents.VocabQuizGenerator import VocabQuizGenerator
# from logger.config import logger
# from dotenv import load_dotenv
# import os

# load_dotenv()
# logger.info(
#     f"Starting vocabulary quiz generation system with ENV: {os.getenv('ENV', 'dev')}"
# )

# try:
#     # Initialize the vocabulary quiz generator
#     orchestrator = VocabQuizGenerator()

#     # Option 1: Process PDF and generate SQL (complete pipeline)
#     logger.info("Starting complete PDF to vocabulary quiz pipeline...")
#     results = orchestrator.process_pdf_to_quiz(
#         pdf_path="data/2025_KS2_English_GPS_Paper1_questions.pdf", 
#         quiz_type="vocabulary-practice",
#     )
#     print(results)

#     # Save results to SQL file
#     if results:
#         sql_file = orchestrator.save_quizzes_to_sql(
#             quizzes=results,
#             output_file="output/generated_vocab_quizzes.sql",
#             class_id=None,  # Optional: can be set if you have a specific class
#         )
#         if sql_file:
#             logger.info(f"Vocabulary quizzes saved to SQL file: {sql_file}")
#         else:
#             logger.error("Failed to save vocabulary quizzes to SQL file")

# except Exception as e:
#     logger.exception(f"Error in vocabulary quiz generation system: {e}")
#     raise






from agents.VocabQuizGenerator import VocabQuizGenerator
from logger.config import logger
from dotenv import load_dotenv
import os

load_dotenv()
logger.info(f"Starting vocabulary quiz generation system with ENV: {os.getenv('ENV', 'dev')}")

# Config
DATA_ROOT = "data/vocab"
OUTPUT_ROOT = "output"
QUIZ_TYPE = "vocabulary-practice"

try:
    orchestrator = VocabQuizGenerator()
    logger.info("🚀 Starting batch vocabulary quiz pipeline...")

    for class_folder in os.listdir(DATA_ROOT):
        class_path = os.path.join(DATA_ROOT, class_folder)
        if not os.path.isdir(class_path):
            continue  # Skip if not a directory

        class_id = class_folder
        logger.info(f"📂 Processing class: {class_id}")

        pdf_files = [f for f in os.listdir(class_path) if f.lower().endswith(".pdf")]
        if not pdf_files:
            logger.warning(f"⚠️ No PDF files found in {class_id}")
            continue

        all_class_quizzes = []

        for pdf_file in pdf_files:
            pdf_path = os.path.join(class_path, pdf_file)
            logger.info(f"📄 Processing PDF: {pdf_path}")

            results = orchestrator.process_pdf_to_quiz(
                pdf_path=pdf_path,
                quiz_type=QUIZ_TYPE
            )

            if not results:
                logger.warning(f"⚠️ No quizzes generated from {pdf_file} in {class_id}")
                continue

            all_class_quizzes.extend(results)

        # After all PDFs processed
        if not all_class_quizzes:
            logger.warning(f"⚠️ No quizzes generated for class {class_id}")
            continue

        # Save single SQL file for the whole class
        sql_filename = f"{class_id}_vocab_quizzes.sql"
        sql_output_path = os.path.join(OUTPUT_ROOT, sql_filename)

        sql_file = orchestrator.save_quizzes_to_sql(
            quizzes=all_class_quizzes,
            output_file=sql_output_path,
            class_id=class_id,
        )

        if sql_file:
            logger.info(f"✅ Combined SQL file saved for class {class_id}: {sql_file}")
        else:
            logger.error(f"❌ Failed to save SQL for class {class_id}")

except Exception as e:
    logger.exception(f"🔥 Fatal error in quiz generation system: {e}")
    raise
