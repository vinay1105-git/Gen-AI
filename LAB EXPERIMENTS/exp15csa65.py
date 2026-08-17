# Q5: Zero-shot, One-shot and Few-shot Prompting
# Promotional Social Media Post for an AI Workshop

print("=" * 70)
print("QUESTION 5: AI WORKSHOP SOCIAL MEDIA POST")
print("=" * 70)


# ZERO-SHOT PROMPT
print("\nZERO-SHOT PROMPT")
print("-" * 70)

zero_shot = """
Create an attractive promotional social media post for an
Artificial Intelligence Workshop. Mention the workshop benefits,
topics covered, practical learning, target audience, and a clear
call to action. Use an engaging style suitable for students.
"""

print(zero_shot)


# ONE-SHOT PROMPT
print("\nONE-SHOT PROMPT")
print("-" * 70)

one_shot = """
Example:

Join our Python Workshop!

Learn Python through practical sessions, interactive activities,
and real-world examples. Improve your programming skills and gain
valuable hands-on experience.

Register now and start learning!

Task:
Using the same promotional style, create a social media post
for an Artificial Intelligence Workshop.
"""

print(one_shot)


# FEW-SHOT PROMPT
print("\nFEW-SHOT PROMPT")
print("-" * 70)

few_shot = """
Example 1:

Join our Data Science Workshop!
Learn data analysis, visualization, and machine learning through
hands-on activities. Build useful skills and explore real-world
applications. Register today!


Example 2:

Level up your coding skills!
Our Programming Workshop includes practical sessions, expert
guidance, and real-world projects. Don't miss this opportunity
to learn and grow!

Task:
Using the examples as guidance, create an engaging promotional
social media post for an Artificial Intelligence Workshop.
"""

print(few_shot)


# GENERATED SOCIAL MEDIA POST
print("\nGENERATED SOCIAL MEDIA POST")
print("-" * 70)

print("""
🤖 AI WORKSHOP 2026 🚀

Ready to explore the exciting world of Artificial Intelligence?

Join our AI Workshop and discover how AI is transforming the
future of technology!

✨ Topics Covered:
• Artificial Intelligence Fundamentals
• Machine Learning
• Generative AI
• Prompt Engineering
• Real-World AI Applications

🎯 What You'll Gain:
✔ Practical knowledge
✔ Hands-on learning
✔ Future-ready AI skills
✔ Understanding of real-world applications

👨‍🎓 Perfect for students, beginners, and AI enthusiasts!

📢 Don't miss this exciting opportunity!

Register Now and Start Your AI Journey! 🚀

#AIWorkshop #ArtificialIntelligence #MachineLearning
#GenerativeAI #PromptEngineering #Technology #Students
""")
