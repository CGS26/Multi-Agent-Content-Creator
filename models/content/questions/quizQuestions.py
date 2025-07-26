from pydantic import BaseModel
from typing import List, Union, Optional
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    mcq = "mcq"
    multiSelect = "multiSelect"
    fillInBlank = "fillInBlank"


class Option(BaseModel):
    id: str
    text: str


class QuizQuestions(BaseModel):
    id: str
    hint: Optional[str]
    type: QuestionType
    options: Optional[List[Option]] = None
    question: str
    explanation: Optional[str]
    correctAnswer: Union[str, List[str]]
    # created_at: Optional[datetime]


class MixedQUestions(BaseModel):
    id: str
    type: QuestionType
    question: str
    options: Optional[List[Option]] = None
    correctAnswer: Union[str, List[str]]


class DailyQuestions(BaseModel):
    id: str
    hint: Optional[str] = None
    type: QuestionType
    options: Optional[List[Option]] = None
    question: str
    explanation: Optional[str] = None
    correctAnswer: Union[str, List[str]]

    class Config:
        extra = "ignore"  # Ignore extra fields that LLM might generate


class VocabQuestions(BaseModel):
    id: str
    hint: Optional[str] = None
    type: QuestionType
    options: Optional[List[Option]] = None
    question: str
    explanation: Optional[str] = None
    correctAnswer: Union[str, List[str]]

    class Config:
        extra = "ignore"  # Ignore extra fields that LLM might generate
