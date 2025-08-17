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

# Agent addresses
ETHERIUS_ADDRESS = "agent1q0vk6hezvvd89rwy0hdzaw2kertckqa40rae4a03jpsgvkye0dw8qyw3n7m"
KATRIK_ADDRESS = "agent1qw5tlakv4cqc8jztkksfz5rlkld74v0dcnkl46tcuvyrxwk9s6dzwryk9lf"

class BroadcastMessage(Model):
    message: str
    original_sender: str

class IdeaQuestion(Model):
    question: str
    original_message: str

class IdeaResponse(Model):
    response: str

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
    
    # Only process messages from user (not from other agents)
    if msg.original_sender != "user":
        ctx.logger.info("Ignoring non-user message")
        return
    
    # Phase 1: Generate strategic question with ChatGPT
    if OPENAI_API_KEY:
        try:
            ctx.logger.info("Phase 1: Generating strategic question...")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            # Generate question
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": """You are Vitalik Buterin having a casual discussion. 
                     Ask Katrik ONE short question about the NFT idea (max 15 words).
                     Be conversational, like talking to a friend. No formal analysis."""},
                    {"role": "user", "content": msg.message}
                ]
            }
            
            response = requests.post(OPENAI_API_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                question = response.json()['choices'][0]['message']['content']
                ctx.logger.info(f"Generated question: {question}")
                
                # Small delay before broadcasting (thinking time)
                await asyncio.sleep(2)
                
                # Broadcast question to Etherius for display
                broadcast_msg = BroadcastMessage(
                    message=question,
                    original_sender="vitalik"
                )
                await ctx.send(ETHERIUS_ADDRESS, broadcast_msg)
                
                # Small delay before sending to Katrik
                await asyncio.sleep(1)
                
                # Send question to Katrik and wait for response
                ctx.logger.info("Sending question to Katrik and waiting for response...")
                idea_question = IdeaQuestion(
                    question=question,
                    original_message=msg.message
                )
                
                katrik_response, status = await ctx.send_and_receive(
                    KATRIK_ADDRESS,
                    idea_question,
                    response_type=IdeaResponse,
                    timeout=30  # 30 second timeout
                )
                
                if isinstance(katrik_response, IdeaResponse):
                    ctx.logger.info(f"Received response from Katrik: {katrik_response.response}")
                    
                    # Phase 3: Synthesize final strategy
                    ctx.logger.info("Phase 3: Synthesizing final strategy...")
                    
                    data = {
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": """You are Vitalik Buterin finishing a casual discussion with Katrik.
                             Give your final take on the NFT idea (max 20 words).
                             Be conversational and decisive, like concluding a chat with a friend."""},
                            {"role": "user", "content": f"User wanted: {msg.message}\n\nYou asked: {question}\n\nKatrik said: {katrik_response.response}"}
                        ]
                    }
                    
                    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
                    
                    if response.status_code == 200:
                        final_strategy = response.json()['choices'][0]['message']['content']
                        ctx.logger.info(f"Final strategy: {final_strategy}")
                        
                        # Small delay before final response
                        await asyncio.sleep(2)
                        
                        # Broadcast final strategy to Etherius
                        final_msg = BroadcastMessage(
                            message=final_strategy,
                            original_sender="vitalik"
                        )
                        await ctx.send(ETHERIUS_ADDRESS, final_msg)
                        ctx.logger.info("Final strategy sent to Etherius")
                    else:
                        ctx.logger.error(f"ChatGPT API error in phase 3: {response.status_code}")
                else:
                    ctx.logger.error(f"Failed to receive response from Katrik: {status}")
            else:
                ctx.logger.error(f"ChatGPT API error in phase 1: {response.status_code}")
        except Exception as e:
            ctx.logger.error(f"Error in collaborative process: {e}")
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