from datetime import datetime

import pandas as pd

VALID_GENDERS = ["Female", "Male", "Non-binary", "Prefer not to say"]
VALID_MOODS = ["Happy", "Normal", "Sad", "Anxious", "Tired", "Lonely"]


def validate_patient_form(patient_name: str, age: str, gender: str, mood: str) -> tuple[bool, str]:
    """Validate the patient information form and return a message."""
    if not patient_name or not patient_name.strip():
        return False, "Please enter the patient's name."

    if not age or not str(age).strip():
        return False, "Please enter the patient's age."

    try:
        age_value = int(age)
    except ValueError:
        return False, "Age must be a number."

    if age_value < 1 or age_value > 120:
        return False, "Please enter a realistic age between 1 and 120."

    if gender not in VALID_GENDERS:
        return False, "Please choose a valid gender option."

    if mood not in VALID_MOODS:
        return False, "Please choose a valid mood option."

    return True, "Patient details look good."


def format_timestamp() -> str:
    """Return a readable timestamp for the conversation history."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_history_dataframe(history: list[dict]) -> pd.DataFrame:
    """Convert the conversation history into a dataframe for display."""
    if not history:
        return pd.DataFrame(columns=["Time", "User Message", "AI Response"])

    return pd.DataFrame(history)[["time", "user_message", "ai_response"]].rename(
        columns={"time": "Time", "user_message": "User Message", "ai_response": "AI Response"}
    )
