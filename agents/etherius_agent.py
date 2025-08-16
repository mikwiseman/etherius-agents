#!/usr/bin/env python3
"""
Etherius Agent - OpenSea MCP Collection Finder
Fetch.ai uAgent that connects to OpenSea's MCP server to answer user questions
by finding relevant NFT collections and returning real marketplace data.

- Uses OpenSea MCP (Model Context Protocol) over Streamable HTTP
- No payments, no x402, no mock data
- Focused on: user asks a question -> agent finds relevant collections and replies

Docs:
- OpenSea MCP (beta): https://docs.opensea.io/docs/mcp
- MCP Spec (protocol version 2025-06-18)
"""

import os
import sys
import json
import uuid
import httpx
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, UTC
from enum import Enum
from dotenv import load_dotenv

from uagents import Agent, Context, Model, Protocol
from pydantic import Field, BaseModel

# Ensure parent directory is importable if this file lives under /agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# ────────────────────────────────────────────────────────────────────────────────
# Agent configuration
# ────────────────────────────────────────────────────────────────────────────────

agent = Agent(
    name="etherius_mcp",
    seed=os.getenv("ETHERIUS_SEED", "etherius_unified_mcp_agent_2025"),
    port=int(os.getenv("ETHERIUS_PORT", 8100)),
    endpoint=[f"http://localhost:{os.getenv('ETHERIUS_PORT', 8100)}/submit"],
    mailbox=True,
)

# ────────────────────────────────────────────────────────────────────────────────
# Request / Response Models
# ────────────────────────────────────────────────────────────────────────────────

class RequestType(str, Enum):
    QUESTION = "question"          # User asks a natural language question
    SEARCH_COLLECTIONS = "search"  # Explicit collections search
    ANALYZE_COLLECTION = "analyze" # Get stats for a specific collection slug


class MCPQuery(Model):
    """Unified request for collection-oriented queries."""
    question: str
    request_type: Optional[RequestType] = None
    chain: Optional[str] = None
    limit: Optional[int] = 10


class CollectionSummary(Model):
    """Normalized view of a collection returned by OpenSea MCP."""
    slug: str
    name: Optional[str] = None
    chain: Optional[str] = None
    floor: Optional[float] = None
    floor_currency: Optional[str] = None
    one_day_volume: Optional[float] = None
    seven_day_volume: Optional[float] = None
    thirty_day_volume: Optional[float] = None
    total_volume: Optional[float] = None
    one_day_change_pct: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    opensea_url: Optional[str] = None


class MCPAnswer(Model):
    """Agent response with normalized collections and a human-friendly message."""
    success: bool
    message: str
    collections: Optional[List[CollectionSummary]] = None
    session_id: str


# Simple REST chat models
class ChatRequest(Model):
    message: str

class ChatResponse(Model):
    response: str


# ────────────────────────────────────────────────────────────────────────────────
# OpenSea MCP Client
# ────────────────────────────────────────────────────────────────────────────────

class OpenSeaMCPClient:
    """
    Minimal MCP client for OpenSea MCP over Streamable HTTP.
    Implements JSON-RPC 2.0 calls for 'initialize', 'tools/list', and 'tools/call'.
    """

    def __init__(self, ctx: Context):
        self._ctx = ctx
        self.access_token = os.getenv("OPENSEA_MCP_TOKEN", "")
        self.base_url = "https://mcp.opensea.io/mcp"
        self.session_id = None  # Will be assigned by server

        self.base_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.access_token:
            self.base_headers["Authorization"] = f"Bearer {self.access_token}"

        self._session_initialized = False

        if not self.access_token:
            self._ctx.logger.warning("⚠️ OPENSEA_MCP_TOKEN not found in environment. "
                                     "Request access at https://docs.opensea.io/docs/mcp and set OPENSEA_MCP_TOKEN.")

    async def _post(self, payload: Dict[str, Any], include_session: bool = True) -> httpx.Response:
        headers = dict(self.base_headers)
        if include_session and self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        async with httpx.AsyncClient(timeout=45.0, follow_redirects=True) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            self._ctx.logger.debug(f"Response headers: {dict(response.headers)}")
            return response

    async def initialize_session(self) -> bool:
        """Initialize MCP session (idempotent)."""
        if self._session_initialized:
            return True

        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                # Use latest stable protocol revision
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "etherius-agent", "version": "1.1.0"},
            },
        }
        try:
            # Don't include session ID in initialize request
            resp = await self._post(init_request, include_session=False)
            if resp.status_code == 200:
                # Capture session ID from response headers if provided
                session_header = resp.headers.get("Mcp-Session-Id")
                if session_header:
                    self.session_id = session_header
                    self._ctx.logger.info(f"✅ OpenSea MCP session initialized with ID: {session_header[:8]}...")
                else:
                    self._ctx.logger.info("✅ OpenSea MCP session initialized")
                self._session_initialized = True
                return True
            else:
                self._ctx.logger.error(f"Failed to initialize MCP session: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            self._ctx.logger.error(f"Error initializing MCP session: {e}")
            return False

    async def list_tools(self) -> Dict[str, Any]:
        """Optional: discover available tools."""
        if not await self.initialize_session():
            return {"error": "initialize_failed"}
        req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        try:
            resp = await self._post(req)
            if resp.status_code == 200:
                return resp.json().get("result", {})
            return {"error": f"tools/list failed: {resp.status_code}", "raw": resp.text}
        except Exception as e:
            return {"error": f"tools/list exception: {e}"}

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a named MCP tool with arguments and parse the JSON-RPC result."""
        if not self.access_token:
            return {
                "error": "missing_token",
                "message": "OPENSEA_MCP_TOKEN not set. Request access at https://docs.opensea.io/docs/mcp",
            }
        if not await self.initialize_session():
            return {"error": "initialize_failed"}

        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        self._ctx.logger.info(f"🔧 Calling MCP tool: {tool_name} args={arguments}")
        try:
            resp = await self._post(req)
            status = resp.status_code
            self._ctx.logger.debug(f"MCP status={status}")
            if status == 200:
                # Check content type
                content_type = resp.headers.get("content-type", "").lower()
                
                if "text/event-stream" in content_type:
                    # Handle SSE response - OpenSea MCP returns SSE format
                    text = resp.text
                    self._ctx.logger.debug(f"SSE Response (first 500 chars): {text[:500]}")
                    
                    # Parse SSE format
                    # SSE format: each message is separated by double newlines
                    # Each field is "name: value\n"
                    messages = text.split('\n\n')
                    
                    for message in messages:
                        if not message.strip():
                            continue
                            
                        # Parse SSE message fields
                        event_type = None
                        data_content = None
                        
                        for line in message.split('\n'):
                            if line.startswith('event:'):
                                event_type = line[6:].strip()
                            elif line.startswith('data:'):
                                data_content = line[5:].strip()
                        
                        # Process data field if present
                        if data_content:
                            try:
                                # Try to parse as JSON
                                parsed = json.loads(data_content)
                                
                                # Check for JSON-RPC response structure
                                if isinstance(parsed, dict):
                                    if "result" in parsed:
                                        self._ctx.logger.info(f"✅ Found result in SSE data")
                                        return self._extract_result(parsed["result"])
                                    elif "error" in parsed:
                                        self._ctx.logger.warning(f"❌ SSE error: {parsed['error']}")
                                        return {"error": parsed["error"]}
                                    # Sometimes the data IS the result
                                    elif any(k in parsed for k in ["collections", "data", "items", "results"]):
                                        self._ctx.logger.info(f"✅ Found collections data in SSE")
                                        return parsed
                            except json.JSONDecodeError:
                                # If not JSON, might be plain text or [DONE]
                                if data_content == "[DONE]":
                                    continue
                                self._ctx.logger.debug(f"Non-JSON SSE data: {data_content[:100]}")
                    
                    # If we didn't find valid data in SSE
                    return {"error": "no_valid_sse_data", "raw": text[:500]}
                    
                else:
                    # Regular JSON response
                    try:
                        payload = resp.json()
                        if "result" in payload:
                            return self._extract_result(payload["result"])
                        if "error" in payload:
                            return {"error": payload["error"]}
                        return {"error": "invalid_response", "raw": payload}
                    except json.JSONDecodeError as e:
                        self._ctx.logger.error(f"Failed to parse JSON response: {e}")
                        return {"error": f"json_parse_error: {e}", "raw": resp.text[:500]}
            elif status in (401, 403):
                return {"error": "unauthorized", "raw": resp.text}
            elif status == 404:
                # Re-init and one retry
                self._session_initialized = False
                if await self.initialize_session():
                    resp2 = await self._post(req)
                    if resp2.status_code == 200:
                        payload2 = resp2.json()
                        return self._extract_result(payload2.get("result", {}))
                return {"error": "not_found_or_session", "raw": resp.text}
            else:
                return {"error": f"http_{status}", "raw": resp.text}
        except Exception as e:
            self._ctx.logger.error(f"MCP call error: {e}")
            return {"error": f"exception: {e}"}

    # ── High-level helpers for OpenSea MCP tools ────────────────────────────────

    async def search_collections(self, query: str, chain: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        params: Dict[str, Any] = {"query": query, "limit": int(limit)}
        if chain:
            params["chain"] = chain
        return await self.call_tool("search_collections", params)

    async def get_collection(self, slug: str, includes: Optional[List[str]] = None) -> Dict[str, Any]:
        # OpenSea MCP expects 'slug' not 'collection'
        params: Dict[str, Any] = {"slug": slug}
        if includes:
            params["includes"] = includes
        # Use valid includes per the error message
        else:
            params["includes"] = ["analytics", "offers", "holders"]
        return await self.call_tool("get_collection", params)

    async def get_trending_collections(self, timeframe: str = "ONE_DAY", chain: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        params: Dict[str, Any] = {"timeframe": timeframe, "limit": int(limit)}
        if chain:
            params["chain"] = chain
        return await self.call_tool("get_trending_collections", params)

    async def get_top_collections(self, chain: Optional[str] = None, limit: int = 10, sort_by: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": int(limit)}
        if chain:
            params["chain"] = chain
        if sort_by:
            params["sort_by"] = sort_by  # depends on server (e.g., ONE_DAY_VOLUME, FLOOR_PRICE, SALES)
        return await self.call_tool("get_top_collections", params)

    # ── Internal helpers ────────────────────────────────────────────────────────

    def _extract_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP result may be:
          - a plain JSON object with domain fields (e.g., {"collections":[...], "cursor":...})
          - or structured MCP content: {"content":[{"type":"json","data":{...}}]}
          - or even text content we can try to parse as JSON
        Return a normalized JSON dict.
        """
        if not isinstance(result, dict):
            return {"data": result}

        # If result contains content array, prefer JSON entries
        if "content" in result and isinstance(result["content"], list):
            for item in result["content"]:
                if isinstance(item, dict):
                    if item.get("type") == "json" and "data" in item:
                        return item["data"]
                    if item.get("type") == "text" and isinstance(item.get("text"), str):
                        try:
                            return json.loads(item["text"])
                        except Exception:
                            # keep raw text as fallback
                            return {"text": item["text"]}
            # If content exists but no json/text recognized, return raw
            return {"content": result["content"]}

        # Otherwise return result as-is; most OpenSea MCP tools return direct JSON
        return result


# ────────────────────────────────────────────────────────────────────────────────
# Normalization helpers
# ────────────────────────────────────────────────────────────────────────────────

def _safe_float(v: Any) -> Optional[float]:
    try:
        return float(v)
    except Exception:
        return None

def _pick(*vals) -> Optional[Any]:
    for v in vals:
        if v not in (None, "", [], {}):
            return v
    return None

def normalize_collection_record(rec: Dict[str, Any]) -> CollectionSummary:
    """
    Normalize a single collection record from OpenSea MCP into CollectionSummary.
    Handles multiple possible key names defensively.
    """
    # Handle OpenSea MCP's nested structure
    if "__typename" in rec and rec.get("__typename") == "DelistedCollection":
        # Skip delisted collections
        return None
        
    # Common field name variations
    slug = _pick(rec.get("slug"), rec.get("collection_slug"), rec.get("collection"), rec.get("id"))
    # Ensure slug is a string
    if slug is None or slug == "":
        slug = "unknown"
    else:
        slug = str(slug)
        
    name = _pick(rec.get("name"), rec.get("collection_name"))
    
    # Handle chain as nested object or string
    chain_obj = rec.get("chain")
    if isinstance(chain_obj, dict):
        chain = chain_obj.get("name") or chain_obj.get("identifier")
    else:
        chain = _pick(chain_obj, rec.get("blockchain"), rec.get("network"))
    
    # Handle floor price as nested object
    floor_obj = rec.get("floorPrice")
    if isinstance(floor_obj, dict):
        price_per = floor_obj.get("pricePerItem", {})
        if isinstance(price_per, dict):
            token_info = price_per.get("token", {})
            floor = _safe_float(token_info.get("unit"))
            floor_currency = token_info.get("symbol", "ETH")
        else:
            floor = None
            floor_currency = None
    else:
        floor = _safe_float(_pick(rec.get("floor_price"), rec.get("floor")))
        floor_currency = _pick(
            rec.get("floor_currency"),
            rec.get("floor_price_currency"),
            rec.get("currency"),
            rec.get("native_currency"),
        )

    # Handle stats - OpenSea MCP has nested volume structure
    stats = rec.get("stats") or {}
    
    # Extract 24h volume from nested structure
    one_day_stats = stats.get("oneDay", {})
    if one_day_stats:
        vol_obj = one_day_stats.get("volume", {})
        if isinstance(vol_obj, dict):
            native_vol = vol_obj.get("native", {})
            one_day_vol = _safe_float(native_vol.get("unit"))
        else:
            one_day_vol = _safe_float(vol_obj)
        one_day_change_pct = _safe_float(one_day_stats.get("floorPriceChange"))
        if one_day_change_pct and -2 <= one_day_change_pct <= 2:
            one_day_change_pct = round(float(one_day_change_pct) * 100.0, 2)
    else:
        one_day_vol = _safe_float(stats.get("one_day_volume"))
        one_day_change_pct = _safe_float(stats.get("one_day_change"))
        
    # Similar for 7-day volume
    seven_day_stats = stats.get("sevenDays", {})
    if seven_day_stats:
        vol_obj = seven_day_stats.get("volume", {})
        if isinstance(vol_obj, dict):
            native_vol = vol_obj.get("native", {})
            seven_day_vol = _safe_float(native_vol.get("unit"))
        else:
            seven_day_vol = _safe_float(vol_obj)
    else:
        seven_day_vol = _safe_float(stats.get("seven_day_volume"))
        
    # Total volume
    total_vol_obj = stats.get("volume", {})
    if isinstance(total_vol_obj, dict):
        native_vol = total_vol_obj.get("native", {})
        total_volume = _safe_float(native_vol.get("unit"))
    else:
        total_volume = _safe_float(stats.get("total_volume"))
    
    thirty_day_vol = _safe_float(stats.get("thirty_day_volume"))
    
    image_url = _pick(rec.get("imageUrl"), rec.get("image_url"), rec.get("display_image_url"), rec.get("logo"))
    description = rec.get("description")
    # Build a canonical OpenSea collection URL if we have a slug
    opensea_url = f"https://opensea.io/collection/{slug}" if slug and slug != "unknown" else None

    return CollectionSummary(
        slug=slug,
        name=name,
        chain=chain,
        floor=floor,
        floor_currency=floor_currency,
        one_day_volume=one_day_vol,
        seven_day_volume=seven_day_vol,
        thirty_day_volume=thirty_day_vol,
        total_volume=total_volume,
        one_day_change_pct=one_day_change_pct,
        image_url=image_url,
        description=description,
        opensea_url=opensea_url,
    )


def normalize_collections(result: Dict[str, Any]) -> List[CollectionSummary]:
    """
    Normalize collections from various possible shapes:
      - {"collections":[...]}
      - {"results":[{"type":"collection", "data":{...}}, ...]}
      - {"data":[...]} or direct [...]
    """
    raw = None
    if isinstance(result, list):
        raw = result
    elif isinstance(result, dict):
        raw = (
            result.get("collections")
            or result.get("data")
            or result.get("results")
            or result.get("items")
        )
        # If "results" contains typed objects, pluck collection-like ones
        if raw and isinstance(raw, list) and raw and isinstance(raw[0], dict) and "type" in raw[0]:
            candidates = []
            for r in raw:
                if (r.get("type") in ("collection", "collections")) and isinstance(r.get("data"), dict):
                    candidates.append(r["data"])
            if candidates:
                raw = candidates

    collections: List[CollectionSummary] = []
    if isinstance(raw, list):
        for rec in raw:
            if isinstance(rec, dict):
                normalized = normalize_collection_record(rec)
                if normalized:  # Skip None (delisted collections)
                    collections.append(normalized)
    elif isinstance(raw, dict):
        # rare case of mapped slug->collection dict
        for _, rec in raw.items():
            if isinstance(rec, dict):
                normalized = normalize_collection_record(rec)
                if normalized:  # Skip None (delisted collections)
                    collections.append(normalized)
    return [c for c in collections if c and c.slug]


# ────────────────────────────────────────────────────────────────────────────────
# Core Agent Logic
# ────────────────────────────────────────────────────────────────────────────────

mcp_clients: Dict[str, OpenSeaMCPClient] = {}

async def get_mcp_client(ctx: Context) -> OpenSeaMCPClient:
    key = str(id(ctx))
    if key not in mcp_clients:
        mcp_clients[key] = OpenSeaMCPClient(ctx)
    return mcp_clients[key]


def _infer_request_type(text: str) -> RequestType:
    t = text.lower()
    if any(x in t for x in ("trend", "trending", "hot", "top")):
        return RequestType.SEARCH_COLLECTIONS
    if any(x in t for x in ("analyze", "floor", "stats", "price", "volume")):
        return RequestType.ANALYZE_COLLECTION
    return RequestType.QUESTION


def _maybe_extract_slug(text: str) -> Optional[str]:
    """
    Attempt to extract a likely OpenSea collection slug from free text.
    Heuristics: compact alphanum + hyphen words; prefer known patterns like boredapeyachtclub, doodles-official, pudgy-penguins.
    """
    s = "".join(ch if ch.isalnum() or ch in "-_" else " " for ch in text.lower())
    tokens = [tok for tok in s.split() if len(tok) >= 3]
    # return the longest hyphen/underscore-containing token as a plausible slug
    candidates = [tok for tok in tokens if "-" in tok or "_" in tok]
    if candidates:
        candidates.sort(key=len, reverse=True)
        return candidates[0]
    # otherwise pick a solid alphanumeric token (e.g., "azuki")
    alnum = [tok for tok in tokens if tok.isalnum()]
    if alnum:
        alnum.sort(key=len, reverse=True)
        return alnum[0]
    return None


async def answer_user_question(ctx: Context, query: str, chain: Optional[str], limit: int) -> Tuple[str, List[CollectionSummary]]:
    """
    Primary orchestration:
      1) Try search_collections with the full user query (optionally chain/limit)
      2) If no results and query looks like a slug, call get_collection
      3) If query hints at 'trending/top', call those tools
    """
    client = await get_mcp_client(ctx)

    # 1) Default: search_collections
    search_res = await client.search_collections(query=query, chain=chain, limit=limit)
    if "error" not in search_res:
        colls = normalize_collections(search_res)
        if colls:
            msg = f"Found {len(colls)} collection(s) for “{query}”."
            return msg, colls

    # 2) If looks like a specific slug, ask get_collection
    slug = _maybe_extract_slug(query)
    # Skip generic words that aren't actual collection slugs
    if slug and slug not in ["collections", "collection", "nft", "nfts", "trending", "top"]:
        detail = await client.get_collection(slug)
        if "error" not in detail:
            colls = normalize_collections(detail)
            if not colls and detail:
                # Try to normalize the detail directly if it's a collection object
                normalized = normalize_collection_record(detail)
                if normalized:
                    colls = [normalized]
            colls = [c for c in colls if c and c.slug]  # ensure at least slug present
            if colls:
                msg = f"Details for collection '{slug}'."
                return msg, colls

    # 3) Trending/top fallback if the query suggests it
    req_type = _infer_request_type(query)
    if req_type == RequestType.SEARCH_COLLECTIONS:
        trend = await client.get_trending_collections(timeframe="ONE_DAY", chain=chain, limit=limit)
        if "error" not in trend:
            colls = normalize_collections(trend)
            if colls:
                msg = f"Trending collections (last 24h){' on ' + chain if chain else ''}."
                return msg, colls

        top = await client.get_top_collections(chain=chain, limit=limit, sort_by="ONE_DAY_VOLUME")
        if "error" not in top:
            colls = normalize_collections(top)
            if colls:
                msg = f"Top collections by daily volume{' on ' + chain if chain else ''}."
                return msg, colls

    # If we reach here, return any error we have
    err_text = "Unable to retrieve collections. "
    if isinstance(search_res, dict) and "error" in search_res:
        err_text += f"MCP error: {search_res.get('error')}"
        raw = search_res.get("raw") or search_res.get("message")
        if raw:
            err_text += f" | {raw}"
    return err_text, []


def format_collections_md(colls: List[CollectionSummary], max_rows: int = 10) -> str:
    """Produce a concise markdown summary of collections."""
    if not colls:
        return "No collections found."

    lines = []
    header = "| # | Collection | Chain | Floor | 24h Vol | 24h Δ | Link |\n|---:|---|---|---:|---:|---:|---|"
    lines.append(header)

    def fmt_num(x: Optional[float]) -> str:
        if x is None:
            return "—"
        if abs(x) >= 1000:
            return f"{x:,.0f}"
        if abs(x) >= 10:
            return f"{x:,.2f}"
        return f"{x:.4f}"

    for i, c in enumerate(colls[:max_rows], start=1):
        # Ensure we're formatting string values, not the entire object
        floor = f"{fmt_num(c.floor)} {c.floor_currency or 'ETH'}" if c.floor is not None else "—"
        vol = fmt_num(c.one_day_volume) if c.one_day_volume else "—"
        d1 = f"{c.one_day_change_pct:+.2f}%" if c.one_day_change_pct is not None else "—"
        name = str(c.name or c.slug)[:50]  # Limit name length and ensure string
        link = c.opensea_url or f"https://opensea.io/collection/{c.slug}"
        chain_str = str(c.chain or '—')[:20]  # Ensure chain is string
        lines.append(f"| {i} | **{name}** | {chain_str} | {floor} | {vol} | {d1} | [OpenSea]({link}) |")

    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────────────────────
# Agent lifecycle & protocol handlers
# ────────────────────────────────────────────────────────────────────────────────

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("🌟 Etherius MCP Agent Starting")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info("🧠 Mode: Collection discovery via OpenSea MCP")
    if os.getenv("OPENSEA_MCP_TOKEN"):
        ctx.logger.info("🔑 OpenSea MCP token detected")
    else:
        ctx.logger.warning("🔒 No OPENSEA_MCP_TOKEN set. Set it to use real data.")
    ctx.logger.info("✨ Ready!")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("👋 Etherius MCP Agent shutting down")

# Protocol for programmatic usage
etherius_protocol = Protocol(name="etherius_mcp_protocol", version="1.1.0")

@etherius_protocol.on_message(model=MCPQuery)
async def handle_mcp_query(ctx: Context, sender: str, msg: MCPQuery):
    ctx.logger.info(f"📨 MCPQuery from {sender}: {msg.question}")
    session_id = f"session_{datetime.now(UTC).timestamp()}"

    limit = int(msg.limit or 10)
    chain = msg.chain

    # Resolve request type heuristically if not provided
    rtype = msg.request_type or _infer_request_type(msg.question)

    if rtype in (RequestType.QUESTION, RequestType.SEARCH_COLLECTIONS, RequestType.ANALYZE_COLLECTION):
        message, collections = await answer_user_question(ctx, msg.question, chain, limit)
        success = len(collections) > 0
        await ctx.send(sender, MCPAnswer(success=success, message=message, collections=collections, session_id=session_id))
        return

    await ctx.send(sender, MCPAnswer(success=False, message="Unsupported request type.", collections=None, session_id=session_id))

# Include protocol
agent.include(etherius_protocol, publish_manifest=True)

# ────────────────────────────────────────────────────────────────────────────────
# REST Endpoints
# ────────────────────────────────────────────────────────────────────────────────

@agent.on_rest_post("/chat", ChatRequest, ChatResponse)
async def chat_endpoint(ctx: Context, req: ChatRequest) -> ChatResponse:
    """
    Single chat endpoint:
      - Takes a natural language question
      - Uses OpenSea MCP to find relevant NFT collections
      - Returns a concise markdown table of results
    """
    ctx.logger.info(f"💬 Chat: {req.message}")
    message, collections = await answer_user_question(ctx, req.message, chain=None, limit=10)
    if collections:
        md = f"**{message}**\n\n" + format_collections_md(collections, max_rows=10)
    else:
        md = f"⚠️ {message}"
    return ChatResponse(response=md)

@agent.on_rest_get("/health", ChatResponse)
async def health_check(ctx: Context) -> ChatResponse:
    return ChatResponse(response="OK")

# ────────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(
        f"""
🌟 Etherius MCP Agent - OpenSea Collection Finder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Natural language → real OpenSea MCP collection data
• Streamable HTTP MCP client (JSON-RPC 2.0, protocol 2025-06-18)
• No payments; no mock data
• REST: POST /chat {{ "message": "Find gaming collections on Base" }}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    )
    agent.run()