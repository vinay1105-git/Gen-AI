import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak your engineering-related query...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    audio = recognizer.listen(source)

try:
    text = recognizer.recognize_google(audio)
    print("\nConverted Text:", text)
except sr.UnknownValueError:
    print("Could not understand the speech.")
except sr.RequestError:
    print("Speech recognition service is unavailable.")
