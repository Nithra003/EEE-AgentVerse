"""
diet_data.py - Diet plans and nutrition data for ElderCare AI
"""

DIET_PLANS = {
    "Diabetes": {
        "description": "Low sugar, high fiber diet to manage blood glucose levels.",
        "foods_to_eat": [
            "Brown rice", "Oats", "Green leafy vegetables", "Bitter gourd",
            "Fenugreek seeds", "Lentils", "Fish", "Nuts (unsalted)",
        ],
        "foods_to_avoid": [
            "White rice", "Sugar & sweets", "Fruit juices", "White bread",
            "Fried foods", "Alcohol", "Processed snacks",
        ],
        "meal_plan": {
            "Breakfast": "Oats porridge with nuts + 1 boiled egg",
            "Mid-Morning": "1 small fruit (guava or apple)",
            "Lunch": "Brown rice + dal + sabzi + salad",
            "Evening Snack": "Roasted chana or cucumber slices",
            "Dinner": "2 rotis + vegetable curry + curd",
        },
        "water_intake": "8-10 glasses per day",
        "tip": "Eat small meals every 3 hours to keep blood sugar stable.",
    },
    "High Blood Pressure": {
        "description": "Low sodium, potassium-rich DASH diet to control blood pressure.",
        "foods_to_eat": [
            "Bananas", "Spinach", "Beets", "Garlic", "Oats",
            "Low-fat dairy", "Berries", "Whole grains", "Fish",
        ],
        "foods_to_avoid": [
            "Salt & pickles", "Processed meats", "Canned foods",
            "Fried snacks", "Alcohol", "Caffeine (excess)", "Red meat",
        ],
        "meal_plan": {
            "Breakfast": "Oats with banana + low-fat milk",
            "Mid-Morning": "Coconut water or buttermilk (no salt)",
            "Lunch": "2 rotis + spinach dal + salad (no salt dressing)",
            "Evening Snack": "Handful of unsalted nuts",
            "Dinner": "Brown rice + fish curry (low salt) + vegetables",
        },
        "water_intake": "8 glasses per day",
        "tip": "Reduce salt intake to less than 1500mg per day.",
    },
    "Heart Disease": {
        "description": "Heart-healthy diet low in saturated fats and cholesterol.",
        "foods_to_eat": [
            "Salmon", "Walnuts", "Flaxseeds", "Olive oil", "Oats",
            "Berries", "Leafy greens", "Legumes", "Whole grains",
        ],
        "foods_to_avoid": [
            "Butter & ghee (excess)", "Red meat", "Full-fat dairy",
            "Fried foods", "Trans fats", "Alcohol", "Sugary drinks",
        ],
        "meal_plan": {
            "Breakfast": "Oats with flaxseeds + green tea",
            "Mid-Morning": "Handful of walnuts + 1 fruit",
            "Lunch": "2 rotis + dal + steamed vegetables",
            "Evening Snack": "Sprouts salad",
            "Dinner": "Grilled fish + brown rice + salad",
        },
        "water_intake": "8 glasses per day",
        "tip": "Use olive oil for cooking. Avoid trans fats completely.",
    },
    "Arthritis": {
        "description": "Anti-inflammatory diet to reduce joint pain and swelling.",
        "foods_to_eat": [
            "Turmeric", "Ginger", "Salmon", "Walnuts", "Berries",
            "Broccoli", "Spinach", "Olive oil", "Green tea",
        ],
        "foods_to_avoid": [
            "Processed foods", "Sugar", "Red meat", "Alcohol",
            "Refined carbs", "Fried foods", "Excess salt",
        ],
        "meal_plan": {
            "Breakfast": "Turmeric milk + whole grain toast",
            "Mid-Morning": "Berries or orange",
            "Lunch": "Brown rice + fish + broccoli stir fry",
            "Evening Snack": "Ginger tea + handful of walnuts",
            "Dinner": "Vegetable soup + 2 rotis",
        },
        "water_intake": "8-10 glasses per day",
        "tip": "Add turmeric and ginger to daily meals for natural anti-inflammation.",
    },
    "General Wellness": {
        "description": "Balanced diet for overall health and energy in elderly.",
        "foods_to_eat": [
            "Fruits & vegetables", "Whole grains", "Lean protein",
            "Low-fat dairy", "Nuts & seeds", "Legumes", "Fish",
        ],
        "foods_to_avoid": [
            "Junk food", "Excess sugar", "Excess salt",
            "Alcohol", "Processed foods", "Sugary drinks",
        ],
        "meal_plan": {
            "Breakfast": "Idli/dosa + sambar + fruit",
            "Mid-Morning": "1 fruit or buttermilk",
            "Lunch": "Rice + dal + sabzi + salad + curd",
            "Evening Snack": "Tea + roasted snack",
            "Dinner": "2 rotis + vegetable curry + soup",
        },
        "water_intake": "8 glasses per day",
        "tip": "Eat colorful vegetables daily for vitamins and minerals.",
    },
}

CONDITIONS = list(DIET_PLANS.keys())

BMI_CATEGORIES = {
    "Underweight": (0, 18.5),
    "Normal": (18.5, 24.9),
    "Overweight": (25, 29.9),
    "Obese": (30, 999),
}


def calculate_bmi(weight_kg: float, height_cm: float) -> tuple:
    """Calculate BMI and return value + category."""
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0, "Invalid"
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)
    for category, (low, high) in BMI_CATEGORIES.items():
        if low <= bmi < high:
            return bmi, category
    return bmi, "Obese"


def get_diet_plan(condition: str) -> dict:
    """Return diet plan for a given condition."""
    return DIET_PLANS.get(condition, DIET_PLANS["General Wellness"])
