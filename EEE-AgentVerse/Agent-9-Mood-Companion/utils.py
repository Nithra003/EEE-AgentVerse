"""
utils.py - Utility functions for Mood Companion Agent
"""

from datetime import datetime


def validate_fields(name, age, mood) -> list:
    errors = []
    if not name.strip():
        errors.append("Please enter your name.")
    if not (1 <= age <= 120):
        errors.append("Age must be between 1 and 120.")
    if not mood:
        errors.append("Please select how you are feeling.")
    return errors


def generate_report_text(data: dict) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = data["response"]
    activity_lines = "\n".join(f"  • {a}" for a in response["activities"])

    return f"""
{'='*55}
       ELDERCARE AI – MOOD COMPANION REPORT
{'='*55}
Generated     : {now}
{'─'*55}
Name          : {data['name']}
Age           : {data['age']} years
Current Mood  : {data['mood']}
{'─'*55}
Message       : {response['message']}
{'─'*55}
SUGGESTED ACTIVITIES:
{activity_lines}
{'─'*55}
💬 Affirmation: {response['affirmation']}
💡 Tip        : {response['tip']}
{'─'*55}
Mood Log      : {data['mood']} at {now}
{'='*55}
      ElderCare AI – Powered by AgentVerse
{'='*55}
"""


# ── Future Integration Points ──────────────────────────────
# TODO: Voice Companion Agent    – read mood response aloud
# TODO: Exercise Coach Agent     – suggest exercise based on mood
# TODO: Diet Recommendation Agent – suggest comfort foods for sad/anxious mood
# TODO: Family Notifier Agent    – alert family if mood is consistently sad/anxious
# TODO: Health Monitoring Agent  – correlate mood with vitals data
# TODO: Medicine Reminder Agent  – check if mood change is medicine side effect
