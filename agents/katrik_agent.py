import os
import sys
import requests
import asyncio
from dotenv import load_dotenv
from uagents import Agent, Context, Model

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Etherius agent address (to broadcast messages)
ETHERIUS_ADDRESS = "agent1q0vk6hezvvd89rwy0hdzaw2kertckqa40rae4a03jpsgvkye0dw8qyw3n7m"

class BroadcastMessage(Model):
    message: str
    original_sender: str

class IdeaQuestion(Model):
    question: str
    original_message: str

class IdeaResponse(Model):
    response: str

agent = Agent(
    name="katrik_agent",
    seed="katrik_agent_seed_2025",
    port=8222,
    endpoint=[f"http://localhost:8222/submit"]
)

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Katrik Agent started with address: {agent.address}")
    ctx.logger.info(f"Listening on port: 8222")

@agent.on_message(model=IdeaQuestion, replies=IdeaResponse)
async def handle_idea_question(ctx: Context, sender: str, msg: IdeaQuestion):
    ctx.logger.info(f"Katrik received question from Vitalik: {msg.question}")
    ctx.logger.info(f"Original message: {msg.original_message}")
    
    # Phase 2: Analyze with OpenAI as NFT market analyst
    if OPENAI_API_KEY:
        try:
            ctx.logger.info("Phase 2: Analyzing as NFT market analyst...")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": """You are Katrik, an NFT enthusiast having a casual discussion with Vitalik.
                     Respond to his question naturally (max 20 words).
                     Be conversational, like chatting with a friend about NFTs."""},
                    {"role": "user", "content": f"Context: User wants {msg.original_message}\n\nVitalik asks: {msg.question}"}
                ]
            }
            
            response = requests.post(OPENAI_API_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                analysis = response.json()['choices'][0]['message']['content']
                ctx.logger.info(f"Market analysis: {analysis}")
                
                # Small delay before responding (thinking time)
                await asyncio.sleep(2)
                
                # Broadcast analysis to Etherius for display
                broadcast_msg = BroadcastMessage(
                    message=analysis,
                    original_sender="katrik"
                )
                await ctx.send(ETHERIUS_ADDRESS, broadcast_msg)
                ctx.logger.info("Analysis broadcast to Etherius")
                
                # Send response back to Vitalik
                response_msg = IdeaResponse(response=analysis)
                await ctx.send(sender, response_msg)
                ctx.logger.info("Response sent back to Vitalik")
            else:
                ctx.logger.error(f"ChatGPT API error: {response.status_code} - {response.text}")
                # Send error response
                error_msg = IdeaResponse(response="Unable to analyze at this time.")
                await ctx.send(sender, error_msg)
        except Exception as e:
            ctx.logger.error(f"Error processing with ChatGPT: {e}")
            # Send error response
            error_msg = IdeaResponse(response="Error occurred during analysis.")
            await ctx.send(sender, error_msg)
    else:
        ctx.logger.warning("OpenAI API key not configured")
        # Send error response
        error_msg = IdeaResponse(response="OpenAI API not configured.")
        await ctx.send(sender, error_msg)

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("Katrik Agent shutting down")

if __name__ == "__main__":
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Katrik Agent - Broadcast Message Receiver
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Receives broadcast messages from Etherius Agent
• Listens on port 8222
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()