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
        tool_prompt = f"""
You are a tool router for OpenSea MCP. Choose exactly ONE tool and the minimal, valid arguments to satisfy the user's request.
Return ONLY a JSON object with keys "tool" and "args". No markdown, no code fences, no extra text.

USER QUERY:
"{user_query}"

ALLOWED TOOLS:
- "search" — AI-powered marketplace search
- "fetch" — Fetch full details for an entity by id
- "search_collections"
- "get_collection" — includes: analytics, offers, holders, activity, items, attributes
- "search_items"
- "get_item" — includes: activity, offers, owners, analytics
- "search_tokens"
- "get_token" — includes: priceHistory, activity, ohlcv
- "get_token_swap_quote"
- "get_token_balances"
- "get_token_balance"
- "get_nft_balances"
- "get_profile" — includes: items, collections, activity, listings, offers, balances, favorites
- "get_top_tokens"
- "get_trending_tokens"
- "get_top_collections"
- "get_trending_collections"

ARGUMENT RULES:
- Chains: normalize to one of {{ "ethereum","polygon","base","solana" }}.
  Aliases → canonical: eth|mainnet→ethereum; matic→polygon; sol→solana.
- Timeframes: ONE_HOUR | ONE_DAY | SEVEN_DAYS | THIRTY_DAYS.
- get_top_collections.sortBy: FLOOR_PRICE | ONE_DAY_VOLUME | ONE_DAY_SALES | VOLUME | SALES.
- Use only relevant args (query, slug, address, symbol, contract, tokenId, limit, chain, includes, fromToken, toToken, amount).
- Never invent parameters. Omit null/empty values. Keep args minimal and correct.

OUTPUT (examples; adapt to the user query):
{{"tool":"search_collections","args":{{"query":"pudgy penguins","limit":5,"chain":"ethereum"}}}}
{{"tool":"get_collection","args":{{"slug":"boredapeyachtclub","includes":["analytics","items"]}}}}
{{"tool":"get_trending_collections","args":{{"timeframe":"ONE_DAY","limit":10}}}}
{{"tool":"get_top_collections","args":{{"sortBy":"ONE_DAY_VOLUME","limit":10,"chain":"ethereum"}}}}
{{"tool":"get_profile","args":{{"address":"vitalik.eth"}}}}
{{"tool":"get_token","args":{{"symbol":"USDC","chain":"ethereum"}}}}
{{"tool":"get_token_swap_quote","args":{{"fromToken":"ETH","toToken":"USDC","amount":"0.40","chain":"ethereum"}}}}
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
            
            parse_prompt = f"""
You are an NFT & token analyst. Read the OpenSea MCP response and write a concise, factual summary.

USER QUESTION:
{user_query}

MCP TOOL USED:
{tool_name}

RAW RESPONSE (JSON):
{json.dumps(mcp_result, indent=2)}

GUIDELINES:
- If the tool returned collections: include name, slug, chain, floor price, 1d/7d volume/sales if present, supply/owners if present. Note trend arrows (↑/↓) only if explicit in data.
- If it returned items: include collection, tokenId, current listing or last sale, 2–3 notable traits (with rarity if present), owner or owner count if provided.
- If it returned a profile or balances: show token holdings (symbol + balance + any USD fields provided), NFT count, top collections, and recent activity if present.
- If it returned tokens: show symbol/name, price and % change (1d/7d) if present, chain if relevant.
- If it returned a swap quote: show expectedOut, minimumReceived (if present), gas estimate, and (only if also provided in the response or question) whether it is enough to buy the referenced floor.
- Numbers: format like "2.45 ETH", "1,234 sales", "$12,340". If a field is missing, output "—".
- Links: when identifiers exist, include OpenSea links:
  • Collection → https://opensea.io/collection/{{slug}}
  • Item → https://opensea.io/assets/{{chain}}/{{contract}}/{{tokenId}}
  • Profile → https://opensea.io/{{address_or_ens}}
- Be crisp and use bullet points or a compact table. Do not invent data. If there was an error field, mention it briefly and provide a next step.

END WITH:
- 2–3 suggested next actions tailored to the result (e.g., "Show 24h trending on Polygon", "List 5 cheapest items under 0.1 ETH", "Quote 0.2 ETH→USDC on Base").

OUTPUT:
Plain text only. No JSON. No code fences.
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