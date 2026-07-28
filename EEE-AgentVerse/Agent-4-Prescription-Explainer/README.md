# ElderCare AI – Prescription Explainer Agent

## Project Overview
ElderCare AI is a simple, elderly-friendly Streamlit web app designed for a college hackathon. It helps patients understand their prescriptions in clear language, covering the medicine purpose, timing, precautions, and possible side effects.

## Features
- Friendly home page with easy navigation
- Patient information form with validation
- Simple medicine explanation for dosage and timing
- Clear precautions and side-effect guidance
- Prescription summary with download support
- Clean, healthcare-themed UI

## Architecture
The project follows a modular structure:
- app.py: Main Streamlit application and UI flow
- medicine_data.py: Medicine knowledge base and explanation data
- utils.py: Validation and summary helpers

## Installation
1. Open a terminal in the project folder.
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the App
Run the app with:

```bash
streamlit run app.py
```

## Example Output
A patient may enter:
- Name: Mrs. Sharma
- Age: 72
- Medicine: Paracetamol
- Dosage: 500 mg
- Frequency: Twice daily
- Food: After food
- Duration: 5 days

The app will explain:
- The purpose of the medicine
- How to take it safely
- Common precautions
- Typical side effects
- A printable summary

## Future Scope
Planned future integrations include:
- Medicine Reminder Agent
- Appointment Booking Agent
- Emergency Detection Agent
- Health Monitoring Agent
- Family Notification Agent
- Voice Companion Agent
- Diet Planning Agent
- Exercise Coach Agent
- Hospital Navigation Agent

## ElderCare AI Overview
ElderCare AI aims to make healthcare easier and safer for older adults by combining simple digital tools with compassionate design.

## Hackathon Description
This project was created as a Day 1 Single Agent Challenge submission for a college hackathon. The goal is to build a complete, runnable, and demo-ready AI assistant experience using Python and Streamlit.
