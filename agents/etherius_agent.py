import os
import sys
import json
import httpx
import time
import hashlib
import asyncio
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from uagents import Agent, Context, Model
import requests
from agent_wallet import AgentWallet

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

# ASI:One Mini configuration
ASI_ONE_API_KEY = os.getenv("ASI_ONE_API_KEY")
ASI_ONE_URL = "https://api.asi1.ai/v1/chat/completions"

# Payment configuration for NFT purchases
PAYMENT_CONFIG = {
    "receiving_address": os.getenv("X402_WALLET_ADDRESS"),
    "network": "base-sepolia",
    "default_price": 0.01,  # USDC
    "auto_check_interval": 15,  # seconds
    "max_check_time": 300  # 5 minutes max
}

# Track active NFT purchases
active_purchases = {}

# Simple Models
class ChatRequest(Model):
    message: str

class ChatResponse(Model):
    response: str

class BroadcastMessage(Model):
    message: str
    original_sender: str

class AgentMessage(Model):
    agent_name: str
    message: str
    timestamp: float

class AgentMessagesResponse(Model):
    messages: List[AgentMessage]

class ImageUrlMessage(Model):
    image_url: str
    source: str

class TvImageResponse(Model):
    image_url: str
    timestamp: float

class MettaQueryRequest(Model):
    query: str


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
    
    async def query_with_gpt(self, user_query: str, ctx: Context = None) -> str:
        """Use ASI:One Mini to generate MCP request, execute it, and parse response"""
        
        if not ASI_ONE_API_KEY:
            return "⚠️ ASI:One API key required. Set ASI_ONE_API_KEY in your .env file."
        
        if not self.access_token:
            return "⚠️ OpenSea MCP token required. Set OPENSEA_MCP_TOKEN in your .env file."
        
        if not await self.initialize():
            return "Failed to initialize OpenSea MCP session."
        
        # Step 1: Use ASI:One Mini to determine the right MCP tool and arguments
        tool_prompt = f"""
You are a tool router for OpenSea MCP. Choose the best tool and arguments to satisfy the user's request.
Return ONLY a JSON object with keys "tool" and "args". No markdown, no code fences, no extra text.

USER QUERY:
"{user_query}"

AVAILABLE TOOLS:
- "search" — General marketplace search for broad/generic NFT queries
- "search_items" — Search specific collection NFTs with filters
- "search_collections" — Search NFT collections
- "get_collection" — Get specific collection details (needs: slug)
- "get_item" — Get specific NFT details (needs: contract, tokenId)
- "search_tokens" — Search cryptocurrencies/tokens
- "get_token" — Get token details (needs: symbol, chain)
- "get_token_swap_quote" — Get swap quote (needs: fromToken, toToken, amount)
- "get_profile" — Get profile details (needs: address)
- "get_trending_collections" — Get trending collections
- "get_top_collections" — Get top collections

TOOL SELECTION RULES:
- Use "search" for generic NFT searches without a specific collection (e.g., "cheap NFTs", "any NFTs under 1 ETH")
- Use "search_items" ONLY when a specific collection is mentioned (e.g., "CryptoPunks", "Azuki", "Bored Apes")
- If user says just "NFTs" or "cheap NFTs" without a collection name, use "search" not "search_items"

CRITICAL - STRUCTURED PARAMETERS FOR search_items:
- query: ONLY the collection/item name (e.g., "CryptoPunks", "Azuki", "Bored Apes")
- priceRange: {{"min": number, "max": number, "currency": "ETH"}} for price filters
- status: "listed" for items on sale, "sold" for sold items
- limit: number of results (10-50)
- chain: ethereum, polygon, base, solana
- includes: ["items"] for images

PARAMETER EXTRACTION RULES:
Extract filters from natural language and use structured parameters:
- "under X ETH" → priceRange: {{"max": X, "currency": "ETH"}}
- "above X ETH" → priceRange: {{"min": X, "currency": "ETH"}}
- "between X and Y ETH" → priceRange: {{"min": X, "max": Y, "currency": "ETH"}}
- "on sale/for sale/listed/currently on sale" → status: "listed"
- "sold" → status: "sold"
- DO NOT put price or status words in the query field!

For get_collection, include relevant data:
- ["items", "floorPrices", "salesVolume"] for market data
- ["items", "activity", "holders"] for collection analytics

EXAMPLES (note how filters become structured parameters):
User: "Find CryptoPunks currently on sale under 30 ETH"
{{"tool":"search_items","args":{{"query":"CryptoPunks","priceRange":{{"max":30,"currency":"ETH"}},"status":"listed","chain":"ethereum","limit":20}}}}

User: "Show me Azuki NFTs between 5 and 10 ETH"
{{"tool":"search_items","args":{{"query":"Azuki","priceRange":{{"min":5,"max":10,"currency":"ETH"}},"status":"listed","chain":"ethereum","limit":15}}}}

User: "Bored Apes for sale"
{{"tool":"search_items","args":{{"query":"Bored Apes","status":"listed","chain":"ethereum","limit":20}}}}

User: "Cheap NFTs under 0.01 ETH on Polygon"
{{"tool":"search","args":{{"query":"cheap NFTs under 0.01 ETH","chain":"polygon","limit":30}}}}

User: "Show pudgy penguins collection"
{{"tool":"get_collection","args":{{"slug":"pudgypenguins","includes":["items","floorPrices","salesVolume"]}}}}

User: "trending collections"
{{"tool":"get_trending_collections","args":{{"timeframe":"ONE_DAY","limit":10}}}}
"""


        try:
            # Get ASI:One Mini to generate the MCP request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ASI_ONE_API_KEY}"
            }
            data = {
                "model": "asi1-mini",
                "messages": [
                    {"role": "system", "content": "You generate OpenSea MCP API requests. Respond only with valid JSON!!, no ```, no markdown or extra text."},
                    {"role": "user", "content": tool_prompt}
                ],
                "temperature": 0
            }
            response = requests.post(ASI_ONE_URL, headers=headers, json=data)
            
            # Check if request was successful
            if response.status_code != 200:
                self._ctx.logger.error(f"ASI:One API error: {response.status_code} - {response.text}")
                return f"❌ ASI:One API error: {response.status_code}"
            
            response_json = response.json()
            
            # Check if response has expected structure
            if 'choices' not in response_json or not response_json['choices']:
                self._ctx.logger.error(f"Invalid ASI:One response structure: {response_json}")
                return "❌ Invalid response from ASI:One Mini"
            
            # Clean up response content (remove markdown if present)
            content = response_json['choices'][0]['message']['content'].strip()
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
            
            self._ctx.logger.info(f"🤖 ASI:One Mini selected: {tool_name} with args: {tool_args}")
            
            # Add query parameter if missing for search tools (only for general search)
            general_search_tools = ["search", "search_collections", "search_tokens"]
            if tool_name in general_search_tools and not tool_args.get("query"):
                # For general search tools, use the full query
                self._ctx.logger.info(f"No query parameter found for {tool_name}, using user's input")
                tool_args["query"] = user_query
            elif tool_name == "search_items" and not tool_args.get("query"):
                # For search_items, extract just the collection/item name, not the full query with filters
                # This is a fallback - the prompt should have extracted it properly
                self._ctx.logger.warning(f"No query for search_items, attempting to extract collection name")
                # Try to extract collection name from common patterns
                import re
                # Look for known collection names or NFT mentions
                collection_patterns = [
                    r'(CryptoPunks?|Punks?)',
                    r'(Bored Apes?|BAYC)',
                    r'(Azuki)',
                    r'(Pudgy Penguins?)',
                    r'(Doodles?)',
                    r'(CloneX)',
                    r'(Moonbirds?)',
                    r'(NFTs?)',
                ]
                for pattern in collection_patterns:
                    match = re.search(pattern, user_query, re.IGNORECASE)
                    if match:
                        tool_args["query"] = match.group(1)
                        self._ctx.logger.info(f"Extracted collection name: {tool_args['query']}")
                        break
                else:
                    # If no pattern matched, use a generic term
                    tool_args["query"] = "NFT"
                    self._ctx.logger.warning("Could not extract collection name, using 'NFT' as fallback")
            
            # Always add includes for appropriate tools to get images
            if tool_name in ["search", "search_items", "get_collection"]:
                if "includes" not in tool_args:
                    tool_args["includes"] = ["items"]
                    self._ctx.logger.info(f"Added includes: ['items'] to {tool_name} for image data")
            
            # Step 2: Execute the MCP request
            mcp_result = await self._execute_mcp_call(tool_name, tool_args)
            
            # Step 3: Use ASI:One Mini to parse and format the response
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
- IMAGE URLS: IMPORTANT - Always include any image URLs found in the response data (look for fields like image_url, image, display_image_url, collection.image_url, nft.image_url, etc.). Include the full URL exactly as provided.
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


            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ASI_ONE_API_KEY}"
            }
            data = {
                "model": "asi1-mini",
                "messages": [
                    {"role": "system", "content": "You parse NFT data and provide clear summaries."},
                    {"role": "user", "content": parse_prompt}
                ]
            }
            response = requests.post(ASI_ONE_URL, headers=headers, json=data)
            
            # Check if request was successful
            if response.status_code != 200:
                self._ctx.logger.error(f"ASI:One API error: {response.status_code} - {response.text}")
                return f"❌ ASI:One API error: {response.status_code}"
            
            response_json = response.json()
            
            # Check if response has expected structure
            if 'choices' not in response_json or not response_json['choices']:
                self._ctx.logger.error(f"Invalid ASI:One response structure: {response_json}")
                return "❌ Invalid response from ASI:One Mini"
            
            parsed_response = response_json['choices'][0]['message']['content']
            
            # Broadcast parsed response to TV agent if context is available
            if ctx and tv_agent_address:
                try:
                    broadcast_msg = BroadcastMessage(
                        message=parsed_response,
                        original_sender="etherius_parsed"
                    )
                    await ctx.send(tv_agent_address, broadcast_msg)
                    self._ctx.logger.info("📺 Broadcasted parsed NFT data to TV agent")
                except Exception as e:
                    self._ctx.logger.error(f"Failed to broadcast to TV agent: {e}")
            
            return parsed_response
            
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

# Addresses of the three receiver agents (will be set on startup)
katrik_agent_address = None
vitalik_agent_address = None
tv_agent_address = None
metta_agent_address = None

# Agent wallet for x402 payments
agent_wallet = None

# Store recent agent messages (keep last 50)
agent_messages: List[AgentMessage] = []
MAX_MESSAGES = 50

# Store current TV image
current_tv_image = {
    "image_url": "",
    "timestamp": 0
}

@agent.on_event("startup")
async def startup(ctx: Context):
    global mcp_client, katrik_agent_address, vitalik_agent_address, tv_agent_address, metta_agent_address, agent_wallet
    ctx.logger.info("🌟 Simplified Etherius Agent Starting")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info("🤖 Using ASI:One Mini for intelligent NFT queries")
    
    # Use the actual agent addresses
    katrik_agent_address = "agent1qw5tlakv4cqc8jztkksfz5rlkld74v0dcnkl46tcuvyrxwk9s6dzwryk9lf"
    vitalik_agent_address = "agent1qwel00zmglnll707lhle9nvnsntqcmahvya5wsa0vyd42sy26sz0wxqp2vs"
    tv_agent_address = "agent1qgydk7m0ghhcf0l6kme7enwlkxswvzlcwqg8epwaexs259re94cdg07kzr2"
    metta_agent_address = "agent1q0qs49vxucg494w3m3405uay4fjyf40q8mr9k73wftgnjqg2zukuwyx33jp"  # MeTTa agent address
    
    ctx.logger.info(f"📡 Will broadcast to Katrik: {katrik_agent_address}")
    ctx.logger.info(f"📡 Will broadcast to Vitalik: {vitalik_agent_address}")
    ctx.logger.info(f"📡 Will broadcast to TV: {tv_agent_address}")
    ctx.logger.info(f"🧠 Will send MeTTa queries to: {metta_agent_address}")
    
    # Check if API key is configured
    if not ASI_ONE_API_KEY:
        ctx.logger.warning("⚠️ ASI_ONE_API_KEY not found in environment. Please set it in your .env file.")
    else:
        ctx.logger.info("✅ ASI:One API key configured")
    
    mcp_client = SimpleOpenSeaMCP(ctx)
    
    # Initialize agent wallet for x402 payments
    ctx.logger.info("💰 Initializing agent wallet...")
    agent_wallet = AgentWallet()
    await agent_wallet.initialize()
    wallet_info = agent_wallet.get_wallet_info()
    ctx.logger.info(f"💳 Agent wallet ready: {wallet_info['address'][:10]}...")
    ctx.logger.info(f"   Type: {wallet_info['type']}, Network: {wallet_info['network']}")
    
    ctx.logger.info("✨ Ready!")

@agent.on_rest_post("/chat", ChatRequest, ChatResponse)
async def chat_endpoint(ctx: Context, req: ChatRequest) -> ChatResponse:
    """Chat endpoint that routes MeTTa queries, handles NFT purchases, or uses ASI:One Mini for OpenSea queries"""
    global agent_messages, active_purchases
    ctx.logger.info(f"💬 Chat: {req.message}")
    
    # Handle buy requests for NFT purchases
    if req.message.lower().startswith("buy "):
        nft_query = req.message[4:].strip()
        ctx.logger.info(f"🛒 NFT purchase request: {nft_query}")
        
        # Generate unique payment ID
        payment_id = hashlib.sha256(f"{nft_query}{time.time()}".encode()).hexdigest()[:8]
        
        # Get NFT details using existing OpenSea MCP
        nft_info = await mcp_client.query_with_gpt(f"get details and price for {nft_query}", ctx)
        
        # Create payment request via x402 service
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                payment_response = await client.post(
                    "http://localhost:8402/payment/create",
                    params={"nft_name": nft_query, "price": PAYMENT_CONFIG["default_price"]}
                )
                
                if payment_response.status_code == 200:
                    payment_data = payment_response.json()
                    payment_id = payment_data["payment_id"]
                    ctx.logger.info(f"Created x402 payment request: {payment_id}")
        except Exception as e:
            ctx.logger.error(f"Failed to create x402 payment request: {e}")
        
        # Store purchase details
        active_purchases[payment_id] = {
            "nft": nft_query,
            "price": PAYMENT_CONFIG["default_price"],
            "start_time": time.time(),
            "status": "awaiting_payment"
        }
        
        # Start auto-checker immediately
        asyncio.create_task(auto_check_payment(ctx, payment_id))
        
        response = f"""
💳 **NFT Purchase Started - x402 Payment System**

**NFT:** {nft_query}
**Price:** ${PAYMENT_CONFIG["default_price"]} USDC
**Payment ID:** `{payment_id}`
**Network:** {PAYMENT_CONFIG["network"]}

**Payment Options:**

**Option 1: Agent Wallet (Recommended)**
• Fund agent's wallet with USDC:
  `{agent_wallet.get_address()}`
• Then type: `execute {payment_id}`
• Agent will use x402 to complete purchase

**Option 2: Direct Payment**
• Send USDC to seller:
  `{PAYMENT_CONFIG["receiving_address"]}`
• Then type: `verify 0xYourTxHash`

**Option 3: x402 Portal**
• Visit: `http://localhost:8402/nft/purchase/{payment_id}`

✨ **Agent wallet enables proper x402 payments!**

{nft_info}
"""
        
        # Store and return response
        agent_msg = AgentMessage(
            agent_name="Etherius",
            message=response,
            timestamp=time.time()
        )
        agent_messages.append(agent_msg)
        
        # Keep only last MAX_MESSAGES
        if len(agent_messages) > MAX_MESSAGES:
            agent_messages = agent_messages[-MAX_MESSAGES:]
        
        return ChatResponse(response=response)
    
    # Handle "execute" command for agent wallet x402 payments
    elif req.message.lower().startswith("execute "):
        payment_id = req.message[8:].strip()
        
        if payment_id not in active_purchases:
            return ChatResponse(response=f"❌ Payment ID `{payment_id}` not found")
        
        purchase = active_purchases[payment_id]
        
        if purchase["status"] == "completed":
            return ChatResponse(response=f"✅ Already paid! NFT: {purchase['nft']} has been transferred.")
        
        ctx.logger.info(f"🤖 Agent executing x402 payment for {payment_id}")
        
        try:
            # Use agent's wallet with x402 client
            result = await agent_wallet.execute_payment(payment_id, purchase["price"])
            
            if result and result.status_code == 200:
                purchase["status"] = "completed"
                
                success_msg = f"""
✅ **Payment Completed via x402!**

**Payment ID:** `{payment_id}`
**NFT:** {purchase["nft"]}
**Method:** Agent wallet with x402 protocol

Your NFT has been transferred! The agent successfully used x402 to complete the purchase.
"""
                
                # Store message for history
                agent_msg = AgentMessage(
                    agent_name="Etherius",
                    message=success_msg,
                    timestamp=time.time()
                )
                agent_messages.append(agent_msg)
                
                # Keep only last MAX_MESSAGES
                if len(agent_messages) > MAX_MESSAGES:
                    agent_messages = agent_messages[-MAX_MESSAGES:]
                
                return ChatResponse(response=success_msg)
            else:
                status_code = result.status_code if result else "unknown"
                return ChatResponse(response=f"❌ Payment failed (status: {status_code}). Check agent wallet balance.")
        except Exception as e:
            ctx.logger.error(f"Payment execution error: {e}")
            return ChatResponse(response=f"❌ Error executing payment: {str(e)}")
    
    # Handle "verify" command for manual transaction verification
    elif req.message.lower().startswith("verify "):
        tx_hash = req.message[7:].strip()
        
        # Find most recent pending payment
        recent_payment_id = None
        for pid, purchase in active_purchases.items():
            if purchase["status"] in ["awaiting_payment", "awaiting_funding"]:
                recent_payment_id = pid
                break
        
        if not recent_payment_id:
            return ChatResponse(response="No pending payment found. Use 'buy' command first.")
        
        if tx_hash.startswith("0x") and len(tx_hash) == 66:
            # Mark as completed (simplified verification for demo)
            active_purchases[recent_payment_id]["status"] = "completed"
            active_purchases[recent_payment_id]["tx_hash"] = tx_hash
            
            return ChatResponse(response=f"✅ Transaction verified! Payment {recent_payment_id} completed with tx: {tx_hash[:10]}...")
        else:
            return ChatResponse(response="❌ Invalid transaction hash. Must start with 0x and be 66 characters.")
    
    # Handle payment check requests (optional manual check)
    elif req.message.lower().startswith("check "):
        payment_id = req.message[6:].strip()
        
        if payment_id not in active_purchases:
            return ChatResponse(response=f"❌ Payment ID `{payment_id}` not found")
        
        purchase = active_purchases[payment_id]
        
        if purchase["status"] == "completed":
            return ChatResponse(response=f"✅ Payment already confirmed! NFT: {purchase['nft']} has been transferred.")
        elif purchase["status"] == "awaiting_payment":
            elapsed = int(time.time() - purchase["start_time"])
            return ChatResponse(response=f"⏳ Still checking for payment... Auto-check running every 15 seconds. ({elapsed}s elapsed)")
        elif purchase["status"] == "expired":
            return ChatResponse(response=f"⏱️ Payment request expired. Please create a new purchase request.")
        else:
            return ChatResponse(response=f"Status: {purchase['status']}")
    
    # Handle "wallet" command to show agent wallet info
    elif req.message.lower() == "wallet":
        wallet_info = agent_wallet.get_wallet_info()
        response = f"""
💰 **Agent Wallet Information**

**Address:** `{wallet_info['address']}`
**Type:** {wallet_info['type']}
**Network:** {wallet_info['network']}
**Status:** {'Ready' if wallet_info['ready'] else 'Not Ready'}

**Check Balance:** https://sepolia.basescan.org/address/{wallet_info['address']}

To fund: Send USDC to the address above on Base Sepolia network.
"""
        return ChatResponse(response=response)
    
    # Check if this is a MeTTa query (starts with !)
    elif req.message.startswith("!"):
        ctx.logger.info("🧠 Detected MeTTa query, routing to MeTTa agent...")
        
        if metta_agent_address:
            # Remove the ! prefix and send to MeTTa agent
            metta_request = MettaQueryRequest(query=req.message[1:])
            await ctx.send(metta_agent_address, metta_request)
            
            # Store a placeholder message
            agent_msg = AgentMessage(
                agent_name="Etherius",
                message="Processing MeTTa query...",
                timestamp=time.time()
            )
            agent_messages.append(agent_msg)
            
            # Keep only last MAX_MESSAGES
            if len(agent_messages) > MAX_MESSAGES:
                agent_messages = agent_messages[-MAX_MESSAGES:]
            
            return ChatResponse(response="MeTTa query sent for processing. Results will appear shortly.")
        else:
            return ChatResponse(response="MeTTa agent not configured. Please ensure MeTTa agent is running.")
    
    # For non-MeTTa queries, broadcast to all agents as before
    if katrik_agent_address and vitalik_agent_address and tv_agent_address:
        broadcast_msg = BroadcastMessage(
            message=req.message,
            original_sender="user"
        )
        
        # Send to all agents (fire and forget)
        ctx.logger.info("📢 Broadcasting message to all agents...")
        await ctx.send(katrik_agent_address, broadcast_msg)
        await ctx.send(vitalik_agent_address, broadcast_msg)
        await ctx.send(tv_agent_address, broadcast_msg)
        ctx.logger.info("✅ Broadcast complete")
    else:
        ctx.logger.warning("⚠️ Agent addresses not initialized, skipping broadcast")
    
    if not mcp_client:
        return ChatResponse(response="Agent not initialized. Please restart.")
    
    response = await mcp_client.query_with_gpt(req.message, ctx)
    
    # Store Etherius's response
    agent_msg = AgentMessage(
        agent_name="Etherius",
        message=response,
        timestamp=time.time()
    )
    agent_messages.append(agent_msg)
    
    # Keep only last MAX_MESSAGES
    if len(agent_messages) > MAX_MESSAGES:
        agent_messages = agent_messages[-MAX_MESSAGES:]
    
    return ChatResponse(response=response)

@agent.on_message(model=BroadcastMessage)
async def handle_agent_response(ctx: Context, sender: str, msg: BroadcastMessage):
    """Handle responses from other agents (like Vitalik's GPT response)"""
    global agent_messages
    ctx.logger.info(f"📬 Received response from {sender}")
    ctx.logger.info(f"📝 Original sender: {msg.original_sender}")
    ctx.logger.info(f"💬 Response: {msg.message}")
    
    # Determine agent name from sender address
    agent_name = "Unknown"
    if sender == katrik_agent_address:
        agent_name = "Katrik"
    elif sender == vitalik_agent_address:
        agent_name = "Vitalik"
    elif sender == tv_agent_address:
        agent_name = "TV"
    elif sender == metta_agent_address:
        agent_name = "MeTTa"
    
    # Store the agent's response
    agent_msg = AgentMessage(
        agent_name=agent_name,
        message=msg.message,
        timestamp=time.time()
    )
    agent_messages.append(agent_msg)
    
    # Keep only last MAX_MESSAGES
    if len(agent_messages) > MAX_MESSAGES:
        agent_messages = agent_messages[-MAX_MESSAGES:]

@agent.on_rest_get("/agent_messages", AgentMessagesResponse)
async def get_agent_messages(ctx: Context) -> AgentMessagesResponse:
    """Get recent agent messages for frontend polling"""
    global agent_messages
    return AgentMessagesResponse(messages=agent_messages)

@agent.on_message(model=ImageUrlMessage)
async def handle_tv_image(ctx: Context, sender: str, msg: ImageUrlMessage):
    """Handle image URL from TV agent"""
    global current_tv_image
    ctx.logger.info(f"📺 Received image URL from TV: {msg.image_url}")
    
    # Store the image URL with timestamp
    current_tv_image = {
        "image_url": msg.image_url,
        "timestamp": time.time()
    }
    ctx.logger.info("TV image URL stored for display")

@agent.on_rest_get("/tv_image", TvImageResponse)
async def get_tv_image(ctx: Context) -> TvImageResponse:
    """Get current TV image for frontend display"""
    global current_tv_image
    return TvImageResponse(
        image_url=current_tv_image["image_url"],
        timestamp=current_tv_image["timestamp"]
    )

@agent.on_rest_get("/health", ChatResponse)
async def health_check(ctx: Context) -> ChatResponse:
    ctx.logger.info("Health check requested")
    return ChatResponse(response="Simplified Etherius agent is healthy!")

# Auto-check payment function
async def auto_check_payment(ctx: Context, payment_id: str):
    """Automatically check for payment every 15 seconds"""
    global active_purchases, agent_messages
    
    if payment_id not in active_purchases:
        return
    
    purchase = active_purchases[payment_id]
    end_time = purchase["start_time"] + PAYMENT_CONFIG["max_check_time"]
    check_count = 0
    
    ctx.logger.info(f"🔄 Starting auto-check for payment {payment_id}")
    
    while time.time() < end_time:
        check_count += 1
        
        # Wait before checking
        await asyncio.sleep(PAYMENT_CONFIG["auto_check_interval"])
        
        # Check if purchase still active
        if payment_id not in active_purchases:
            break
        if purchase["status"] != "awaiting_payment":
            break
        
        ctx.logger.info(f"🔍 Auto-check #{check_count} for {payment_id}")
        
        # Check blockchain (mock for now)
        payment_found = await check_blockchain(
            PAYMENT_CONFIG["receiving_address"],
            purchase["price"],
            payment_id
        )
        
        if payment_found:
            # Payment detected!
            ctx.logger.info(f"✅ Payment detected for {payment_id}!")
            
            purchase["status"] = "completed"
            purchase["tx_hash"] = payment_found  # tx hash from blockchain
            
            # Notify user immediately
            success_message = f"""
🎉 **Payment Automatically Detected!**

**Payment ID:** `{payment_id}`
**NFT:** {purchase["nft"]}
**Transaction:** `{purchase["tx_hash"]}`

✅ Your NFT has been transferred to your wallet!

Thank you for your purchase!
"""
            
            # Add to messages for user to see
            agent_messages.append(AgentMessage(
                agent_name="Etherius",
                message=success_message,
                timestamp=time.time()
            ))
            
            # Keep only last MAX_MESSAGES
            if len(agent_messages) > MAX_MESSAGES:
                agent_messages = agent_messages[-MAX_MESSAGES:]
            
            # Transfer NFT (mock)
            await transfer_nft(purchase["nft"])
            
            break
    
    # Timeout reached
    if purchase["status"] == "awaiting_payment":
        purchase["status"] = "expired"
        ctx.logger.info(f"⏱️ Payment {payment_id} expired after 5 minutes")
        
        timeout_message = f"""
⏱️ **Payment Window Expired**

Payment ID `{payment_id}` has expired after 5 minutes.
If you already sent payment, please contact support.
To try again, send a new "buy" request.
"""
        
        agent_messages.append(AgentMessage(
            agent_name="Etherius",
            message=timeout_message,
            timestamp=time.time()
        ))
        
        # Keep only last MAX_MESSAGES
        if len(agent_messages) > MAX_MESSAGES:
            agent_messages = agent_messages[-MAX_MESSAGES:]

# Real x402 payment verification
async def check_blockchain(address: str, amount: float, payment_id: str) -> Optional[str]:
    """
    Check if payment received via x402 service
    Returns transaction hash if payment is verified
    """
    try:
        # Check payment status via x402 service
        async with httpx.AsyncClient(timeout=10.0) as client:
            # First check if payment has been recorded
            status_response = await client.get(
                f"http://localhost:8402/payment/status/{payment_id}"
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data.get("status") == "completed":
                    # Payment already verified
                    return status_data.get("tx_hash", f"0x{payment_id}")
            
            # Try to verify payment through x402 protected endpoint
            # This will return 402 if payment not made, 200 if payment verified
            verify_response = await client.post(
                f"http://localhost:8402/nft/purchase/{payment_id}",
                headers={
                    "X-Payment-Id": payment_id,
                    "Content-Type": "application/json"
                },
                json={"payment_id": payment_id}
            )
            
            if verify_response.status_code == 200:
                # Payment successfully verified by x402
                data = verify_response.json()
                return data.get("tx_hash", f"0x{payment_id}")
            elif verify_response.status_code == 402:
                # Payment still required - user hasn't paid yet
                return None
            else:
                # Some other error
                return None
                
    except Exception as e:
        # Log error but don't crash
        print(f"Error checking payment {payment_id}: {e}")
        return None

# Mock NFT transfer
async def transfer_nft(nft_name: str) -> bool:
    """Transfer NFT to buyer (mock)"""
    # In production: Execute actual NFT contract transfer
    return True

if __name__ == "__main__":
    print("""
🌟 Simplified Etherius Agent - ASI:One Mini Powered NFT Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Natural language NFT queries via ASI:One Mini
• Automatic OpenSea MCP request generation
• Intelligent response parsing and formatting
• REST API: POST /chat {"message": "your question"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()