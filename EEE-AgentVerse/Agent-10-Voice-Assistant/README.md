# ElderCare AI – Voice Companion Agent

## Project Overview
ElderCare AI – Voice Companion Agent is a friendly Streamlit web application created for the Day 1 Single Agent Challenge. It provides emotional support, simple conversation, wellness suggestions, and daily motivation for elderly users in a calming and accessible interface.

## Features
- Friendly home page with a calm healthcare design
- Patient information form with validation
- Voice companion chat interface using Streamlit chat components
- Supportive AI responses tailored to the selected mood
- Wellness suggestions based on mood
- Daily motivation button with random inspirational quotes
- Conversation history shown in a dataframe
- Future integration points for other ElderCare AI agents

## Architecture
The project follows a modular structure:
- app.py: main Streamlit application entry point
- chatbot.py: response generation and wellness logic
- responses.py: predefined messages, quotes, and integration notes
- utils.py: validation and history handling

## Installation
1. Open a terminal in the project folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Instructions
Start the app with:
```bash
streamlit run app.py
```

## Example Output
Example interaction:
```text
User: I am feeling lonely today.
AI: I am here with you. Would you like to talk or hear a cheerful story?
```

## Future Scope
The app is designed to integrate with future ElderCare AI agents such as medicine reminders, appointment booking, emergency support, and family notification systems.

## ElderCare AI Overview
ElderCare AI is a compassionate digital support system for older adults. It combines conversation, wellness guidance, and future automation to create a safer and more supportive experience.

## Hackathon Description
This project is designed for a college hackathon demo and focuses on a simple, polished, production-style single-agent experience that can later evolve into a multi-agent healthcare assistant.
