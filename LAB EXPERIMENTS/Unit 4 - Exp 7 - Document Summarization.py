from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
filename = input("Enter text document filename: ")

with open(filename, "r", encoding="utf-8") as file:
    text = file.read()

summary = summarizer(text[:4000], max_length=150, min_length=40, do_sample=False)
print("\nSummary:")
print(summary[0]["summary_text"])
