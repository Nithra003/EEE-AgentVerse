"""
Emergency Response Agent for Elder Care System
"""

from uagents import Agent, Context, Model


class EmergencyAlert(Model):
    person_name: str
    status: str
    location: str
    risk_level: str
    timestamp: str
    movement: str
    posture: str
    time_on_ground: int


response_agent = Agent(
    name="emergency_response_agent",
    seed="emergency_response_agent_secret_seed",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"],
)

RESPONSE_AGENT_ADDRESS = response_agent.address


def format_emergency_notification(alert: EmergencyAlert) -> str:
    return (
        f"\n=================================="
        f"\nEMERGENCY ALERT"
        f"\n=================================="
        f"\nPerson     : {alert.person_name}"
        f"\nStatus     : {alert.status}"
        f"\nLocation   : {alert.location}"
        f"\nRisk Level : {alert.risk_level}"
        f"\nTime       : {alert.timestamp}"
        f"\n----------------------------------"
        f"\nSensor Data:"
        f"\n  Movement      : {alert.movement}"
        f"\n  Posture       : {alert.posture}"
        f"\n  Time on Ground: {alert.time_on_ground}s"
        f"\n=================================="
    )


def call_emergency_services():
    print("Calling emergency contacts...")
    print("Emergency Contact #1: Jane Doe (Daughter)")
    print("Emergency Contact #2: St. Mary's Hospital")
    print()
    print("Ambulance notified.")
    print("Estimated arrival: 8 minutes")
    print()


@response_agent.on_message(model=EmergencyAlert)
async def handle_emergency_alert(ctx: Context, sender: str, msg: EmergencyAlert):
    ctx.logger.info(f"Emergency alert received from {sender}")
    print(format_emergency_notification(msg))

    if msg.status == "Fall Detected":
        print("FALL DETECTED - INITIATING EMERGENCY PROTOCOL")
        print()
        call_emergency_services()
        ctx.logger.warning(f"EMERGENCY: {msg.person_name} - {msg.status} at {msg.location}")
        print("Incident logged and recorded.")
        print()
    else:
        print("Status: Normal - No emergency response required.")
        ctx.logger.info(f"Normal update from {msg.person_name}")

    print("==================================")
    print()


@response_agent.on_event("startup")
async def startup(ctx: Context):
    print("\n" + "="*50)
    print("Emergency Response Agent Started")
    print("="*50)
    print(f"Agent Address: {response_agent.address}")
    print()
    print("Listening for emergency alerts...")
    print("="*50 + "\n")
    ctx.logger.info("Response Agent startup sequence completed")


@response_agent.on_interval(period=30.0)
async def health_check(ctx: Context):
    ctx.logger.info("Response Agent is operational and ready to receive alerts")


if __name__ == "__main__":
    response_agent.run()
