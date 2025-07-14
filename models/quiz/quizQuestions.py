from pydantic import BaseModel
from typing import List, Union, Optional
from datetime import datetime
from enum import Enum

class QuestionType(str,Enum):
    mcq = "mcq"
    multiSelect = "multiSelect"
    fillInBlank = "fillInBlank"

class Option(BaseModel):
    id:str
    text: str
    
class QuizQuestion(BaseModel):
    id: str
    hint: Optional[str]
    type: QuestionType 
    options: Optional[List[Option]] = None
    question:str
    explanation: Optional[List[str]]
    correctAnswer : Union[str,List[str]]
    created_at: Optional[datetime] 

