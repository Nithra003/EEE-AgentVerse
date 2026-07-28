"""
Emergency Response Agent for Elder Care System
- Receives emergency alerts from the Detection Agent
- Processes and displays emergency information
- Notifies emergency contacts and ambulance services
"""

import asyncio
from datetime import datetime
from uagents import Agent, Context, Model


# Define the EmergencyAlert message model (must match Detection Agent)
class EmergencyAlert(Model):
    """
    Message model for emergency alerts received from Detection Agent.
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


# Create the Emergency Response Agent
response_agent = Agent(
    name="emergency_response_agent",
    seed="emergency_response_agent_secret_seed",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Store the response agent address
RESPONSE_AGENT_ADDRESS = response_agent.address


def format_emergency_notification(alert: EmergencyAlert) -> str:
    """
    Format the emergency alert into a readable notification message.
    
    Args:
        alert (EmergencyAlert): The emergency alert message
        
    Returns:
        str: Formatted emergency notification
    """
    notification = f"""
==================================
🚨 EMERGENCY ALERT
==================================
Person     : {alert.person_name}
Status     : {alert.status}
Location   : {alert.location}
Risk Level : {alert.risk_level}
Time       : {alert.timestamp}
----------------------------------
Sensor Data:
  Movement      : {alert.movement}
  Posture       : {alert.posture}
  Time on Ground: {alert.time_on_ground}s
==================================
"""
    return notification


def call_emergency_services():
    """
    Simulate calling emergency services.
    In a real system, this would integrate with actual emergency services APIs.
    """
    print("Calling emergency contacts...")
    print("📞 Emergency Contact #1: Jane Doe (Daughter)")
    print("📞 Emergency Contact #2: St. Mary's Hospital")
    print()
    print("🚑 Ambulance notified.")
    print("🚑 Estimated arrival: 8 minutes")
    print()


@response_agent.on_message(model=EmergencyAlert)
async def handle_emergency_alert(ctx: Context, sender: str, msg: EmergencyAlert):
    """
    Handle incoming emergency alerts from the Detection Agent.
    
    This is the main message handler that:
    1. Receives the alert
    2. Formats and displays it
    3. Initiates emergency response procedures
    4. Logs the incident
    
    Args:
        ctx (Context): Agent context
        sender (str): Address of the sending agent
        msg (EmergencyAlert): The emergency alert message
    """
    # Log the incoming message
    ctx.logger.info(f"Emergency alert received from {sender}")
    
    # Display the formatted emergency notification
    print(format_emergency_notification(msg))
    
    # Take action based on alert type
    if msg.status == "Fall Detected":
        print("⚠️  FALL DETECTED - INITIATING EMERGENCY PROTOCOL")
        print()
        
        # Call emergency services
        call_emergency_services()
        
        # Log incident
        ctx.logger.warning(f"EMERGENCY: {msg.person_name} - {msg.status} at {msg.location}")
        print("📋 Incident logged and recorded.")
        print()
    else:
        # Safe status
        print("✓ Status: Normal - No emergency response required.")
        ctx.logger.info(f"Normal update from {msg.person_name}")
    
    print("==================================")
    print()


@response_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Agent startup event handler.
    Displays initialization information and registers the agent.
    """
    print("\n" + "="*50)
    print("🏥 Emergency Response Agent Started")
    print("="*50)
    print(f"Agent Address: {response_agent.address}")
    print()
    print("To connect Detection Agent, set environment variable:")
    print(f'  SET RESPONSE_AGENT_ADDRESS={response_agent.address}')
    print("Or pass this address to detection_agent.py")
    print()
    print("Listening for emergency alerts...")
    print("="*50 + "\n")
    
    ctx.logger.info("Response Agent startup sequence completed")


@response_agent.on_interval(period=30.0)
async def health_check(ctx: Context):
    """
    Periodic health check to ensure the Response Agent is operational.
    Runs every 30 seconds.
    """
    ctx.logger.info("Response Agent is operational and ready to receive alerts")


if __name__ == "__main__":
    # Run the response agent
    response_agent.run()
