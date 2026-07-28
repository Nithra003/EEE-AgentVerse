# 🏥 ElderCare AI – Appointment Booking Agent

> **Day 1 – Single Agent Challenge | College Hackathon**

An AI-powered appointment booking assistant designed for senior citizens.
Uses **Google Gemini AI** to analyse symptoms and recommend the right medical specialist.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🤖 AI Symptom Analysis | Gemini 1.5 Flash analyses free-text symptoms |
| 👨‍⚕️ Doctor Recommendation | Matches patient to the right specialist |
| 📅 Slot Booking | Choose from available time slots |
| 🪪 Appointment ID | Auto-generated unique ID (e.g. APT-20260727-1001) |
| 📥 Download Confirmation | Plain-text confirmation file |
| ✅ Validation | Name, age, phone, symptoms all validated |
| 👴 Elder-Friendly UI | Large fonts, big buttons, high-contrast theme |

---

## 🗂️ Project Structure

```
AgentVerse/
├── app.py            # Main Streamlit application & page router
├── doctors.py        # Doctor data, slots, and symptom keyword map
├── utils.py          # Validation, Gemini AI, ID generation, confirmation builder
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a Gemini API Key (free)
Visit → https://aistudio.google.com/app/apikey

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Enter your Gemini API key in the sidebar and start booking!

---

## 🩺 Supported Specialties

| Symptoms | Specialist |
|---|---|
| Fever, Cold, Cough, Headache | General Physician |
| Chest Pain, Palpitations | Cardiologist |
| Joint Pain, Back Pain, Fracture | Orthopedic |
| Eye Problems, Vision Issues | Ophthalmologist |
| Tooth Pain, Gum Problems | Dentist |
| Skin Rash, Allergy, Acne | Dermatologist |

> Without a Gemini API key, the app falls back to keyword-based matching automatically.

---

## 🔮 Future Agent Integration Points

The codebase contains clearly marked `# FUTURE INTEGRATION POINT` comments
for the following planned agents:

- 💊 **Medicine Reminder Agent** – post-appointment medication reminders
- 🚨 **Emergency Detection Agent** – real-time critical symptom alerts
- 📄 **Prescription Explainer Agent** – plain-language prescription summaries
- 📊 **Health Monitoring Agent** – wearable vitals dashboard
- 👨‍👩‍👧 **Family Notification Agent** – SMS/WhatsApp alerts to family
- 🎙️ **Voice Companion Agent** – voice navigation for elders
- 🥗 **Diet Planning Agent** – personalised dietary recommendations
- 🏃 **Exercise Coach Agent** – safe senior exercise plans
- 🗺️ **Hospital Navigation Agent** – indoor hospital wayfinding

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **Streamlit** – UI framework
- **Google Generative AI SDK** – Gemini 1.5 Flash

---

## 📸 App Flow

```
Home Page → Patient Form → AI Symptom Analysis
         → Doctor Selection → Appointment Confirmation → Download
```

---

*Built with ❤️ for ElderCare AI – Hackathon Day 1*
