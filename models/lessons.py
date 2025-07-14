from typing import List
from uuid import  UUID
from pydantic import BaseModel
from models.content.base import ContentUnion



class lessons(BaseModel):
    course_id:UUID
    is_active:bool
    title:str
    sections:List[ContentUnion]
