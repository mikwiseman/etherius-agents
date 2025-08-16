import os
import sys
from dotenv import load_dotenv
from uagents import Agent, Context, Model

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

class BroadcastMessage(Model):
    message: str
    original_sender: str

agent = Agent(
    name="vitalik_agent",
    seed="vitalik_agent_seed_2025",
    port=8232,
    endpoint=[f"http://localhost:8232/submit"]
)

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Vitalik Agent started with address: {agent.address}")
    ctx.logger.info(f"Listening on port: {os.getenv('VITALIK_PORT', 8202)}")

@agent.on_message(model=BroadcastMessage)
async def handle_broadcast(ctx: Context, sender: str, msg: BroadcastMessage):
    ctx.logger.info(f"Vitalik received broadcast from {sender}")
    ctx.logger.info(f"Original sender: {msg.original_sender}")
    ctx.logger.info(f"Message: {msg.message}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("Vitalik Agent shutting down")

if __name__ == "__main__":
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Vitalik Agent - Broadcast Message Receiver
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Receives broadcast messages from Etherius Agent
• Listens on port 8232
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()