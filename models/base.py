from uuid import UUID
from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True