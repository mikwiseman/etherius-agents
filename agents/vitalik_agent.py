import os
import sys
import requests
from dotenv import load_dotenv
from uagents import Agent, Context, Model

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Etherius agent address (to send responses back)
ETHERIUS_ADDRESS = "agent1q0vk6hezvvd89rwy0hdzaw2kertckqa40rae4a03jpsgvkye0dw8qyw3n7m"

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
    
    # Process message with ChatGPT
    if OPENAI_API_KEY:
        try:
            ctx.logger.info("Processing message with ChatGPT...")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": """You are Vitalik Buterin. Based on the user's input, suggest a specific NFT search query.
                     Start your response with 'Find' and mention a specific NFT collection or search.
                     Examples:
                     - "Find CryptoPunks with zombie traits"
                     - "Find Bored Apes under 10 ETH"
                     - "Find trending collections on Base"
                     - "Find Pudgy Penguins floor price"
                     - "Find latest Art Blocks drops"
                     Be specific and actionable, always starting with 'Find'."""},
                    {"role": "user", "content": msg.message}
                ]
            }
            
            response = requests.post(OPENAI_API_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                gpt_response = response.json()['choices'][0]['message']['content']
                ctx.logger.info(f"GPT Response: {gpt_response}")
                
                # Send response back to etherius
                response_msg = BroadcastMessage(
                    message=f"Vitalik's thoughts: {gpt_response}",
                    original_sender="vitalik_gpt"
                )
                
                await ctx.send(ETHERIUS_ADDRESS, response_msg)
                ctx.logger.info("Response sent back to Etherius")
            else:
                ctx.logger.error(f"ChatGPT API error: {response.status_code} - {response.text}")
        except Exception as e:
            ctx.logger.error(f"Error processing with ChatGPT: {e}")
    else:
        ctx.logger.warning("OpenAI API key not configured")

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