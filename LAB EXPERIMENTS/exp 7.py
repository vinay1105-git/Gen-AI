# Functional Prompt Development

def summarization_prompt():
    return """
Summarize the following paragraph in 50 words.

Text:
Artificial Intelligence (AI) is transforming industries by automating tasks,
improving decision-making, and enhancing customer experiences.
AI technologies such as machine learning and deep learning are widely used
in healthcare, finance, education, and transportation.
"""


def email_prompt():
    return """
Write a professional email requesting one day leave from college due to illness.
"""


def content_prompt():
    return """
Write a 150-word article on the importance of Artificial Intelligence in Education.
"""


print("========== SUMMARIZATION PROMPT ==========")
print(summarization_prompt())

print("\n========== EMAIL CREATION PROMPT ==========")
print(email_prompt())

print("\n========== CONTENT GENERATION PROMPT ==========")
print(content_prompt())