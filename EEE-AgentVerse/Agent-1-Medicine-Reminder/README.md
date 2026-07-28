# eldercare-agents

A simple Python project for an AI multi-agent hackathon focused on eldercare reminders.

## Project structure

- agents/medicine_reminder.py: medicine reminder agent implementation
- orchestrator.py: runs the demo scenarios
- demo_data.py: sample scenarios
- requirements.txt: Python dependencies
- .env.example: example environment variables

## Setup

1. Create a virtual environment:
   python -m venv .venv
2. Activate it:
   - Windows: .venv\\Scripts\\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Copy .env.example to .env and set your Anthropic API key.

## Run the demo

python orchestrator.py

## Notes

- The agent returns only valid JSON in the required structure.
- If the Anthropic API is unavailable, the agent uses a deterministic fallback response.
- The implementation avoids medical advice and keeps the tone warm and respectful.
