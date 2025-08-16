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
    name="tv_agent",
    seed="tv_agent_seed_2025",
    port=int(os.getenv("TV_PORT", 8203)),
    endpoint=[f"http://localhost:{os.getenv('TV_PORT', 8203)}/submit"],
    mailbox=True,
    publish_agent_details=True
)

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"TV Agent started with address: {agent.address}")
    ctx.logger.info(f"Listening on port: {os.getenv('TV_PORT', 8203)}")

@agent.on_message(model=BroadcastMessage)
async def handle_broadcast(ctx: Context, sender: str, msg: BroadcastMessage):
    ctx.logger.info(f"TV received broadcast from {sender}")
    ctx.logger.info(f"Original sender: {msg.original_sender}")
    ctx.logger.info(f"Message: {msg.message}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("TV Agent shutting down")

if __name__ == "__main__":
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TV Agent - Broadcast Message Receiver
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Receives broadcast messages from Etherius Agent
• Listens on port 8203
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()