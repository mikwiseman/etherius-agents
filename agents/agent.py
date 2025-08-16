import os
from enum import Enum
from dotenv import load_dotenv

from uagents import Agent, Context, Model
from uagents.experimental.quota import QuotaProtocol, RateLimit
from uagents_core.models import ErrorMessage

# Load environment variables
load_dotenv()

# Import chat protocols
from chat_proto import chat_proto, struct_output_client_proto
from nft_service import get_nft_info, NFTQueryRequest, NFTQueryResponse

# Create the agent with chat protocol support
agent = Agent(
    name="etherius_chat_agent_mik2025",
    seed="etherius_chat_agent_mik_2025",
    port=int(os.getenv("CHAT_AGENT_PORT", 8101)),
    mailbox=True
)


# Create the main protocol with rate limiting
proto = QuotaProtocol(
    storage_reference=agent.storage,
    name="NFT-Intelligence-Protocol",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=60, max_requests=30),
)

@proto.on_message(
    NFTQueryRequest, replies={NFTQueryResponse, ErrorMessage}
)
async def handle_request(ctx: Context, sender: str, msg: NFTQueryRequest):
    """Handle direct NFT query requests from other agents"""
    ctx.logger.info(f"Received NFT query request: {msg.query}")
    try:
        results = await get_nft_info(msg.query)
        ctx.logger.info(f'printing results in function {results}')
        ctx.logger.info("Successfully fetched NFT information")
        await ctx.send(sender, NFTQueryResponse(results=results))
    except Exception as err:
        ctx.logger.error(err)
        await ctx.send(sender, ErrorMessage(error=str(err)))

agent.include(proto, publish_manifest=True)

### Health check protocol
def agent_is_healthy() -> bool:
    """
    Check if the agent can connect to OpenSea MCP
    """
    try:
        import asyncio
        asyncio.run(get_nft_info("test"))
        return True
    except Exception:
        return False

class HealthCheck(Model):
    pass

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class AgentHealth(Model):
    agent_name: str
    status: HealthStatus

health_protocol = QuotaProtocol(
    storage_reference=agent.storage, name="HealthProtocol", version="0.1.0"
)

@health_protocol.on_message(HealthCheck, replies={AgentHealth})
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    status = HealthStatus.UNHEALTHY
    try:
        if agent_is_healthy():
            status = HealthStatus.HEALTHY
    except Exception as err:
        ctx.logger.error(err)
    finally:
        await ctx.send(sender, AgentHealth(agent_name="etherius_chat_agent", status=status))

# Include all protocols
agent.include(health_protocol, publish_manifest=True)
agent.include(chat_proto, publish_manifest=True)
agent.include(struct_output_client_proto, publish_manifest=True)


if __name__ == "__main__":
    print("""
🌟 Etherius Chat Agent - ASI1 LLM Compatible NFT Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Chat protocol enabled for ASI1 LLM integration
• Natural language NFT queries via GPT-4o
• Automatic OpenSea MCP request generation
• Rate limiting: 30 requests per hour
• Port: 8101 (configurable via CHAT_AGENT_PORT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    print(f"📍 Agent Address: {agent.address}")
    print("✨ Starting agent...\n")
    agent.run()