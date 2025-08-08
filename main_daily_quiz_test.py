# # from agents.DailyQuizGenerator import DailyQuizGenerator
# # from logger.config import logger
# # from dotenv import load_dotenv
# # import os

# # load_dotenv()
# # logger.info(
# #     f"Starting daily quiz generation system with ENV: {os.getenv('ENV', 'dev')}"
# # )

# # try:
# #     # Initialize the daily quiz generator
# #     orchestrator = DailyQuizGenerator()

# #     # Option 1: Process PDF and generate SQL (complete pipeline)
# #     logger.info("Starting complete PDF to daily quiz pipeline...")
# #     results = orchestrator.process_pdf_to_quiz(
# #         pdf_path="data/lesson1.pdf",
# #         quiz_type="daily-practice",
# #         max_chunks=2,  # Process first 2 chunks/sections for testing
# #     )
# #     print(results)

# #     # Save results to SQL file
# #     if results:
# #         sql_file = orchestrator.save_quizzes_to_sql(
# #             quizzes=results,
# #             output_file="output/generated_daily_quizzes.sql",
# #             subject_id=subject_id,  # Optional: can be set if you have a specific subject
# #         )
# #         if sql_file:
# #             logger.info(f"Daily quizzes saved to SQL file: {sql_file}")
# #         else:
# #             logger.error("Failed to save daily quizzes to SQL file")

# # except Exception as e:
# #     logger.exception(f"Error in daily quiz generation system: {e}")
# #     raise


# from agents.DailyQuizGenerator import DailyQuizGenerator
# from logger.config import logger
# from dotenv import load_dotenv
# import os

# load_dotenv()
# logger.info(f"Starting daily quiz generation system with ENV: {os.getenv('ENV', 'dev')}")

# # Config
# DATA_ROOT = "data"
# OUTPUT_ROOT = "output"
# QUIZ_TYPE = "daily-practice"

# try:
#     orchestrator = DailyQuizGenerator()
#     logger.info("🚀 Starting batch daily quiz pipeline...")

#     for subject_folder in os.listdir(DATA_ROOT):
#         subject_path = os.path.join(DATA_ROOT, subject_folder)
#         if not os.path.isdir(subject_path):
#             continue  # Skip non-folder files

#         subject_id = subject_folder
#         logger.info(f"📂 Processing subject folder: {subject_id}")

#         # Get all PDFs in this subject folder
#         pdf_files = [f for f in os.listdir(subject_path) if f.lower().endswith(".pdf")]
#         if not pdf_files:
#             logger.warning(f"⚠️ No PDFs found in folder: {subject_id}")
#             continue

#         all_subject_quizzes = []

#         for pdf_file in pdf_files:
#             pdf_path = os.path.join(subject_path, pdf_file)
#             logger.info(f"📄 Processing PDF: {pdf_path}")

#             results = orchestrator.process_pdf_to_quiz(
#                 pdf_path=pdf_path,
#                 quiz_type=QUIZ_TYPE,
#             )

#             if not results:
#                 logger.warning(f"⚠️ No quizzes generated from {pdf_file} in subject {subject_id}")
#                 continue

#             all_subject_quizzes.extend(results)

#         # After all PDFs are processed
#         if not all_subject_quizzes:
#             logger.warning(f"⚠️ No quizzes generated for subject {subject_id}")
#             continue

#         # Save combined quizzes to one SQL file per subject
#         sql_filename = f"{subject_id}_daily_quizzes.sql"
#         sql_output_path = os.path.join(OUTPUT_ROOT, sql_filename)

#         sql_file = orchestrator.save_quizzes_to_sql(
#             quizzes=all_subject_quizzes,
#             output_file=sql_output_path,
#             subject_id=subject_id,  
#         )

#         if sql_file:
#             logger.info(f"✅ Combined daily quiz SQL saved for subject {subject_id}: {sql_file}")
#         else:
#             logger.error(f"❌ Failed to save daily quizzes for subject {subject_id}")

# except Exception as e:
#     logger.exception(f"🔥 Fatal error in daily quiz generation system: {e}")
#     raise


from agents.DailyQuizGenerator import DailyQuizGenerator
from logger.config import logger
from dotenv import load_dotenv
import os

load_dotenv()
logger.info(f"Starting daily quiz generation system with ENV: {os.getenv('ENV', 'dev')}")

# Config
DATA_ROOT = "data"
OUTPUT_ROOT = "out/daily"
QUIZ_TYPE = "daily-practice"
# MAX_CHUNKS = 2  # Optional: limit processing to first 2 chunks per PDF

try:
    orchestrator = DailyQuizGenerator()
    logger.info("🚀 Starting batch daily quiz pipeline...")

    for class_folder in os.listdir(DATA_ROOT):
        class_path = os.path.join(DATA_ROOT, class_folder)
        if not os.path.isdir(class_path):
            continue

        class_id = class_folder
        logger.info(f"🏫 Processing class: {class_id}")

        for subject_folder in os.listdir(class_path):
            subject_path = os.path.join(class_path, subject_folder)
            if not os.path.isdir(subject_path):
                continue

            subject_id = subject_folder
            logger.info(f"📚 Processing subject: {subject_id} in class: {class_id}")

            # Get all PDFs in this subject folder
            pdf_files = [f for f in os.listdir(subject_path) if f.lower().endswith(".pdf")]
            if not pdf_files:
                logger.warning(f"⚠️ No PDFs found in {subject_id} of class {class_id}")
                continue

            all_quizzes = []

            for pdf_file in pdf_files:
                pdf_path = os.path.join(subject_path, pdf_file)
                logger.info(f"📄 Processing PDF: {pdf_path}")

                results = orchestrator.process_pdf_to_quiz(
                    pdf_path=pdf_path,
                    quiz_type=QUIZ_TYPE,
                )

                if not results:
                    logger.warning(f"⚠️ No quizzes generated from {pdf_file}")
                    continue

                all_quizzes.extend(results)

            if not all_quizzes:
                logger.warning(f"⚠️ No quizzes generated for {subject_id} in class {class_id}")
                continue

            # Save to SQL
            sql_filename = f"{class_id}_{subject_id}_daily_quizzes.sql"
            sql_output_path = os.path.join(OUTPUT_ROOT, sql_filename)

            sql_file = orchestrator.save_quizzes_to_sql(
                quizzes=all_quizzes,
                output_file=sql_output_path,
                subject_id=subject_id,
                class_id=class_id
            )

            if sql_file:
                logger.info(f"✅ Saved SQL for {class_id}/{subject_id} -> {sql_file}")
            else:
                logger.error(f"❌ Failed to save SQL for {class_id}/{subject_id}")

except Exception as e:
    logger.exception(f"🔥 Fatal error in daily quiz generation system: {e}")
    raise
