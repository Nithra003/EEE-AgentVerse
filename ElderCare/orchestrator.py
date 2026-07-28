"""Run the medicine reminder agent against demo scenarios."""

from __future__ import annotations

import json

from agents.medicine_reminder import MedicineReminderAgent
from demo_data import SAMPLE_SCENARIOS


def main() -> None:
    """Run each demo scenario and print the resulting JSON payload."""
    agent = MedicineReminderAgent()
    for scenario in SAMPLE_SCENARIOS:
        result = agent.generate_response(
            patient_name=scenario["patient_name"],
            medicine_name=scenario["medicine_name"],
            dosage=scenario["dosage"],
            scheduled_time=scenario["scheduled_time"],
            patient_response=scenario["patient_response"],
        )
        print(json.dumps(result, indent=2))
        print()


if __name__ == "__main__":
    main()
