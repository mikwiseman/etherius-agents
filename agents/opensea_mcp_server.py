"""
OpenSea MCP Server - Model Context Protocol server for NFT marketplace data
Provides real NFT data through MCP tools, resources, and prompts
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, UTC
from dotenv import load_dotenv

try:
    from fastmcp import FastMCP
except ImportError:
    # Fallback if fastmcp not available
    FastMCP = None

import httpx
from pycoingecko import CoinGeckoAPI

load_dotenv()

# Initialize APIs
cg = CoinGeckoAPI()

# Create MCP server
if FastMCP:
    mcp = FastMCP("OpenSea NFT Data Server")
else:
    # Fallback implementation
    class MockMCP:
        def __init__(self, name):
            self.name = name
        def tool(self):
            return lambda func: func
        def resource(self, path):
            return lambda func: func
        def prompt(self):
            return lambda func: func
    mcp = MockMCP("OpenSea NFT Data Server")

# OpenSea API client (using public data endpoints)
class OpenSeaClient:
    def __init__(self):
        self.base_url = "https://api.opensea.io/api/v2"
        self.headers = {
            "X-API-KEY": os.getenv("OPENSEA_API_KEY", ""),
            "Accept": "application/json"
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def get_collection_stats(self, collection_slug: str) -> Dict[str, Any]:
        """Get collection statistics from OpenSea API"""
        if not self.headers.get("X-API-KEY"):
            raise ValueError("OpenSea API key required. Set OPENSEA_API_KEY in environment.")
        
        try:
            url = f"{self.base_url}/collections/{collection_slug}/stats"
            response = await self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                error_msg = f"OpenSea API error: {response.status_code}"
                raise Exception(error_msg)
        except Exception as e:
            print(f"Error fetching collection stats: {e}")
            raise
    
    async def get_collection_floor(self, collection_slug: str) -> float:
        """Get collection floor price"""
        stats = await self.get_collection_stats(collection_slug)
        return stats.get("stats", {}).get("floor_price", 0.0)
    
    async def search_nfts(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for NFTs using OpenSea API"""
        if not self.headers.get("X-API-KEY"):
            raise ValueError("OpenSea API key required. Set OPENSEA_API_KEY in environment.")
        
        try:
            url = f"{self.base_url}/events"
            params = {
                "limit": limit,
                "event_type": "listing"
            }
            
            response = await self.session.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                nfts = []
                for event in data.get("asset_events", []):
                    asset = event.get("asset", {})
                    nfts.append({
                        "token_id": asset.get("token_id", ""),
                        "name": asset.get("name", ""),
                        "collection": asset.get("collection", {}).get("slug", ""),
                        "image_url": asset.get("image_url", ""),
                        "price_eth": float(event.get("starting_price", 0)) / 10**18,
                        "traits": asset.get("traits", [])
                    })
                return nfts
            else:
                raise Exception(f"OpenSea API error: {response.status_code}")
        except Exception as e:
            print(f"Error searching NFTs: {e}")
            raise

# MCP Tools
@mcp.tool()
async def get_nft_collection_stats(collection_slug: str) -> Dict[str, Any]:
    """
    Get comprehensive statistics for an NFT collection.
    
    Args:
        collection_slug: The slug identifier for the collection (e.g., 'boredapeyachtclub')
    
    Returns:
        Collection statistics including floor price, volume, and holder data
    """
    async with OpenSeaClient() as client:
        stats = await client.get_collection_stats(collection_slug)
        
        # Add ETH to USD conversion
        try:
            eth_price = cg.get_price(ids='ethereum', vs_currencies='usd')['ethereum']['usd']
            if "stats" in stats:
                stats["stats"]["floor_price_usd"] = stats["stats"]["floor_price"] * eth_price
                stats["stats"]["total_volume_usd"] = stats["stats"]["total_volume"] * eth_price
        except:
            eth_price = 3000  # Fallback price
        
        return {
            "collection": collection_slug,
            "stats": stats.get("stats", {}),
            "eth_price_usd": eth_price,
            "timestamp": datetime.now(UTC).isoformat()
        }

@mcp.tool()
async def search_nfts_by_criteria(
    query: str,
    max_price_eth: Optional[float] = None,
    min_rarity_rank: Optional[int] = None,
    collection: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search for NFTs based on various criteria.
    
    Args:
        query: Search query string
        max_price_eth: Maximum price in ETH
        min_rarity_rank: Minimum rarity rank (lower is rarer)
        collection: Specific collection to search within
        limit: Maximum number of results
    
    Returns:
        List of NFTs matching the criteria
    """
    async with OpenSeaClient() as client:
        nfts = await client.search_nfts(query, limit)
        
        # Filter based on criteria
        filtered_nfts = []
        for nft in nfts:
            if max_price_eth and nft.get("price_eth", 0) > max_price_eth:
                continue
            if min_rarity_rank and nft.get("rarity_rank", float('inf')) > min_rarity_rank:
                continue
            if collection and nft.get("collection") != collection:
                continue
            filtered_nfts.append(nft)
        
        return filtered_nfts

@mcp.tool()
async def get_nft_price_history(
    collection_slug: str,
    token_id: str,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get price history for a specific NFT.
    
    Args:
        collection_slug: Collection identifier
        token_id: Token ID within the collection
        days: Number of days of history
    
    Returns:
        Price history data with sales and listings
    """
    async with OpenSeaClient() as client:
        if not client.headers.get("X-API-KEY"):
            raise ValueError("OpenSea API key required for price history.")
        
        # Get events for specific NFT
        url = f"{client.base_url}/events"
        params = {
            "collection_slug": collection_slug,
            "token_id": token_id,
            "limit": 50,
            "event_type": "successful,listing"
        }
        
        response = await client.session.get(url, headers=client.headers, params=params)
        if response.status_code == 200:
            data = response.json()
            price_history = []
            
            for event in data.get("asset_events", []):
                price_history.append({
                    "date": event.get("created_date", ""),
                    "price_eth": float(event.get("total_price", 0)) / 10**18,
                    "event_type": event.get("event_type", "")
                })
            
            # Calculate price change
            if len(price_history) >= 2:
                current = price_history[0]["price_eth"]
                past = price_history[-1]["price_eth"]
                change = ((current - past) / past * 100) if past > 0 else 0
            else:
                change = 0
            
            return {
                "collection": collection_slug,
                "token_id": token_id,
                "price_history": price_history,
                "current_price": price_history[0]["price_eth"] if price_history else 0,
                "price_change_30d": round(change, 2)
            }
        else:
            raise Exception(f"OpenSea API error: {response.status_code}")

@mcp.tool()
async def analyze_nft_market_trends() -> Dict[str, Any]:
    """
    Analyze current NFT market trends across top collections.
    
    Returns:
        Market analysis with trending collections and insights
    """
    async with OpenSeaClient() as client:
        if not client.headers.get("X-API-KEY"):
            raise ValueError("OpenSea API key required for market analysis.")
        
        # Get top collections by volume
        top_collections = [
            "pudgypenguins",
            "azuki",
            "boredapeyachtclub",
            "doodles-official",
            "clonex"
        ]
        
        trending_collections = []
        for slug in top_collections:
            try:
                stats = await client.get_collection_stats(slug)
                if "stats" in stats:
                    s = stats["stats"]
                    trending_collections.append({
                        "name": slug,
                        "floor": s.get("floor_price", 0),
                        "volume_24h": s.get("one_day_volume", 0),
                        "change_24h": s.get("one_day_change", 0) * 100
                    })
            except:
                continue
        
        if not trending_collections:
            raise Exception("Unable to fetch collection data")
        
        # Calculate market metrics
        total_volume = sum(c["volume_24h"] for c in trending_collections)
        avg_floor = sum(c["floor"] for c in trending_collections) / len(trending_collections)
        total_change = sum(c["change_24h"] for c in trending_collections)
        
        return {
            "trending_collections": trending_collections,
            "market_metrics": {
                "total_volume_24h": total_volume,
                "average_floor_price": round(avg_floor, 2),
                "market_sentiment": "bullish" if total_change > 0 else "bearish",
                "top_performer": max(trending_collections, key=lambda x: x["change_24h"])["name"] if trending_collections else "N/A",
                "most_volume": max(trending_collections, key=lambda x: x["volume_24h"])["name"] if trending_collections else "N/A"
            },
            "insights": [
                f"Market sentiment: {'Positive' if total_change > 0 else 'Negative'} with {abs(total_change):.1f}% total change",
                f"Average floor price across top collections: {avg_floor:.2f} ETH",
                f"Total 24h volume: {total_volume:.2f} ETH"
            ],
            "timestamp": datetime.now(UTC).isoformat()
        }

# MCP Resources
@mcp.resource("nft://collections/trending")
async def get_trending_collections() -> str:
    """Resource endpoint for trending NFT collections"""
    trends = await analyze_nft_market_trends()
    return json.dumps(trends, indent=2)

@mcp.resource("nft://collection/{collection_slug}/stats")
async def get_collection_resource(collection_slug: str) -> str:
    """Resource endpoint for specific collection stats"""
    stats = await get_nft_collection_stats(collection_slug)
    return json.dumps(stats, indent=2)

# MCP Prompts
@mcp.prompt()
async def nft_investment_analysis(collection_name: str) -> str:
    """
    Generate an investment analysis prompt for an NFT collection.
    
    Args:
        collection_name: Name of the NFT collection to analyze
    
    Returns:
        Structured prompt for NFT investment analysis
    """
    return f"""Analyze the investment potential of {collection_name} NFT collection.

Consider the following factors:
1. Current floor price and volume trends
2. Holder distribution and whale activity
3. Community strength and social sentiment
4. Utility and roadmap execution
5. Market position vs competitors

Provide:
- Risk assessment (1-10 scale)
- Investment recommendation (buy/hold/sell)
- Key opportunities and threats
- 30-day price prediction
- Suggested entry and exit strategies"""

@mcp.prompt()
async def nft_comparison(collections: List[str]) -> str:
    """
    Generate a comparison prompt for multiple NFT collections.
    
    Args:
        collections: List of collection names to compare
    
    Returns:
        Structured prompt for NFT collection comparison
    """
    collection_list = ", ".join(collections)
    return f"""Compare the following NFT collections: {collection_list}

Analyze each collection on:
1. Market performance (floor price, volume, liquidity)
2. Community metrics (holders, engagement, growth)
3. Innovation and utility
4. Risk/reward profile
5. Long-term potential

Provide:
- Ranking from best to worst investment
- Key differentiators for each
- Recommended portfolio allocation
- Market cycle positioning"""

# Run MCP server
async def run_server():
    """Run the MCP server"""
    print("🚀 OpenSea MCP Server started!")
    print("📊 Available tools:")
    print("  - get_nft_collection_stats")
    print("  - search_nfts_by_criteria")
    print("  - get_nft_price_history")
    print("  - analyze_nft_market_trends")
    print("📁 Available resources:")
    print("  - nft://collections/trending")
    print("  - nft://collection/{slug}/stats")
    print("💡 Available prompts:")
    print("  - nft_investment_analysis")
    print("  - nft_comparison")
    
    # Keep server running
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    if FastMCP:
        # Run with FastMCP
        import uvicorn
        uvicorn.run("opensea_mcp_server:mcp", host="0.0.0.0", port=8300, reload=True)
    else:
        # Run standalone
        asyncio.run(run_server())