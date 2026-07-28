"""
exercise_data.py - Exercise plans for ElderCare AI
"""

EXERCISE_PLANS = {
    "General Fitness": {
        "description": "Light daily exercises to maintain mobility and strength.",
        "intensity": "Low",
        "duration": "30 minutes/day",
        "exercises": [
            {"name": "Morning Walk", "duration": "15 min", "benefit": "Improves circulation & mood"},
            {"name": "Chair Squats", "sets": "2 x 10 reps", "benefit": "Strengthens legs"},
            {"name": "Arm Circles", "sets": "2 x 15 reps", "benefit": "Shoulder mobility"},
            {"name": "Deep Breathing", "duration": "5 min", "benefit": "Reduces stress"},
            {"name": "Heel Raises", "sets": "2 x 12 reps", "benefit": "Balance & calf strength"},
        ],
        "precautions": ["Stop if you feel dizzy", "Wear comfortable shoes", "Stay hydrated"],
        "tip": "Start slow and gradually increase duration each week.",
    },
    "Diabetes Management": {
        "description": "Aerobic and resistance exercises to control blood sugar.",
        "intensity": "Moderate",
        "duration": "45 minutes/day",
        "exercises": [
            {"name": "Brisk Walking", "duration": "20 min", "benefit": "Lowers blood glucose"},
            {"name": "Leg Raises", "sets": "3 x 12 reps", "benefit": "Strengthens core & legs"},
            {"name": "Resistance Band Rows", "sets": "2 x 10 reps", "benefit": "Upper body strength"},
            {"name": "Seated Marching", "duration": "5 min", "benefit": "Improves circulation"},
            {"name": "Yoga Stretches", "duration": "10 min", "benefit": "Flexibility & stress relief"},
        ],
        "precautions": [
            "Check blood sugar before exercise",
            "Carry a snack in case of low sugar",
            "Avoid exercise if sugar > 250 mg/dL",
        ],
        "tip": "Exercise after meals (1-2 hours) for best blood sugar control.",
    },
    "High Blood Pressure": {
        "description": "Low-intensity aerobic exercises to reduce blood pressure.",
        "intensity": "Low-Moderate",
        "duration": "30 minutes/day",
        "exercises": [
            {"name": "Slow Walking", "duration": "20 min", "benefit": "Lowers BP naturally"},
            {"name": "Seated Yoga", "duration": "10 min", "benefit": "Reduces stress & BP"},
            {"name": "Neck Stretches", "sets": "3 x 10 reps", "benefit": "Relieves tension"},
            {"name": "Diaphragmatic Breathing", "duration": "5 min", "benefit": "Calms nervous system"},
            {"name": "Gentle Tai Chi", "duration": "10 min", "benefit": "Balance & relaxation"},
        ],
        "precautions": [
            "Avoid heavy lifting",
            "No breath-holding during exercise",
            "Stop if BP > 180/110",
            "Monitor BP before and after",
        ],
        "tip": "Consistency is key – 30 min daily walk reduces BP by 5-8 mmHg.",
    },
    "Arthritis": {
        "description": "Gentle range-of-motion exercises to reduce joint pain.",
        "intensity": "Very Low",
        "duration": "20-30 minutes/day",
        "exercises": [
            {"name": "Water Walking (if available)", "duration": "15 min", "benefit": "Low-impact joint exercise"},
            {"name": "Finger Bends", "sets": "3 x 10 reps", "benefit": "Hand joint flexibility"},
            {"name": "Knee Extensions (seated)", "sets": "2 x 10 reps", "benefit": "Knee strength"},
            {"name": "Shoulder Rolls", "sets": "2 x 10 reps", "benefit": "Shoulder mobility"},
            {"name": "Gentle Stretching", "duration": "10 min", "benefit": "Reduces stiffness"},
        ],
        "precautions": [
            "Never exercise through sharp pain",
            "Apply warm compress before exercise",
            "Rest if joints are swollen",
            "Avoid high-impact activities",
        ],
        "tip": "Warm up joints with a hot water bag before exercising.",
    },
    "Post-Recovery": {
        "description": "Very gentle exercises for recovery after illness or surgery.",
        "intensity": "Very Low",
        "duration": "15-20 minutes/day",
        "exercises": [
            {"name": "Bed Exercises (ankle pumps)", "sets": "3 x 10 reps", "benefit": "Prevents blood clots"},
            {"name": "Seated Deep Breathing", "duration": "5 min", "benefit": "Lung recovery"},
            {"name": "Gentle Arm Raises", "sets": "2 x 8 reps", "benefit": "Shoulder mobility"},
            {"name": "Short Walk (indoors)", "duration": "5-10 min", "benefit": "Gradual mobility"},
            {"name": "Neck Tilts", "sets": "2 x 8 reps", "benefit": "Neck flexibility"},
        ],
        "precautions": [
            "Always consult doctor before starting",
            "Have someone nearby for support",
            "Stop immediately if pain increases",
            "Increase duration only with doctor approval",
        ],
        "tip": "Recovery takes time – listen to your body and rest when needed.",
    },
}

FITNESS_LEVELS = ["Beginner", "Intermediate", "Active"]
CONDITIONS = list(EXERCISE_PLANS.keys())

WEEKLY_SCHEDULE = {
    "Monday": "Full routine",
    "Tuesday": "Light stretching only",
    "Wednesday": "Full routine",
    "Thursday": "Rest or gentle walk",
    "Friday": "Full routine",
    "Saturday": "Light stretching only",
    "Sunday": "Complete rest",
}


def get_exercise_plan(condition: str) -> dict:
    return EXERCISE_PLANS.get(condition, EXERCISE_PLANS["General Fitness"])
