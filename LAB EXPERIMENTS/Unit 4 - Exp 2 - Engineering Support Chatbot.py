from transformers import pipeline

qa = pipeline("text2text-generation", model="google/flan-t5-small")
question = input("Enter an engineering technical question: ")
prompt = f"Provide a simple engineering solution for: {question}"
result = qa(prompt, max_new_tokens=100)
print("\nSolution:", result[0]["generated_text"])
