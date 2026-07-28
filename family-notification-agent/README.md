# 🚨 ElderCare AI – Family Notification Agent

> **AgentVerse Hackathon · Day 1 – Single Agent Challenge**

An AI-powered Family Notification Agent that automatically alerts family members during elder care emergencies or important health events.

---

## 📌 Project Overview

The **Family Notification Agent** is the first agent in the **ElderCare AI** multi-agent system. It provides instant, automated emergency notifications to family members when an elderly person faces a health crisis — such as a fall, missed medicine, high blood pressure, or an SOS alert.

Built with **Python + Streamlit**, it is designed to be elder-friendly, fast, and ready for real-world integration.

---

## ✨ Features

- 📋 **Patient & Emergency Form** – Collects patient details and emergency type
- 🚨 **Smart Priority Engine** – Auto-assigns Medium / High / Critical priority
- 📡 **Notification Simulation** – Simulates SMS, Email, and Call alerts
- 📊 **Notification History** – Session-based history table with delivery status
- 📥 **Downloadable Report** – One-click emergency report as `.txt` file
- ✅ **Full Validation** – Age, phone number, and required field checks
- 🏥 **Elder-Friendly UI** – Large fonts, clear layout, healthcare color theme

---

## 🏗️ Architecture

```
family-notification-agent/
│
├── app.py               ← Main Streamlit UI (all pages & sections)
├── notifications.py     ← Notification builder, simulator, history manager
├── utils.py             ← Validation, priority logic, report generator
├── requirements.txt     ← Python dependencies
├── README.md            ← Project documentation
└── sample_output.txt    ← Demo output for presentation
```

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/EEE-AgentVerse-New.git
cd EEE-AgentVerse-New/family-notification-agent

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Running the App

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🖥️ Example Output

```
✅ Emergency notification generated successfully!

🚨 Emergency Alert – Fall Detected
👤 Patient : Rajamani Krishnan | Age: 72
📍 Location: 12, Anna Nagar, Chennai
🕐 Date & Time: 2025-07-15 at 14:32:10
👥 Contact : Karthik Rajamani (Son)
📞 Number  : 9876543210
🚨 Priority: Critical

📩 SMS sent successfully.
📧 Email notification dispatched.
📞 Emergency contact notified.
🚑 Emergency services can now be contacted.
```

---

## 🔮 Future Scope

| Agent | Integration Plan |
|---|---|
| 💊 Medicine Reminder Agent | Trigger on "Missed Medicine" emergency |
| 📅 Appointment Booking Agent | Auto-book doctor after High/Critical alert |
| 🚨 Emergency Detection Agent | Replace manual form with live sensor data |
| 📋 Prescription Explainer Agent | Attach prescription to notification report |
| ❤️ Health Monitoring Agent | Stream real-time vitals into the agent |
| 🎙️ Voice Companion Agent | Read alerts aloud for elder users |
| 🥗 Diet Planning Agent | Post-alert diet suggestions |
| 🏃 Exercise Coach Agent | Safe exercise plan after recovery |
| 🏥 Hospital Navigation Agent | Show nearest hospital on Critical alerts |

---

## 🤖 ElderCare AI Overview

**ElderCare AI** is a multi-agent AI system designed to provide comprehensive care for elderly individuals. It consists of 9 specialized agents that work together to monitor health, manage medications, handle emergencies, and support daily life — all powered by AI.

The **Family Notification Agent** is the emergency communication backbone of this system.

---

## 🏆 Hackathon Description

**AgentVerse Hackathon** challenges teams to build AI agent systems that solve real-world problems.

- **Day 1 Challenge:** Build a single, fully functional AI agent
- **Theme:** ElderCare AI – Caring for the elderly with technology
- **Stack:** Python, Streamlit, AI/ML tools
- **Goal:** Demonstrate a working agent ready for multi-agent integration

---

## 👨‍💻 Team

Built with ❤️ for the AgentVerse Hackathon · ElderCare AI Project
