"""
utils.py - Utility functions for Exercise Coach Agent
"""

from datetime import datetime


def validate_fields(name, age, condition, fitness_level) -> list:
    errors = []
    if not name.strip():
        errors.append("Patient name is required.")
    if not (1 <= age <= 120):
        errors.append("Age must be between 1 and 120.")
    if not condition:
        errors.append("Please select a health condition.")
    if not fitness_level:
        errors.append("Please select fitness level.")
    return errors


def generate_report_text(data: dict) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plan = data["plan"]
    ex_lines = "\n".join(
        f"  • {e['name']} – {e.get('duration', e.get('sets',''))} | {e['benefit']}"
        for e in plan["exercises"]
    )
    precaution_lines = "\n".join(f"  ⚠ {p}" for p in plan["precautions"])
    schedule_lines = "\n".join(f"  {day:12}: {task}" for day, task in data["schedule"].items())

    return f"""
{'='*55}
       ELDERCARE AI – EXERCISE COACH REPORT
{'='*55}
Generated     : {now}
{'─'*55}
Patient Name  : {data['name']}
Age           : {data['age']} years
Fitness Level : {data['fitness_level']}
Condition     : {data['condition']}
{'─'*55}
Plan          : {plan['description']}
Intensity     : {plan['intensity']}
Duration      : {plan['duration']}
{'─'*55}
EXERCISES:
{ex_lines}
{'─'*55}
WEEKLY SCHEDULE:
{schedule_lines}
{'─'*55}
PRECAUTIONS:
{precaution_lines}
{'─'*55}
💡 Tip        : {plan['tip']}
{'='*55}
      ElderCare AI – Powered by AgentVerse
{'='*55}
"""


# ── Future Integration Points ──────────────────────────────
# TODO: Health Monitoring Agent  – adjust intensity based on live heart rate
# TODO: Diet Recommendation Agent – combine exercise + diet plan
# TODO: Medicine Reminder Agent  – avoid exercise during medicine side-effect hours
# TODO: Family Notifier Agent    – notify family after exercise session
# TODO: Voice Companion Agent    – voice-guided exercise instructions
# TODO: Mood Companion Agent     – suggest exercise based on mood
