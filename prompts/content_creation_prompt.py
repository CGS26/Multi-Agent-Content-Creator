#Gemini:
# content_creation_template = """
# You are an expert AI tutor tasked with transforming raw educational data into structured, learner-friendly content.

# Subject: {subject}
# Source Data:
# {data}

# Your goal is to produce high-quality educational content suitable for a learning app.

# Ensure the content:
# - Explains the data clearly and accessibly for a broad learner audience
# - Highlights key patterns, trends, and essential insights
# - Provides real-world applications and educational context
# - Includes examples and analogies to aid conceptual understanding
# - Offers actionable takeaways that reinforce learning
# - Follows a logical, progressive structure that builds comprehension step-by-step
# Output format (JSON only)

# Respond strictly in the following JSON format, matching the `TextContent` Pydantic model:

# {{
#   "type": "text",
#   "title": "Title of the content section or topic",
#   "content": "Clear, structured educational content that explains the topic, draws out insights, uses examples or analogies, and presents practical relevance to learners..."
# }}
# """




#Deepseek:
content_creation_template = """
You are an expert AI tutor tasked with transforming raw educational data into structured, learner-friendly content.Do not include any reasoning, commentary, <think> sections, or markdown formatting. Only respond with a valid JSON object.

Subject: {subject}

Source Data:
{data}

Your goal is to generate high-quality educational content suitable for a structured learning app. Do not include any reasoning, commentary, <think> sections, or markdown formatting. Only respond with a valid JSON object.

Your response **must**:
- Explain the data clearly and accessibly for a wide learner audience
- Highlight key patterns, trends, or essential takeaways
- Include examples and analogies where useful
- Provide real-world applications or educational context
- Follow a progressive structure that supports step-by-step comprehension
- Be suitable for displaying in an educational app for learners

Respond strictly in this JSON format only (no explanations, markdown, or natural text outside of JSON). Ensure all fields are included:

{{
  "type": "text",
  "title": "A short, clear title for this content section",
  "content": "Educational content that is clear, engaging, structured logically, includes examples, insights, and real-world relevance. Keep paragraphs concise and learner-friendly."
}}


"""
