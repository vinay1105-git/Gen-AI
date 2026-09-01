from transformers import pipeline

generator = pipeline("text2text-generation", model="google/flan-t5-small")
topic = input("Enter a research topic: ")

prompt = f"""
For the research topic "{topic}", provide relevant keywords,
important areas to study, and a concise research summary.
"""

result = generator(prompt, max_new_tokens=180)
print("\nResearch Assistance:")
print(result[0]["generated_text"])
