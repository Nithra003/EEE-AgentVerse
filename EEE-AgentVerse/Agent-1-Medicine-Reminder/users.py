"""users.py — User store for Medicine Reminder Agent"""
import json, os, hashlib
from datetime import datetime

_FILE = os.path.join(os.path.dirname(__file__), "users_data.json")

def _load() -> dict:
    if os.path.exists(_FILE):
        with open(_FILE, "r") as f:
            return json.load(f)
    return {}

def _save(data: dict):
    with open(_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def register(username: str, password: str, name: str, age: int, phone: str) -> tuple[bool, str]:
    data = _load()
    if username.lower() in data:
        return False, "Username already exists."
    data[username.lower()] = {
        "password": _hash(password),
        "name": name,
        "age": age,
        "phone": phone,
        "medicines": [],
        "dose_log": [],
        "created": datetime.now().strftime("%Y-%m-%d"),
    }
    _save(data)
    return True, "Registered successfully!"

def login(username: str, password: str) -> tuple[bool, dict | str]:
    data = _load()
    user = data.get(username.lower())
    if not user:
        return False, "User not found."
    if user["password"] != _hash(password):
        return False, "Wrong password."
    return True, user

def get_user(username: str) -> dict | None:
    return _load().get(username.lower())

def update_profile(username: str, name: str, age: int, phone: str):
    data = _load()
    if username.lower() in data:
        data[username.lower()].update({"name": name, "age": age, "phone": phone})
        _save(data)

def save_medicines(username: str, medicines: list):
    data = _load()
    if username.lower() in data:
        data[username.lower()]["medicines"] = medicines
        _save(data)

def log_dose(username: str, medicine: str, status: str, note: str = ""):
    data = _load()
    if username.lower() in data:
        data[username.lower()]["dose_log"].append({
            "medicine": medicine,
            "status": status,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "note": note,
        })
        _save(data)

def get_adherence(username: str) -> dict:
    user = get_user(username)
    if not user:
        return {"total": 0, "taken": 0, "missed": 0, "percentage": 0, "logs": []}
    logs   = user.get("dose_log", [])
    total  = len(logs)
    taken  = sum(1 for l in logs if l["status"] == "taken")
    missed = total - taken
    pct    = round((taken / total) * 100) if total > 0 else 0
    return {"total": total, "taken": taken, "missed": missed, "percentage": pct, "logs": logs}

def get_todays_log(username: str) -> list:
    user = get_user(username)
    if not user:
        return []
    today = datetime.now().strftime("%Y-%m-%d")
    return [l for l in user.get("dose_log", []) if l["time"].startswith(today)]

def check_missed_count(username: str, medicine: str) -> int:
    user = get_user(username)
    if not user:
        return 0
    return sum(1 for l in user.get("dose_log", [])
               if l["medicine"].lower() == medicine.lower() and l["status"] in ["missed", "skipped"])
