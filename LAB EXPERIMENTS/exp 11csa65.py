# Q1: Zero-shot, One-shot and Few-shot Prompting
# Product Description for a Smart Fitness Watch

print("=" * 70)
print("QUESTION 1: SMART FITNESS WATCH")
print("=" * 70)

# ZERO-SHOT PROMPT
print("\nZERO-SHOT PROMPT")
print("-" * 70)

zero_shot = """
Generate a professional product description for a Smart Fitness Watch.
Include its design, fitness tracking features, health monitoring,
battery life, smart features, and benefits to customers.
"""

print(zero_shot)

print("OUTPUT:")
print("""
Smart Fitness Watch

Stay active, healthy, and connected with our Smart Fitness Watch.
It features advanced fitness tracking, heart-rate monitoring, sleep
tracking, step counting, calorie monitoring, and workout tracking.
Its stylish and lightweight design makes it comfortable for everyday
use. With long battery life and smart notifications for calls and
messages, it is an ideal companion for fitness enthusiasts and
health-conscious users. Track your daily activities, monitor your
health, and achieve your fitness goals with ease.
""")


# ONE-SHOT PROMPT
print("\nONE-SHOT PROMPT")
print("-" * 70)

one_shot = """
Example:

Product: Smart Water Bottle
Description: A smart water bottle that monitors water consumption,
provides drinking reminders, and helps users maintain healthy
hydration habits.

Task:
Using the same style, generate a professional product description
for a Smart Fitness Watch. Include its features, health monitoring,
fitness tracking, battery life, and benefits.
"""

print(one_shot)

print("OUTPUT:")
print("""
Smart Fitness Watch

A smart and stylish fitness watch designed to help users monitor
their health and improve their daily fitness. It tracks steps,
calories, heart rate, sleep, workouts, and physical activity.
The watch provides useful notifications and reminders while its
long-lasting battery supports everyday use. Its lightweight design
makes it suitable for exercise, work, and outdoor activities.
""")


# FEW-SHOT PROMPT
print("\nFEW-SHOT PROMPT")
print("-" * 70)

few_shot = """
Example 1:

Product: Smart Water Bottle
Description: A smart bottle that tracks water intake, sends reminders,
and helps users maintain proper hydration throughout the day.

Example 2:

Product: Fitness Band
Description: A lightweight fitness band that monitors steps, calories,
heart rate, sleep, and workouts while providing daily activity insights.

Task:
Using the examples as guidance, generate a professional product
description for a Smart Fitness Watch.
"""

print(few_shot)

print("OUTPUT:")
print("""
Smart Fitness Watch

Experience smarter fitness with a modern Smart Fitness Watch that
combines health monitoring, workout tracking, and smart connectivity.
It monitors heart rate, steps, calories, sleep, and daily activities.
Users can track workouts and receive useful reminders and notifications.
Its comfortable design and long-lasting battery make it suitable
for everyday fitness and lifestyle needs. Whether exercising,
working, or relaxing, this watch helps users understand their health
and achieve their fitness goals.
""")
