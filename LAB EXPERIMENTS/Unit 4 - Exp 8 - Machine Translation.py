from transformers import pipeline

translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi")
text = input("Enter engineering text in English: ")

result = translator(text, max_length=200)
print("\nHindi Translation:")
print(result[0]["translation_text"])
