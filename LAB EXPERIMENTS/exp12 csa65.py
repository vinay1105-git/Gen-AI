# Q2: Zero-shot, One-shot and Few-shot Prompting
# 200-word Blog on Applications of Artificial Intelligence in Healthcare

print("=" * 70)
print("QUESTION 2: AI IN HEALTHCARE")
print("=" * 70)


# ZERO-SHOT PROMPT
print("\nZERO-SHOT PROMPT")
print("-" * 70)

zero_shot = """
Write a blog of exactly 200 words on the topic
"Applications of Artificial Intelligence in Healthcare".
Explain major applications, benefits, examples, and future scope
of Artificial Intelligence in healthcare. Use clear and professional
language suitable for students.
"""

print(zero_shot)


# ONE-SHOT PROMPT
print("\nONE-SHOT PROMPT")
print("-" * 70)

one_shot = """
Example:

Topic: Applications of AI in Education

Blog:
Artificial Intelligence is changing education through personalized
learning, intelligent tutoring systems, automated assessment, and
learning analytics. These technologies help teachers understand
student performance and provide learners with customized educational
experiences.

Task:
Using the same informative style, write exactly 200 words on
"Applications of Artificial Intelligence in Healthcare". Include
applications, benefits, examples, and future possibilities.
"""

print(one_shot)


# FEW-SHOT PROMPT
print("\nFEW-SHOT PROMPT")
print("-" * 70)

few_shot = """
Example 1:

Topic: AI in Banking
Focus: Fraud detection, customer service, risk analysis, automation,
and personalized financial services.

Example 2:

Topic: AI in Transportation
Focus: Traffic prediction, route optimization, autonomous vehicles,
safety, and intelligent transportation systems.

Task:
Following the focus and structure of the examples, write exactly
200 words on "Applications of Artificial Intelligence in Healthcare".
Discuss diagnosis, treatment, drug discovery, patient monitoring,
hospital management, benefits, and future scope.
"""

print(few_shot)


# GENERATED 200-WORD BLOG
print("\nGENERATED 200-WORD BLOG")
print("-" * 70)

blog = """
Artificial Intelligence (AI) is transforming healthcare by improving
the way diseases are diagnosed, treated, and managed. One important
application of AI is medical diagnosis. Machine learning systems can
analyze X-rays, CT scans, and MRI images to help doctors identify
abnormalities and diseases more quickly.

AI also supports personalized treatment. By analyzing patient records,
medical history, and test results, AI systems can help healthcare
professionals select suitable treatment options. Another major
application is drug discovery, where AI analyzes biological and
chemical information to identify promising medicines and reduce
research time.

Patient monitoring is another useful application. Smart devices and
AI systems can continuously monitor vital signs and alert healthcare
professionals when unusual changes occur. AI-powered chatbots can
also answer basic health questions, provide reminders, and assist
with appointment scheduling.

Hospitals can use AI for managing records, predicting patient demand,
optimizing resources, and improving administrative processes.

In the future, AI may enable more accurate diagnosis, remote
monitoring, robotic surgery, and personalized healthcare. However,
privacy, security, fairness, data quality, and ethical concerns must
be carefully addressed to ensure safe and responsible use of AI in
healthcare.
"""

print(blog)

# Word count
words = blog.split()
print("Word Count:", len(words))
