# Install the library
# pip install google-generativeai

import google.generativeai as genai

# Replace with your Gemini API key
API_KEY = "YOUR_GEMINI_API_KEY"

# Configure the API
genai.configure(api_key=API_KEY)

# Load the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Generate content
response = model.generate_content(
    "Explain Artificial Intelligence in simple words."
)

# Display the response
print("AI Response:")
print(response.text)