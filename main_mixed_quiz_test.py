# from agents.MixedQuizGenerator import MixedQuizGenerator
# from logger.config import logger
# from dotenv import load_dotenv
# import os

# load_dotenv()
# logger.info(
#     f"Starting mixed quiz generation system with ENV: {os.getenv('ENV', 'dev')}"
# )

# try:
#     # Initialize the mixed quiz generator
#     orchestrator = MixedQuizGenerator()

#     # Option 1: Process PDF and generate SQL (complete pipeline)
#     logger.info("Starting complete PDF to mixed quiz pipeline...")
#     results = orchestrator.process_pdf_to_quiz(
#         pdf_path="data/lesson1.pdf",
#         quiz_type="mixed",
#         max_chunks=2,  # Process first 2 chunks/sections for testing
#     )
#     print(results)

#     # Save results to SQL file
#     if results:
#         sql_file = orchestrator.save_quizzes_to_sql(
#             quizzes=results, output_file="output/generated_mixed_quizzes.sql"
#         )
#         if sql_file:
#             logger.info(f"Mixed quizzes saved to SQL file: {sql_file}")
#         else:
#             logger.error("Failed to save mixed quizzes to SQL file")

# except Exception as e:
#     logger.exception(f"Error in mixed quiz generation system: {e}")
#     raise




from agents.MixedQuizGenerator import MixedQuizGenerator
from logger.config import logger
from dotenv import load_dotenv
import os

load_dotenv()
logger.info(f"Starting mixed quiz generation system with ENV: {os.getenv('ENV', 'dev')}")

# Config
DATA_ROOT = "maindata/mixed"
OUTPUT_ROOT = "out/mixed"
QUIZ_TYPE = "mixed"
# MAX_CHUNKS = 2  # Optional: limit processing to first 2 chunks per PDF

try:
    orchestrator = MixedQuizGenerator()
    logger.info("🚀 Starting batch mixed quiz pipeline...")

    for class_folder in os.listdir(DATA_ROOT):
        class_path = os.path.join(DATA_ROOT, class_folder)
        if not os.path.isdir(class_path):
            continue  # Skip non-folders

        class_id = class_folder
        logger.info(f"📂 Processing class folder: {class_id}")

        # Get all PDF files in this class folder
        pdf_files = [f for f in os.listdir(class_path) if f.lower().endswith(".pdf")]
        if not pdf_files:
            logger.warning(f"⚠️ No PDFs found in folder: {class_id}")
            continue

        all_class_quizzes = []

        for pdf_file in pdf_files:
            pdf_path = os.path.join(class_path, pdf_file)
            logger.info(f"📄 Processing PDF: {pdf_path}")

            # Process PDF and generate quizzes
            results = orchestrator.process_pdf_to_quiz(
                pdf_path=pdf_path,
                quiz_type=QUIZ_TYPE,
                # max_chunks=MAX_CHUNKS,
            )

            if not results:
                logger.warning(f"⚠️ No quizzes generated from {pdf_file} in class {class_id}")
                continue

            all_class_quizzes.extend(results)

        # After all PDFs processed
        if not all_class_quizzes:
            logger.warning(f"⚠️ No quizzes generated for class {class_id}")
            continue

        # Save to one combined SQL file per class
        sql_filename = f"{class_id}_mixed_quizzes.sql"
        sql_output_path = os.path.join(OUTPUT_ROOT, sql_filename)

        sql_file = orchestrator.save_quizzes_to_sql(
            quizzes=all_class_quizzes,
            output_file=sql_output_path,
            class_id=class_id,
        )

        if sql_file:
            logger.info(f"✅ Combined mixed quiz SQL saved for class {class_id}: {sql_file}")
        else:
            logger.error(f"❌ Failed to save mixed quizzes for class {class_id}")

except Exception as e:
    logger.exception(f"🔥 Fatal error in mixed quiz generation system: {e}")
    raise
