import os
import sys
import requests
import re
from dotenv import load_dotenv
from uagents import Agent, Context, Model

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Etherius agent address (to send image URLs back)
ETHERIUS_ADDRESS = "agent1q0vk6hezvvd89rwy0hdzaw2kertckqa40rae4a03jpsgvkye0dw8qyw3n7m"

class BroadcastMessage(Model):
    message: str
    original_sender: str

class ImageUrlMessage(Model):
    image_url: str
    source: str

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
    
    # Only process messages from etherius_parsed
    if msg.original_sender != "etherius_parsed":
        ctx.logger.info("Ignoring non-parsed message")
        return
    
    # Extract NFT image URL using GPT
    if OPENAI_API_KEY:
        try:
            ctx.logger.info("Extracting NFT image URL with GPT...")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": """Extract exactly ONE NFT image URL from the text"""},
                    {"role": "user", "content": msg.message}
                ]
            }
            
            response = requests.post(OPENAI_API_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                image_url = response.json()['choices'][0]['message']['content'].strip()
                
                # Validate it looks like a URL
                if image_url and (image_url.startswith('http') or image_url.startswith('ipfs://')):
                    ctx.logger.info(f"Found NFT image URL: {image_url}")
                    
                    # Send image URL back to Etherius
                    image_msg = ImageUrlMessage(
                        image_url=image_url,
                        source="tv_agent"
                    )
                    
                    await ctx.send(ETHERIUS_ADDRESS, image_msg)
                    ctx.logger.info(f"Image URL sent back to Etherius:{image_url}")
                else:
                    ctx.logger.info(f"No valid image URL found in message:{image_url}")
            else:
                ctx.logger.error(f"GPT API error: {response.status_code} - {response.text}")
        except Exception as e:
            ctx.logger.error(f"Error extracting image URL: {e}")
    else:
        ctx.logger.warning("OpenAI API key not configured")

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