from pydantic import BaseModel


class TextContent(BaseModel):
    type:str
    content:str
    title:str
