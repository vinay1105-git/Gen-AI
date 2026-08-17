# Q4: Zero-shot, One-shot and Few-shot Prompting
# Professional Email Requesting Leave Due to Illness

print("=" * 70)
print("QUESTION 4: PROFESSIONAL SICK LEAVE EMAIL")
print("=" * 70)


# ZERO-SHOT PROMPT
print("\nZERO-SHOT PROMPT")
print("-" * 70)

zero_shot = """
Write a professional email requesting leave due to illness.
Include a suitable subject, polite greeting, reason for leave,
requested leave period, assurance about missed work, and a
professional closing.
"""

print(zero_shot)


# ONE-SHOT PROMPT
print("\nONE-SHOT PROMPT")
print("-" * 70)

one_shot = """
Example:

Subject: Leave Request

Dear Sir/Madam,

I am feeling unwell and would like to request leave for one day.
I will complete any missed work after returning.

Thank you for your consideration.

Yours sincerely,
Student

Task:
Using the same professional style, write an email requesting
leave due to illness.
"""

print(one_shot)


# FEW-SHOT PROMPT
print("\nFEW-SHOT PROMPT")
print("-" * 70)

few_shot = """
Example 1:

Subject: Sick Leave Request

Dear Sir/Madam,

I am suffering from fever and am unable to attend college today.
Kindly grant me leave for one day. I will complete the missed work
after returning.

Yours sincerely,
Student


Example 2:

Subject: Medical Leave Request

Dear Professor,

I am currently unwell and have been advised to take rest.
Therefore, I kindly request leave for two days. I will catch up
on all missed lessons after returning.

Regards,
Student

Task:
Using the examples as guidance, generate a professional email
requesting leave due to illness.
"""

print(few_shot)


# GENERATED EMAIL
print("\nGENERATED PROFESSIONAL EMAIL")
print("-" * 70)

print("""
Subject: Request for Sick Leave

Dear Sir/Madam,

I am writing to inform you that I am currently suffering from
illness and am unable to attend college. Therefore, I kindly
request you to grant me leave for one day so that I can take
proper rest and recover.

I will make sure to complete the missed academic work after
returning to college.

Thank you for your understanding and consideration.

Yours sincerely,
Student
""")


# COMPARISON
print("\nCOMPARISON OF GENERATED EMAILS")
print("-" * 70)

print("{:<15} {:<15} {:<15} {:<15}".format(
    "Method", "Tone", "Grammar", "Completeness"))

print("-" * 70)

print("{:<15} {:<15} {:<15} {:<15}".format(
    "Zero-shot", "Good", "Good", "Good"))

print("{:<15} {:<15} {:<15} {:<15}".format(
    "One-shot", "Very Good", "Very Good", "Very Good"))

print("{:<15} {:<15} {:<15} {:<15}".format(
    "Few-shot", "Excellent", "Excellent", "Excellent"))

print("-" * 70)

print("""
Observation:
Zero-shot prompting creates a basic professional email.
One-shot prompting improves the tone and formatting using one example.
Few-shot prompting provides the most consistent professional tone,
grammar, formatting, and completeness.
""")
