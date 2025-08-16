import os
import sys
import json
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from uagents import Agent, Context, Model
import openai

# Ensure parent directory is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Agent configuration
agent = Agent(
    name="etherius_agent_mik2025",
    seed="etherius_agent_mik_2025",
    port=int(os.getenv("ETHERIUS_PORT", 8100)),
    endpoint=[f"http://localhost:{os.getenv('ETHERIUS_PORT', 8100)}/submit"],
    mailbox=True,
    publish_agent_details=True,
    readme_path = "README.md"
)

openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simple Models
class ChatRequest(Model):
    message: str

class ChatResponse(Model):
    response: str


class SimpleOpenSeaMCP:
    """Minimal MCP client that uses GPT-4o for request/response handling"""
    
    def __init__(self, ctx: Context):
        self._ctx = ctx
        self.access_token = os.getenv("OPENSEA_MCP_TOKEN", "")
        self.base_url = "https://mcp.opensea.io/mcp"
        self.session_id = None
        self._initialized = False
        
        if not self.access_token:
            self._ctx.logger.warning("⚠️ OPENSEA_MCP_TOKEN not found. Set it in .env file.")
    
    async def initialize(self) -> bool:
        """Initialize MCP session"""
        if self._initialized:
            return True
            
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "etherius-simple", "version": "2.0"}
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(self.base_url, headers=headers, json=init_request)
                if resp.status_code == 200:
                    session_id = resp.headers.get("Mcp-Session-Id")
                    if session_id:
                        self.session_id = session_id
                    self._initialized = True
                    self._ctx.logger.info("✅ OpenSea MCP initialized")
                    return True
                else:
                    self._ctx.logger.error(f"Failed to initialize: {resp.status_code}")
                    return False
        except Exception as e:
            self._ctx.logger.error(f"Init error: {e}")
            return False
    
    async def query_with_gpt(self, user_query: str) -> str:
        """Use GPT-4o to generate MCP request, execute it, and parse response"""
        
        if not self.access_token:
            return "⚠️ OpenSea MCP token required. Set OPENSEA_MCP_TOKEN in your .env file."
        
        if not await self.initialize():
            return "Failed to initialize OpenSea MCP session."
        
        # Step 1: Use GPT-4o to determine the right MCP tool and arguments
        tool_prompt = f"""You are an NFT expert helping query OpenSea's MCP API.
        
User Query: "{user_query}"

Available OpenSea MCP tools:
1. search_collections - Search for NFT collections
   Args: query (string), limit (number, default 10), chain (optional: ethereum/polygon/base/solana)
   
2. get_collection - Get detailed info about a specific collection
   Args: slug (string - the collection identifier), includes (array of: analytics/offers/holders/activity/items/attributes)
   
3. get_trending_collections - Get trending collections
   Args: timeframe (ONE_HOUR/ONE_DAY/SEVEN_DAYS/THIRTY_DAYS), limit (number), chain (optional)
   
4. get_top_collections - Get top collections
   Args: sortBy (REQUIRED - one of: FLOOR_PRICE, ONE_DAY_VOLUME, ONE_DAY_SALES, VOLUME, SALES), limit (number, default 10), chain (optional)

Based on the user's query, respond with ONLY a JSON object with the tool name and arguments.
Example: {{"tool": "search_collections", "args": {{"query": "pudgy penguins", "limit": 5}}}}
"""

        try:
            # Get GPT-4o to generate the MCP request
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You generate OpenSea MCP API requests. Respond only with valid JSON!!, no ```, no markdown or extra text."},
                    {"role": "user", "content": tool_prompt}
                ]
            )
            
            # Clean up response content (remove markdown if present)
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                # Remove markdown code blocks
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            tool_request = json.loads(content)
            tool_name = tool_request.get("tool")
            tool_args = tool_request.get("args", {})
            
            # Fix parameter names for OpenSea MCP compatibility
            if "sort_by" in tool_args:
                tool_args["sortBy"] = tool_args.pop("sort_by")
            
            self._ctx.logger.info(f"🤖 GPT-4o selected: {tool_name} with args: {tool_args}")
            
            # Step 2: Execute the MCP request
            mcp_result = await self._execute_mcp_call(tool_name, tool_args)
            
            # Step 3: Use GPT-4o to parse and format the response
            if "error" in mcp_result:
                return f"❌ Error: {mcp_result['error']}"
            
            parse_prompt = f"""You are an NFT expert. Parse this OpenSea MCP response and provide a clear, concise summary for the user.

User's original question: "{user_query}"
MCP Tool Used: {tool_name}
Raw Response: {json.dumps(mcp_result, indent=2)}

Provide a friendly, informative response with:
- Key collection names and stats (floor price, volume, etc.)
- Format numbers nicely (e.g., 2.5 ETH, 1,234 sales)
- Include OpenSea links where relevant
- Use bullet points or a simple table format
- Keep it concise but informative
"""

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You parse NFT data and provide clear summaries."},
                    {"role": "user", "content": parse_prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except json.JSONDecodeError as e:
            return f"Failed to parse GPT response: {e}"
        except Exception as e:
            self._ctx.logger.error(f"Error in GPT query: {e}")
            return f"Error processing request: {str(e)}"
    
    async def _execute_mcp_call(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an OpenSea MCP tool call"""
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": args}
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(self.base_url, headers=headers, json=request)
                
                if resp.status_code == 200:
                    # Handle SSE response
                    content_type = resp.headers.get("content-type", "").lower()
                    
                    if "text/event-stream" in content_type:
                        # Parse SSE format
                        text = resp.text
                        for message in text.split('\n\n'):
                            for line in message.split('\n'):
                                if line.startswith('data:'):
                                    try:
                                        data = json.loads(line[5:].strip())
                                        if "result" in data:
                                            return data["result"]
                                        elif "error" in data:
                                            return {"error": data["error"]}
                                    except:
                                        continue
                        return {"error": "No valid data in SSE response"}
                    else:
                        # Regular JSON response
                        data = resp.json()
                        if "result" in data:
                            return data["result"]
                        elif "error" in data:
                            return {"error": data["error"]}
                        return {"error": "Invalid response format"}
                else:
                    return {"error": f"HTTP {resp.status_code}"}
                    
        except Exception as e:
            return {"error": str(e)}

# ────────────────────────────────────────────────────────────────────────────────
# Agent Lifecycle
# ────────────────────────────────────────────────────────────────────────────────

mcp_client: Optional[SimpleOpenSeaMCP] = None

@agent.on_event("startup")
async def startup(ctx: Context):
    global mcp_client
    ctx.logger.info("🌟 Simplified Etherius Agent Starting")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info("🤖 Using GPT-4o for intelligent NFT queries")
    mcp_client = SimpleOpenSeaMCP(ctx)
    ctx.logger.info("✨ Ready!")

@agent.on_rest_post("/chat", ChatRequest, ChatResponse)
async def chat_endpoint(ctx: Context, req: ChatRequest) -> ChatResponse:
    """Chat endpoint that uses GPT-4o to handle all OpenSea queries"""
    ctx.logger.info(f"💬 Chat: {req.message}")
    
    if not mcp_client:
        return ChatResponse(response="Agent not initialized. Please restart.")
    
    response = await mcp_client.query_with_gpt(req.message)
    return ChatResponse(response=response)

@agent.on_rest_get("/health", ChatResponse)
async def health_check(ctx: Context) -> ChatResponse:
    return ChatResponse(response="Simplified Etherius agent is healthy!")

if __name__ == "__main__":
    print("""
🌟 Simplified Etherius Agent - GPT-4o Powered NFT Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Natural language NFT queries via GPT-4o
• Automatic OpenSea MCP request generation
• Intelligent response parsing and formatting
• REST API: POST /chat {"message": "your question"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()