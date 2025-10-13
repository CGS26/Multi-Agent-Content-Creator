import csv
import uuid
from models.quiz import VocabQuiz
from models.content.questions.quizQuestions import VocabQuestions, Option, QuestionType
from logger.config import logger
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

def generate_vocab_quiz_from_csv(csv_path: str, output_file: str = "antonym_vocab_quiz.sql", class_id: str = None, questions_per_quiz: int = 10):
    """
    Generate vocabulary quizzes from CSV file containing antonym questions.
    Each quiz will have a maximum of questions_per_quiz questions.
    """
    all_questions = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create the question text
            question_text = f"What is the antonym for {row['Question']}?"

            # Create options list
            options = []
            option_letters = ['A', 'B', 'C', 'D', 'E']
            for i, letter in enumerate(option_letters):
                option_key = f'Option {i+1}'
                if option_key in row:
                    options.append(Option(id=letter, text=row[option_key]))

            # Find the correct answer ID
            correct_answer_text = row['Answer']
            correct_answer_id = None
            for opt in options:
                if opt.text == correct_answer_text:
                    correct_answer_id = opt.id
                    break

            if correct_answer_id is None:
                logger.warning(f"Correct answer '{correct_answer_text}' not found in options for question: {question_text}")
                continue

            # Create VocabQuestions object
            vocab_question = VocabQuestions(
                id=str(uuid.uuid4()),
                type=QuestionType.mcq,
                question=question_text,
                options=options,
                correctAnswer=correct_answer_id,
                hint=None,
                explanation=None
            )

            all_questions.append(vocab_question)

    if not all_questions:
        logger.error("No questions generated from CSV")
        return None

    # Split questions into chunks of questions_per_quiz
    quizzes = []
    for i in range(0, len(all_questions), questions_per_quiz):
        chunk = all_questions[i:i + questions_per_quiz]
        quiz = VocabQuiz(
            title=f"Antonym Vocabulary Practice - Part {len(quizzes) + 1}",
            description="Practice antonyms with multiple choice questions",
            questions=chunk
        )
        quizzes.append(quiz)

    # Save to SQL directly without using VocabQuizGenerator (to avoid OpenAI dependency)
    try:
        sql_statements = []
        class_id_value = f"'{class_id}'" if class_id else "NULL"

        for quiz in quizzes:
            # Escape single quotes in strings
            title = quiz.title.replace("'", "''")
            description = (
                quiz.description.replace("'", "''") if quiz.description else ""
            )

            # Convert questions to JSON format
            questions_json = []
            for question in quiz.questions:
                question_dict = {
                    "id": question.id,
                    "type": question.type.value,
                    "question": question.question,
                    "hint": question.hint,
                    "explanation": question.explanation,
                    "correctAnswer": question.correctAnswer,
                }

                if question.options:
                    question_dict["options"] = [
                        {"id": opt.id, "text": opt.text} for opt in question.options
                    ]

                questions_json.append(question_dict)

            # Convert to JSON string and escape for SQL
            questions_json_str = json.dumps(questions_json).replace("'", "''")

            # Create INSERT statement
            sql_statement = f"""INSERT INTO vocab_practice_quizzes (title, description, questions, class_id, created_at)
VALUES ('{title}', '{description}', '{questions_json_str}', {class_id_value}, NOW());"""

            sql_statements.append(sql_statement)

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("-- Generated Vocabulary Practice Quiz INSERT statements\n")
            f.write(f"-- Generated on: {datetime.now().isoformat()}\n")
            f.write(f"-- Total quizzes: {len(quizzes)}\n")
            f.write(f"-- Questions per quiz: {questions_per_quiz}\n\n")

            for statement in sql_statements:
                f.write(statement + "\n\n")

        logger.info(f"Successfully saved {len(quizzes)} vocab quizzes to {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Error saving quizzes to SQL: {e}")
        return None

if __name__ == "__main__":
    csv_file = "100-antonyms-generated - 300-anto-cgpt.csv"
    output_sql = "antonym_vocab_quiz1.sql"
    # class
    class_id = "6c4db2d7-7ad4-4c87-90f6-b65b28b57a56"  # Optional: set CLASS_ID in .env file
    try:
        result = generate_vocab_quiz_from_csv(csv_file, output_sql,class_id)
        if result:
            print(f"Quiz generated successfully: {result}")
        else:
            print("Failed to generate quiz")
    except Exception as e:
        logger.exception(f"Error generating vocab quiz: {e}")
        print(f"Error: {e}")