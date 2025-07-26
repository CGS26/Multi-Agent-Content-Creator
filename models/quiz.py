from pydantic import BaseModel
from typing import List, Union, Optional
from uuid import UUID

# custom imports
from models.content.questions.quizQuestions import (
    QuizQuestions,
    MixedQUestions,
    DailyQuestions,
)

""" 
  id uuid not null default gen_random_uuid (),
  class_id uuid null,
  title text not null,
  description text null,
  questions jsonb not null,
  created_at timestamp with time zone null default now(),
  constraint mathquizes_pkey primary key (id),
  constraint mathquizes_class_id_fkey foreign KEY (class_id) references classes (id)
"""


class Quiz(BaseModel):
    # class_id: UUID
    title: str
    description: str
    questions: List[QuizQuestions]


class MixedQuiz(BaseModel):
    title: str
    description: str
    questions: List[MixedQUestions]

    class Config:
        extra = "ignore"  # Ignore extra fields that LLM might generate


class DailyQuiz(BaseModel):
    title: str
    description: str
    questions: List[DailyQuestions]

    class Config:
        extra = "ignore"  # Ignore extra fields that LLM might generate
