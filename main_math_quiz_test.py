# # from agents.MultiAgentOrchestrator import MultiAgentOrchestrator
# # from agents.MathQuizGenerator import MathQuizGenerator
# # from logger.config import logger
# # from dotenv import load_dotenv
# # import os

# # load_dotenv()
# # logger.info(
# #     f"Starting multi-agent SQL generation system with ENV: {os.getenv('ENV', 'dev')}"
# # )

# # try:
# #     orchestrator = MathQuizGenerator()  # MultiAgentOrchestrator()


# #     logger.info("Starting complete PDF to SQL pipeline...")
# #     results = orchestrator.process_pdf_to_quiz(
# #         pdf_path="data/lesson1.pdf",
# #         quiz_type="Mathematics",

# #     )
# #     print(results)

# #     # Save results to SQL file
# #     if results:
# #         sql_file = orchestrator.save_quizzes_to_sql(
# #             quizzes=results, output_file="output/generated_quizzes.sql"
# #         )
# #         if sql_file:
# #             logger.info(f"Quizzes saved to SQL file: {sql_file}")
# #         else:
# #             logger.error("Failed to save quizzes to SQL file")



# # except Exception as e:
# #     logger.exception(f"Error in multi-agent system: {e}")
# #     raise



# from agents.MultiAgentOrchestrator import MultiAgentOrchestrator
# from agents.MathQuizGenerator import MathQuizGenerator
# from logger.config import logger
# from dotenv import load_dotenv
# import os

# load_dotenv()
# logger.info(
#     f"Starting multi-agent SQL generation system with ENV: {os.getenv('ENV', 'dev')}"
# )

# try:
#     orchestrator = MathQuizGenerator()  # or MultiAgentOrchestrator()

#     # Set the base input and output directories
#     base_data_dir = "data"
#     output_dir = "out"
#     os.makedirs(output_dir, exist_ok=True)

#     # Loop through each class folder in the data directory
#     for class_folder in os.listdir(base_data_dir):
#         class_path = os.path.join(base_data_dir, class_folder)
#         print(class_path)
#         if os.path.isdir(class_path):  # Only process directories
#             class_id = class_folder
#             logger.info(f"Processing class: {class_id}")

#             all_quizzes = []

#             for file in os.listdir(class_path):
#                 if file.endswith(".pdf"):
#                     pdf_path = os.path.join(class_path, file)
#                     logger.info(f"Processing PDF: {pdf_path}")

#                     try:
#                         results = orchestrator.process_pdf_to_quiz(
#                             pdf_path=pdf_path,
#                             quiz_type="Mathematics",
#                             class_id=class_id
#                         )

#                         if results:
#                             all_quizzes.extend(results)
#                         else:
#                             logger.warning(f"No quiz generated for: {pdf_path}")

#                     except Exception as pdf_error:
#                         logger.exception(f"Failed to process {pdf_path}: {pdf_error}")

#             # Save all quizzes for this class_id
#             if all_quizzes:
#                 sql_file = orchestrator.save_quizzes_to_sql(
#                     quizzes=all_quizzes,
#                     output_file=os.path.join(output_dir, f"{class_id}_quizzes.sql"),
#                     class_id=class_id
#                 )
#                 if sql_file:
#                     logger.info(f"Saved quizzes to {sql_file}")
#                 else:
#                     logger.error(f"Failed to save SQL for class: {class_id}")

# except Exception as e:
#     logger.exception(f"Error in multi-agent system: {e}")
#     raise

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
    orchestrator = MathQuizGenerator()  # or MultiAgentOrchestrator()

    # Set the base input and output directories
    base_data_dir = "data"
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    # Loop through each class folder in the data directory
    for class_folder in os.listdir(base_data_dir):
        class_path = os.path.join(base_data_dir, class_folder)
        print(f"\n[INFO] Found folder: {class_path}")

        if os.path.isdir(class_path):
            class_id = class_folder
            print(f"[INFO] Processing class_id: {class_id}")
            logger.info(f"Processing class: {class_id}")

            all_quizzes = []

            for file in os.listdir(class_path):
                if file.endswith(".pdf"):
                    pdf_path = os.path.join(class_path, file)
                    print(f"[INFO] Processing PDF file: {pdf_path}")
                    logger.info(f"Processing PDF: {pdf_path}")

                    try:
                        results = orchestrator.process_pdf_to_quiz(
                            pdf_path=pdf_path,
                            quiz_type="Mathematics",
                        )

                        print(f"[DEBUG] Results from {file} => {results}")

                        if results:
                            all_quizzes.extend(results)
                        else:
                            print(f"[WARNING] No quizzes generated for: {file}")
                            logger.warning(f"No quiz generated for: {pdf_path}")

                    except Exception as pdf_error:
                        print(f"[ERROR] Failed to process {file}: {pdf_error}")
                        logger.exception(f"Failed to process {pdf_path}: {pdf_error}")

            print(f"[INFO] Total quizzes for class {class_id}: {len(all_quizzes)}")

            if all_quizzes:
                output_file_path = os.path.join(output_dir, f"{class_id}_quizzes.sql")
                print(f"[INFO] Saving SQL to: {output_file_path}")

                sql_file = orchestrator.save_quizzes_to_sql(
                    quizzes=all_quizzes,
                    output_file=output_file_path,
                    class_id=class_id
                )

                if sql_file:
                    print(f"[SUCCESS] Saved quizzes to SQL file: {sql_file}")
                    logger.info(f"Saved quizzes to {sql_file}")
                else:
                    print(f"[ERROR] Failed to save SQL file for class: {class_id}")
                    logger.error(f"Failed to save SQL for class: {class_id}")
            else:
                print(f"[INFO] No quizzes to save for class: {class_id}")

except Exception as e:
    print(f"[FATAL ERROR] {e}")
    logger.exception(f"Error in multi-agent system: {e}")
    raise
