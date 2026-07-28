# Health Report Agent

## Project Overview

The Health Report Agent is a production-ready Python project designed for the Fetch.ai Agentverse Hackathon. It receives health data from wearable devices or other agents, evaluates vital signs, generates a structured health report, and forwards the result to the appropriate care partner.

This project includes:
- Async agent communication with simulated caregiver and emergency response agents.
- Pydantic models for validated health input and report payloads.
- Clear risk classification and recommendations.
- A lightweight professional dashboard page for live report preview.

## Features

- Validates wearable health data with `pydantic`
- Analyzes heart rate, SpO2, temperature, blood pressure, steps, and sleep
- Classifies overall status and risk level
- Generates structured health reports
- Dispatches reports to caregiver or emergency response agents
- Serves a friendly dashboard at `http://127.0.0.1:8080/dashboard`
- Logs each processing stage for observability

## Folder Structure

```
health-report-agent/
│
├── health_report_agent.py
├── models.py
├── requirements.txt
├── README.md
├── sample_output.txt
├── .gitignore
└── screenshots/
```

## Installation

1. Install Python 3.11 or later.
2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
.\.venv\Scripts\activate.bat
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running Instructions

Run the agent locally:

```bash
python health_report_agent.py
```

After startup, open the dashboard in your browser:

```bash
http://127.0.0.1:8080/dashboard
```

The agent will generate a demo health report and keep the dashboard available until terminated.

## Architecture Diagram

```
Wearable Device
        │
        ▼
Health Report Agent
        │
Analyze Health Metrics
        │
Generate Report
        │
        ▼
Caregiver Agent / Emergency Response Agent
```

## Sample Input

```json
{
  "patient_name": "John",
  "age": 72,
  "heart_rate": 108,
  "spo2": 91,
  "body_temperature": 38.4,
  "blood_pressure": "150/95",
  "steps": 1800,
  "sleep_hours": 5,
  "timestamp": "2026-07-28T10:30:00Z"
}
```

## Sample Output

See `sample_output.txt` for the exact console output example and review the dashboard page.

## Future Improvements

- Real wearable device integration via BLE or API
- AI-powered trend prediction and anomaly detection
- Daily and weekly health summary reports
- Cloud database storage for patient history
- Dashboard visualization using React or Dash
- SMS/email notifications for caregiver alerts

## Hackathon Description

This project is built for the Fetch.ai Agentverse Hackathon. It demonstrates a modular, async healthcare agent that validates data, evaluates risk, and routes information to the best next responder.

The Health Report Agent is a strong submission because it combines clean code, robust validation, structured reporting, and a professional live dashboard.
