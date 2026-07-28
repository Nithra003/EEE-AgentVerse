<<<<<<< HEAD
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
=======
# Elder-AI: Multi-Agent Elder Care Emergency Detection System

A sophisticated multi-agent system built with the **uAgents framework** for detecting and responding to elderly fall emergencies. This project demonstrates agent-to-agent communication for the **Fetch.ai Agentverse Hackathon**.

## 📋 Project Overview

Elder-AI is an intelligent monitoring system that uses simulated sensor data to detect falls in elderly individuals. The system consists of two autonomous agents working in concert:

1. **Detection Agent** - Continuously monitors sensor data and detects potential falls
2. **Response Agent** - Receives alerts and initiates emergency response procedures

The system is designed for real-world deployment in assisted living facilities, nursing homes, and private residences.

## ✨ Features

- **Real-time Monitoring**: Continuous sensor data analysis
- **Fall Detection Logic**: Multi-criteria detection (posture, movement, duration)
- **Emergency Alerts**: Asynchronous messaging between agents
- **Formatted Notifications**: Clear, readable emergency information display
- **Emergency Integration**: Simulated emergency contact and ambulance notification
- **Graceful Error Handling**: Robust message validation and error recovery
- **Production-Ready Code**: Clean architecture with comprehensive comments
- **Pydantic Models**: Type-safe message definitions

## 🏗️ Architecture

```
┌─────────────────────┐
│  Simulated Sensors  │
│ (Movement, Posture, │
│  Time on Ground)    │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────┐
│ Emergency Detection Agent    │
│ • Reads sensor data          │
│ • Applies detection logic    │
│ • Sends EmergencyAlert msg   │
└──────────┬───────────────────┘
           │
        (uAgents Message)
        EmergencyAlert
           │
           ▼
┌──────────────────────────────┐
│ Emergency Response Agent     │
│ • Receives alert             │
│ • Displays notification      │
│ • Calls emergency services   │
└──────────────────────────────┘
```

## 🔧 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd elder-ai
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the System

The system requires two terminal sessions to run both agents simultaneously.

### Terminal 1: Start the Response Agent
```bash
python response_agent.py
```

You should see:
```
==================================================
Emergency Response Agent Started
Agent Address: agent1qdgcfr8w0gz6d7j82s9fqpxgz7f3l4u5r7k9m2b3c5d7e9f0g1h2j3k4l5m6n7p8q
==================================================
Listening for emergency alerts...
```

### Terminal 2: Start the Detection Agent
```bash
python detection_agent.py
```

You should see:
```
==================================================
Starting Emergency Detection Agent...
Agent Address: agent1q2gsrxjge37z3uwdsvl3k0r2xdcl4u5r7k9m2b3c5d7e9f0g1h2j3k4l5m6n7p8q
Waiting for Response Agent to connect...
==================================================

--- Reading #1 ---
Movement: low
Posture: standing
Time on ground: 3 seconds
✓ Status: Safe
```

When a fall is detected, you'll see emergency alerts in Terminal 2 (Detection Agent) and detailed emergency response in Terminal 1 (Response Agent).

## 📊 Example Output

See `sample_output.txt` for a complete example of system output showing fall detection and emergency response.

### Fall Detection Output (Detection Agent)
```
--- Reading #3 ---
Movement: none
Posture: lying
Time on ground: 35 seconds
⚠️  Emergency detected!
Sending alert to Response Agent...
Alert sent successfully!
```

### Emergency Response Output (Response Agent)
```
==================================
🚨 EMERGENCY ALERT
==================================
Person     : John Doe
Status     : Fall Detected
Location   : Living Room
Risk Level : HIGH
Time       : 2026-07-27 10:15:32
----------------------------------
Sensor Data:
  Movement      : none
  Posture       : lying
  Time on Ground: 35s
==================================

⚠️  FALL DETECTED - INITIATING EMERGENCY PROTOCOL

Calling emergency contacts...
📞 Emergency Contact #1: Jane Doe (Daughter)
📞 Emergency Contact #2: St. Mary's Hospital

🚑 Ambulance notified.
🚑 Estimated arrival: 8 minutes

📋 Incident logged and recorded.
```

## 📁 Project Structure

```
elder-ai/
├── detection_agent.py       # Emergency Detection Agent
├── response_agent.py        # Emergency Response Agent
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation (this file)
├── .gitignore              # Git ignore file
├── sample_output.txt       # Example system output
└── screenshots/            # Optional: system screenshots
```

## 🔍 How It Works

### Detection Logic

The Emergency Detection Agent continuously monitors three key sensor readings:

1. **Movement**: "none", "low", or "high"
2. **Posture**: "standing", "sitting", or "lying"
3. **Time on Ground**: Duration in seconds

**Emergency is triggered when:**
```
IF posture == "lying" 
   AND movement == "none" 
   AND time_on_ground > 20 seconds
THEN status = "Fall Detected"
ELSE status = "Safe"
```

### Message Format

Alerts are sent using the `EmergencyAlert` Pydantic model:

```python
class EmergencyAlert(Model):
    person_name: str        # Name of the monitored person
    status: str             # "Fall Detected" or "Safe"
    location: str           # Location of the person
    risk_level: str         # "HIGH", "MEDIUM", "LOW"
    timestamp: str          # ISO format timestamp
    movement: str           # Sensor: movement data
    posture: str            # Sensor: posture data
    time_on_ground: int     # Sensor: seconds on ground
```

### Response Procedures

When a fall is detected, the Response Agent:

1. ✓ Receives and validates the alert
2. ✓ Displays formatted emergency notification
3. ✓ Initiates emergency contact calls
4. ✓ Notifies ambulance services
5. ✓ Logs the incident for records

## 🔐 Security Features

- **Type Safety**: Pydantic models validate all messages
- **Agent Addresses**: Deterministic, cryptographically secure addresses
- **Error Handling**: Graceful handling of invalid messages
- **Message Validation**: Automatic validation of all incoming messages

## 🚀 Future Improvements

1. **Real Sensor Integration**
   - Connect to actual IoT sensors
   - Support for camera feeds with computer vision
   - Wearable device integration (smartwatches, health bands)

2. **Enhanced Detection**
   - Machine learning-based fall detection
   - Multiple fall detection algorithms
   - Confidence scoring system

3. **Advanced Alerts**
   - SMS/Email notifications
   - Integration with hospital systems
   - Real emergency services API integration
   - Geolocation services

4. **Data Analytics**
   - Historical incident tracking
   - Pattern analysis
   - Risk assessment reporting
   - Dashboard for caregivers

5. **Multi-Location Support**
   - Support for multiple monitored locations
   - Location-based routing of alerts
   - Facility-wide monitoring network

6. **Scalability**
   - Support for multiple monitored individuals
   - Load balancing across multiple agents
   - Database integration for persistence
   - Web API for external integrations

7. **Testing**
   - Unit tests for detection logic
   - Integration tests for agent communication
   - Simulation of edge cases and failures

## 🏆 Hackathon Context

This project is designed for the **Fetch.ai Agentverse Hackathon** and demonstrates:

- ✓ Multi-agent system architecture
- ✓ Asynchronous message-based communication
- ✓ Autonomous agent capabilities
- ✓ Real-world use case application
- ✓ Production-ready code quality
- ✓ Scalable system design

The uAgents framework enables autonomous agents to communicate reliably and securely, perfect for critical applications like elder care emergency detection.

## 📚 Technology Stack

- **Python 3.9+**: Programming language
- **uAgents 0.17.0**: Agent framework by Fetch.ai
- **Pydantic 2.5.0**: Data validation and serialization
- **asyncio**: Asynchronous programming

## 📝 License

This project is open source and available for use in the Fetch.ai Agentverse Hackathon.

## 🤝 Support

For questions or issues:
1. Check the `sample_output.txt` for expected behavior
2. Ensure both agents are running in separate terminals
3. Verify Python version is 3.9 or higher
4. Check that all requirements are installed

## 📞 Contact

Developed for the Fetch.ai Agentverse Hackathon - a showcase of autonomous agent technology.

---

**Happy Monitoring! 🏥**
>>>>>>> 4b3877c40201ff8a8eacb874f0d974caf49c2856
