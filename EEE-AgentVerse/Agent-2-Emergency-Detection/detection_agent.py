"""
Emergency Detection Agent for Elder Care System
- Simulates elderly monitoring using sensor data
- Detects falls based on posture, movement, and time on ground
- Sends emergency alerts to the Response Agent
"""

import asyncio
import random
import os
from datetime import datetime
from uagents import Agent, Context, Model


# Define the EmergencyAlert message model using Pydantic
class EmergencyAlert(Model):
    """
    Message model for emergency alerts sent from Detection Agent to Response Agent.
    Contains all relevant information about the detected emergency.
    """
    person_name: str
    status: str  # "Fall Detected" or "Safe"
    location: str
    risk_level: str  # "HIGH", "MEDIUM", "LOW"
    timestamp: str
    movement: str
    posture: str
    time_on_ground: int


# Create the Emergency Detection Agent
# The agent address is deterministic based on the name and seed
detection_agent = Agent(
    name="emergency_detection_agent",
    seed="emergency_detection_agent_secret_seed",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Store the detection agent address
DETECTION_AGENT_ADDRESS = detection_agent.address

# Response Agent address - this is deterministic based on response_agent.py seed
# The address is generated from: seed="emergency_response_agent_secret_seed", name="emergency_response_agent"
# This can be overridden by environment variable for flexibility
RESPONSE_AGENT_ADDRESS = os.getenv(
    "RESPONSE_AGENT_ADDRESS",
    "agent1qz84c5d7qg5qx4t6w5e8v7k0n3m2b5s8a1d4f7h0j3k6m9p2r5t8v1x4z7"
)


@detection_agent.on_message(model=EmergencyAlert)
async def handle_alert_response(ctx: Context, sender: str, msg: EmergencyAlert):
    """
    Handle any responses or acknowledgments from the Response Agent.
    Logs the communication for monitoring purposes.
    """
    ctx.logger.info(f"✓ Response Agent acknowledged alert: {msg.status}")


def simulate_sensor_data():
    """
    Simulate sensor data for elderly monitoring.
    
    Returns:
        dict: Contains simulated sensor readings
              - movement: "none", "low", "high"
              - posture: "standing", "sitting", "lying"
              - time_on_ground: time in seconds
    """
    # Randomly decide if this is a normal reading or an emergency
    is_emergency = random.random() < 0.3  # 30% chance of emergency scenario
    
    if is_emergency:
        # Simulate a fall: person lying down with no movement for extended period
        movement = "none"
        posture = "lying"
        time_on_ground = random.randint(21, 60)  # More than 20 seconds
    else:
        # Normal activity
        movement = random.choice(["none", "low", "high"])
        posture = random.choice(["standing", "sitting"])
        time_on_ground = random.randint(0, 10)
    
    return {
        "movement": movement,
        "posture": posture,
        "time_on_ground": time_on_ground,
    }




def detect_emergency(sensor_data):
    """
    Determine if sensor data indicates an emergency.
    
    Emergency detected when:
    - Posture == "lying"
    - Movement == "none"
    - Time on ground > 20 seconds
    
    Args:
        sensor_data (dict): Dictionary containing sensor readings
        
    Returns:
        tuple: (is_emergency: bool, status: str)
    """
    is_fall = (
        sensor_data["posture"] == "lying"
        and sensor_data["movement"] == "none"
        and sensor_data["time_on_ground"] > 20
    )
    
    if is_fall:
        return True, "Fall Detected"
    return False, "Safe"


@detection_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Agent startup event handler.
    Displays initialization information.
    """
    print("\n" + "="*50)
    print("👴 Emergency Detection Agent Started")
    print("="*50)
    print(f"Agent Address: {detection_agent.address}")
    print(f"Response Agent: {RESPONSE_AGENT_ADDRESS}")
    print()
    print("Starting continuous monitoring...")
    print("(Reading sensor data every 8 seconds)")
    print("="*50 + "\n")
    
    ctx.logger.info("Detection Agent startup sequence initiated")


@detection_agent.on_interval(period=8.0)
async def monitor(ctx: Context):
    """
    Interval-based monitoring that simulates sensor readings.
    Runs every 8 seconds to check for emergencies.
    Reads simulated sensor data, detects falls, and sends alerts to Response Agent.
    """
    # Simulate reading sensor data
    sensor_data = simulate_sensor_data()
    is_emergency, status = detect_emergency(sensor_data)
    
    # Format timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Print sensor reading
    print(f"\n--- Sensor Reading ---")
    print(f"Movement: {sensor_data['movement']}")
    print(f"Posture: {sensor_data['posture']}")
    print(f"Time on ground: {sensor_data['time_on_ground']} seconds")
    
    # Determine risk level
    if is_emergency:
        risk_level = "HIGH"
        print(f"⚠️  Emergency detected!")
        print(f"Sending alert to Response Agent...")
    else:
        risk_level = "LOW"
        print(f"✓ Status: Safe")
    
    # Create alert message using Pydantic model
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
    
    # Send alert to Response Agent
    try:
        await ctx.send(RESPONSE_AGENT_ADDRESS, alert)
        if is_emergency:
            print(f"✓ Alert sent successfully!")
    except Exception as e:
        if is_emergency:
            ctx.logger.warning(f"Failed to send emergency alert: {str(e)}")
            print(f"⚠️  Could not send alert. Is Response Agent running?")
        else:
            ctx.logger.debug(f"Could not send status update: {str(e)}")
    
    print(f"Waiting for next reading...")


if __name__ == "__main__":
    # Run the detection agent
    # The agent will continuously run the monitor() interval task
    detection_agent.run()

