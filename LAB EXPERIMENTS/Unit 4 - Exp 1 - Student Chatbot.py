from transformers import pipeline

chatbot = pipeline("text-generation", model="distilgpt2")
query = input("Enter your college-related query: ")
prompt = f"Answer this engineering college student query clearly: {query}"
result = chatbot(prompt, max_new_tokens=80, do_sample=True)
print("\nChatbot:", result[0]["generated_text"])
