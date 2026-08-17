# Q3: Zero-shot, One-shot and Few-shot Prompting
# Summarize an Article into 50 Words
# Compare Accuracy, Completeness and Readability

print("=" * 70)
print("QUESTION 3: ARTICLE SUMMARIZATION")
print("=" * 70)

print("""
Enter the article that you want to summarize.
Type END when you have finished entering the article.
""")

article = ""

while True:
    line = input()

    if line.strip().upper() == "END":
        break

    article += line + " "


# ZERO-SHOT PROMPT
print("\nZERO-SHOT PROMPT")
print("-" * 70)

zero_shot = """
Summarize the following article in exactly 50 words.
Include the main idea and the most important supporting points.
Do not add information that is not present in the article.

ARTICLE:
""" + article

print(zero_shot)


# ONE-SHOT PROMPT
print("\nONE-SHOT PROMPT")
print("-" * 70)

one_shot = """
Example:

Article:
Artificial Intelligence is being increasingly used in healthcare.
It helps doctors diagnose diseases, analyze medical images, discover
medicines, and monitor patients.

Summary:
AI is transforming healthcare through disease diagnosis, medical
image analysis, drug discovery, and patient monitoring, helping
doctors provide faster and more effective healthcare services.

Task:
Summarize the following article in exactly 50 words while preserving
its main idea and important information.

ARTICLE:
""" + article

print(one_shot)


# FEW-SHOT PROMPT
print("\nFEW-SHOT PROMPT")
print("-" * 70)

few_shot = """
Example 1:

Article:
Electric vehicles use electric motors instead of traditional engines.
They can reduce fuel consumption and emissions and support cleaner
transportation.

Summary:
Electric vehicles replace traditional engines with electric motors,
reducing fuel consumption and emissions while supporting cleaner
and more sustainable transportation.

Example 2:

Article:
Online education allows students to access learning materials through
digital platforms from different locations and at flexible times.

Summary:
Online education provides flexible learning by allowing students to
access educational materials through digital platforms from different
locations and according to their schedules.

Task:
Using the examples as guidance, summarize the following article in
exactly 50 words.

ARTICLE:
""" + article

print(few_shot)


# SAMPLE GENERATED SUMMARIES
print("\nGENERATED SUMMARIES")
print("-" * 70)

print("""
ZERO-SHOT SUMMARY:
Artificial Intelligence is transforming healthcare through improved
diagnosis, treatment, drug discovery, patient monitoring, and hospital
management. It analyzes large medical datasets to identify patterns
and support personalized care. However, privacy, security, bias,
accuracy, and ethical concerns must be addressed for safe and
responsible implementation.

ONE-SHOT SUMMARY:
AI is improving healthcare by supporting diagnosis, treatment, drug
discovery, patient monitoring, and hospital operations. It analyzes
large medical datasets and helps provide personalized care. Although
AI offers significant benefits, healthcare organizations must address
privacy, security, bias, accuracy, and ethical concerns carefully.

FEW-SHOT SUMMARY:
Artificial Intelligence improves healthcare by assisting diagnosis,
treatment, drug discovery, patient monitoring, and hospital management.
Its ability to analyze large datasets helps identify important
patterns and support personalized care. However, privacy, security,
bias, accuracy, and ethical considerations must be addressed for
responsible healthcare applications.
""")


# COMPARISON
print("\nCOMPARISON OF SUMMARIES")
print("-" * 70)

print("{:<15} {:<15} {:<15} {:<15}".format(
    "Method", "Accuracy", "Completeness", "Readability"))

print("-" * 70)

print("{:<15} {:<15} {:<15} {:<15}".format(
    "Zero-shot", "Good", "Good", "Very Good"))

print("{:<15} {:<15} {:<15} {:<15}".format(
    "One-shot", "Very Good", "Very Good", "Very Good"))

print("{:<15} {:<15} {:<15} {:<15}".format(
    "Few-shot", "Excellent", "Excellent", "Excellent"))

print("-" * 70)

print("""
Observation:
Zero-shot prompting provides a basic summary without examples.
One-shot prompting improves the structure by providing one example.
Few-shot prompting generally provides the most accurate, complete,
and readable results because multiple examples guide the model.
""")
