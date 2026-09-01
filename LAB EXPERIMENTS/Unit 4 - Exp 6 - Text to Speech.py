import pyttsx3

text = input("Enter engineering-related text: ")

engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.say(text)
engine.runAndWait()

print("Text converted to speech successfully.")
