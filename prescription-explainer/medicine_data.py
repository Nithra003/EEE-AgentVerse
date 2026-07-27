from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class MedicineDetails:
    """Structured details for a medicine explanation."""

    name: str
    purpose: str
    treats: str
    how_to_take: str
    best_time: str
    precautions: list[str]
    storage: list[str]
    side_effects: list[str]
    missed_dose: str


class MedicineKnowledgeBase:
    """A simple in-memory knowledge base for common medicines."""

    def __init__(self) -> None:
        self._database: Dict[str, MedicineDetails] = {
            "paracetamol": MedicineDetails(
                name="Paracetamol 500 mg",
                purpose="Helps reduce fever and body pain.",
                treats="Fever, mild aches, and pain.",
                how_to_take="Take {dosage} {frequency} with water.",
                best_time="Take it after food for a gentler stomach experience.",
                precautions=[
                    "Do not take more than the recommended amount.",
                    "Avoid alcohol while using this medicine.",
                    "If you have liver problems, ask a doctor before use.",
                ],
                storage=["Store in a cool, dry place.", "Keep the bottle closed.", "Keep away from children."],
                side_effects=["Mild stomach upset", "Sleepiness", "Nausea"],
                missed_dose="If you miss a dose, take it when you remember unless it is close to the next dose.",
            ),
            "amoxicillin": MedicineDetails(
                name="Amoxicillin",
                purpose="Helps fight bacterial infection.",
                treats="Common bacterial infections such as throat or chest infections.",
                how_to_take="Take {dosage} {frequency} with or after food.",
                best_time="Take it at the same time each day.",
                precautions=[
                    "Complete the full course unless a doctor says otherwise.",
                    "Tell your doctor if you have a penicillin allergy.",
                    "Use only as directed.",
                ],
                storage=["Store at room temperature.", "Keep the medicine dry.", "Keep away from children."],
                side_effects=["Diarrhea", "Nausea", "Rash"],
                missed_dose="If you miss a dose, take it as soon as you remember. If it is almost time for the next one, skip the missed dose.",
            ),
            "metformin": MedicineDetails(
                name="Metformin",
                purpose="Helps control blood sugar levels.",
                treats="Type 2 diabetes.",
                how_to_take="Take {dosage} {frequency} with meals.",
                best_time="Take it with food to reduce stomach upset.",
                precautions=[
                    "Do not stop it suddenly without medical advice.",
                    "Drink enough water.",
                    "Tell your doctor if you feel very weak or dizzy.",
                ],
                storage=["Store at room temperature.", "Keep in a dry place.", "Keep away from children."],
                side_effects=["Mild stomach upset", "Diarrhea", "Loss of appetite"],
                missed_dose="If you miss a dose, take it when you remember. If it is close to the next dose, skip the missed dose.",
            ),
            "atorvastatin": MedicineDetails(
                name="Atorvastatin",
                purpose="Helps lower cholesterol levels.",
                treats="High cholesterol and heart risk.",
                how_to_take="Take {dosage} {frequency} once daily.",
                best_time="Take it in the evening if advised by your doctor.",
                precautions=[
                    "Take it as prescribed.",
                    "Tell your doctor about muscle pain or weakness.",
                    "Avoid grapefruit juice.",
                ],
                storage=["Store at room temperature.", "Keep away from moisture.", "Keep out of reach of children."],
                side_effects=["Muscle aches", "Headache", "Feeling tired"],
                missed_dose="If you miss a dose, take it when you remember. If it is close to the next dose, skip the missed dose.",
            ),
        }

    def get_medicine(self, medicine_name: str) -> Optional[MedicineDetails]:
        """Return a known medicine from the in-memory database."""
        if not medicine_name:
            return None
        key = medicine_name.strip().lower()
        return self._database.get(key)

    def get_generic_medicine(self, medicine_name: str) -> MedicineDetails:
        """Create a safe fallback explanation for unknown medicines."""
        return MedicineDetails(
            name=medicine_name.strip() or "Medicine",
            purpose="This medicine is intended to support your treatment plan.",
            treats="The condition your doctor has prescribed it for.",
            how_to_take="Take {dosage} {frequency} exactly as directed by your doctor or pharmacist.",
            best_time="Take it at the same time each day if possible.",
            precautions=[
                "Follow the label or pharmacist instructions carefully.",
                "Do not change the dose without medical advice.",
                "Keep the medicine in a safe place.",
            ],
            storage=["Store in a cool, dry place.", "Keep out of reach of children."],
            side_effects=["Mild stomach upset", "Dizziness", "Headache"],
            missed_dose="If you miss a dose, ask your pharmacist or doctor for the safest next step.",
        )
