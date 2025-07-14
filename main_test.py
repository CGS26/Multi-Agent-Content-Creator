from agents.MathQuizGenerator import MathQuizGenerator
from langchain.schema import Document

# Instantiate the quiz generator
quiz_gen = MathQuizGenerator()

# Create a mock Document with some sample content
sample_content = "Mathematics is the study of numbers, shapes, and patterns."
doc = Document(page_content=sample_content, metadata={"source": "mock"})

# Call the generate method and print the output
result = quiz_gen.generate("mcq", doc)
print(result)








