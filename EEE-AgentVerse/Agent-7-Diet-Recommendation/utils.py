"""
utils.py - Utility functions for Diet Recommendation Agent
"""

import re
from datetime import datetime


def validate_fields(name, age, weight, height, condition, gender) -> list:
    errors = []
    if not name.strip():
        errors.append("Patient name is required.")
    if not (1 <= age <= 120):
        errors.append("Age must be between 1 and 120.")
    if not (20 <= weight <= 300):
        errors.append("Weight must be between 20 and 300 kg.")
    if not (50 <= height <= 250):
        errors.append("Height must be between 50 and 250 cm.")
    if not condition:
        errors.append("Please select a health condition.")
    if not gender:
        errors.append("Please select gender.")
    return errors


def generate_report_text(data: dict) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plan = data["plan"]
    meal_lines = "\n".join(f"  {k:15}: {v}" for k, v in plan["meal_plan"].items())
    eat_lines = "\n".join(f"  ✓ {f}" for f in plan["foods_to_eat"])
    avoid_lines = "\n".join(f"  ✗ {f}" for f in plan["foods_to_avoid"])

    return f"""
{'='*55}
       ELDERCARE AI – DIET RECOMMENDATION REPORT
{'='*55}
Generated     : {now}
{'─'*55}
Patient Name  : {data['name']}
Age           : {data['age']} years
Gender        : {data['gender']}
Weight        : {data['weight']} kg
Height        : {data['height']} cm
BMI           : {data['bmi']} ({data['bmi_category']})
Condition     : {data['condition']}
{'─'*55}
Diet Plan     : {plan['description']}
{'─'*55}
MEAL PLAN:
{meal_lines}
{'─'*55}
FOODS TO EAT:
{eat_lines}
{'─'*55}
FOODS TO AVOID:
{avoid_lines}
{'─'*55}
Water Intake  : {plan['water_intake']}
💡 Tip        : {plan['tip']}
{'='*55}
      ElderCare AI – Powered by AgentVerse
{'='*55}
"""


# ── Future Integration Points ──────────────────────────────
# TODO: Health Monitoring Agent  – auto-select condition from live vitals
# TODO: Medicine Reminder Agent  – align meal times with medicine schedule
# TODO: Exercise Coach Agent     – combine diet + exercise plan
# TODO: Family Notifier Agent    – send diet plan to family caregiver
# TODO: Voice Companion Agent    – read diet plan aloud for elder users
# TODO: Appointment Booking Agent – book dietitian if BMI is Obese
