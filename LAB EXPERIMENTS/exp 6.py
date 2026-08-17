# Prompt Strategy Design
# Zero-shot, One-shot and Few-shot Prompting

def zero_shot():
    prompt = """
Task:
Classify the sentiment of the following sentence.

Sentence:
"The movie was fantastic and I enjoyed every moment."

Answer:
"""
    return prompt


def one_shot():
    prompt = """
Example:

Sentence:
"I hate this product."

Answer:
Negative

Now classify:

Sentence:
"The movie was fantastic and I enjoyed every moment."

Answer:
"""
    return prompt


def few_shot():
    prompt = """
Example 1

Sentence:
"I love this phone."

Answer:
Positive

Example 2

Sentence:
"This service is terrible."

Answer:
Negative

Example 3

Sentence:
"The food is amazing."

Answer:
Positive

Now classify:

Sentence:
"The movie was fantastic and I enjoyed every moment."

Answer:
"""
    return prompt


print("========== ZERO-SHOT ==========")
print(zero_shot())

print("\n========== ONE-SHOT ==========")
print(one_shot())

print("\n========== FEW-SHOT ==========")
print(few_shot())