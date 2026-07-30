"""
Emergency Detection Agent for Elder Care System
- Simulates elderly monitoring using sensor data
- Detects falls based on posture, movement, and time on ground
- Sends emergency alerts to the Response Agent
"""

import random
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime
from uagents import Agent, Context, Model
from shared.agent_bridge import emergency_to_family


class EmergencyAlert(Model):
    person_name: str
    status: str
    location: str
    risk_level: str
    timestamp: str
    movement: str
    posture: str
    time_on_ground: int


detection_agent = Agent(
    name="emergency_detection_agent",
    seed="emergency_detection_agent_secret_seed",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
)

# The response agent address is deterministic from its seed — computed correctly here
from uagents import Agent as _A
_resp = _A(name="emergency_response_agent", seed="emergency_response_agent_secret_seed")
RESPONSE_AGENT_ADDRESS = os.getenv("RESPONSE_AGENT_ADDRESS", _resp.address)


@detection_agent.on_message(model=EmergencyAlert)
async def handle_alert_response(ctx: Context, sender: str, msg: EmergencyAlert):
    ctx.logger.info(f"Response Agent acknowledged alert: {msg.status}")


def simulate_sensor_data():
    is_emergency = random.random() < 0.3

    if is_emergency:
        movement = "none"
        posture = "lying"
        time_on_ground = random.randint(21, 60)
    else:
        movement = random.choice(["none", "low", "high"])
        posture = random.choice(["standing", "sitting"])
        time_on_ground = random.randint(0, 10)

    return {"movement": movement, "posture": posture, "time_on_ground": time_on_ground}


def detect_emergency(sensor_data):
    is_fall = (
        sensor_data["posture"] == "lying"
        and sensor_data["movement"] == "none"
        and sensor_data["time_on_ground"] > 20
    )
    return (True, "Fall Detected") if is_fall else (False, "Safe")


@detection_agent.on_event("startup")
async def startup(ctx: Context):
    print("\n" + "="*50)
    print("Emergency Detection Agent Started")
    print("="*50)
    print(f"Agent Address  : {detection_agent.address}")
    print(f"Response Agent : {RESPONSE_AGENT_ADDRESS}")
    print()
    print("Starting continuous monitoring...")
    print("Reading sensor data every 8 seconds")
    print("="*50 + "\n")
    ctx.logger.info("Detection Agent startup sequence initiated")


@detection_agent.on_interval(period=8.0)
async def monitor(ctx: Context):
    sensor_data = simulate_sensor_data()
    is_emergency, status = detect_emergency(sensor_data)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n--- Sensor Reading ---")
    print(f"Movement       : {sensor_data['movement']}")
    print(f"Posture        : {sensor_data['posture']}")
    print(f"Time on ground : {sensor_data['time_on_ground']} seconds")

    if is_emergency:
        risk_level = "HIGH"
        print("Status         : Emergency detected!")
        print("Sending alert to Response Agent...")
        emergency_to_family(
            patient_name="John Doe",
            location="Living Room",
            risk_level=risk_level,
            status=status,
        )
    else:
        risk_level = "LOW"
        print("Status         : Safe")

    alert = EmergencyAlert(
        person_name="John Doe",
        status=status,
        location="Living Room",
        risk_level=risk_level,
        timestamp=timestamp,
        movement=sensor_data["movement"],
        posture=sensor_data["posture"],
        time_on_ground=sensor_data["time_on_ground"],
    )

    try:
        await ctx.send(RESPONSE_AGENT_ADDRESS, alert)
        if is_emergency:
            print("Alert sent successfully.")
    except Exception as e:
        if is_emergency:
            ctx.logger.warning(f"Failed to send emergency alert: {str(e)}")
            print("Could not send alert. Is Response Agent running?")
        else:
            ctx.logger.debug(f"Could not send status update: {str(e)}")

    print("Waiting for next reading...")


if __name__ == "__main__":
    detection_agent.run()
