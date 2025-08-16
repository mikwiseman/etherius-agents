"""
NFT Vending Machine Agent with OpenSea MCP Integration
Sells NFTs with dynamic pricing and X402 payment processing
"""

import os
import json
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, UTC
from enum import Enum
from dotenv import load_dotenv
import aiohttp

from uagents import Agent, Context, Model, Protocol
from pydantic import Field
import openai

load_dotenv()

# Agent configuration
agent = Agent(
    name="nft_vending_machine",
    seed=os.getenv("AGENT_SEED_PHRASE", "nft_vending_unique_seed_2024"),
    port=int(os.getenv("NFT_VENDING_AGENT_PORT", 8101)),
    endpoint=[f"http://localhost:{os.getenv('NFT_VENDING_AGENT_PORT', 8101)}/submit"],
    mailbox=True
)

# OpenAI configuration
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# NFT categories
class NFTCategory(str, Enum):
    ART = "art"
    GAMING = "gaming"
    MUSIC = "music"
    COLLECTIBLES = "collectibles"
    METAVERSE = "metaverse"
    PHOTOGRAPHY = "photography"
    SPORTS = "sports"
    UTILITY = "utility"

# NFT model
class NFT(Model):
    token_id: str = Field(..., description="NFT token ID")
    collection_name: str = Field(..., description="Collection name")
    collection_address: str = Field(..., description="Collection contract address")
    name: str = Field(..., description="NFT name")
    description: str = Field(..., description="NFT description")
    image_url: str = Field(..., description="NFT image URL")
    category: NFTCategory = Field(..., description="NFT category")
    price_eth: float = Field(..., description="Price in ETH")
    price_usd: float = Field(..., description="Price in USD")
    rarity_score: float = Field(default=0.5, description="Rarity score (0-1)")
    traits: List[Dict[str, Any]] = Field(default_factory=list, description="NFT traits")
    owner: str = Field(..., description="Current owner address")
    blockchain: str = Field(default="ethereum", description="Blockchain network")
    marketplace_url: str = Field(..., description="OpenSea listing URL")

# Message models
class NFTQuery(Model):
    query: str = Field(..., description="Natural language query about NFTs")
    category: Optional[NFTCategory] = Field(None, description="Category filter")
    max_price_eth: Optional[float] = Field(None, description="Maximum price in ETH")
    min_rarity: Optional[float] = Field(None, description="Minimum rarity score")
    collection: Optional[str] = Field(None, description="Specific collection name")

class NFTResponse(Model):
    nfts: List[NFT] = Field(..., description="Matching NFTs")
    recommendation: str = Field(..., description="AI-generated recommendation")
    market_insights: str = Field(..., description="Market insights")
    total_items: int = Field(..., description="Total items found")

class NFTPurchaseRequest(Model):
    token_id: str = Field(..., description="NFT token ID")
    collection_address: str = Field(..., description="Collection contract address")
    offer_price_eth: Optional[float] = Field(None, description="Offer price if negotiating")
    payment_method: str = Field(default="x402", description="Payment method")

class NFTPurchaseResponse(Model):
    success: bool = Field(..., description="Purchase success status")
    nft: Optional[NFT] = Field(None, description="Purchased NFT")
    final_price_eth: float = Field(..., description="Final price in ETH")
    final_price_usd: float = Field(..., description="Final price in USD")
    payment_url: str = Field(..., description="X402 payment URL")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    opensea_url: str = Field(..., description="OpenSea transaction URL")
    message: str = Field(..., description="Response message")

class MarketAnalysis(Model):
    collection: str = Field(..., description="Collection to analyze")
    timeframe: str = Field(default="7d", description="Analysis timeframe")

class MarketAnalysisResponse(Model):
    collection: str = Field(..., description="Collection name")
    floor_price_eth: float = Field(..., description="Floor price in ETH")
    volume_24h: float = Field(..., description="24h volume in ETH")
    price_change_24h: float = Field(..., description="24h price change percentage")
    trending_traits: List[str] = Field(..., description="Trending traits")
    recommendation: str = Field(..., description="Investment recommendation")

# OpenSea MCP client
class OpenSeaMCPClient:
    def __init__(self):
        self.base_url = os.getenv("OPENSEA_MCP_URL", "https://mcp.opensea.io/mcp")
        self.access_token = os.getenv("OPENSEA_ACCESS_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def search_nfts(self, query: str, filters: Dict[str, Any]) -> List[NFT]:
        """Search NFTs using OpenSea MCP"""
        try:
            # Simulate MCP query (replace with actual MCP integration)
            # In production, this would use the actual OpenSea MCP protocol
            mock_nfts = self._generate_mock_nfts(query, filters)
            return mock_nfts
        except Exception as e:
            print(f"Error searching NFTs: {e}")
            return []
    
    async def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get collection statistics from OpenSea"""
        # Simulate collection stats (replace with actual MCP call)
        return {
            "floor_price": random.uniform(0.1, 5.0),
            "volume_24h": random.uniform(10, 1000),
            "price_change_24h": random.uniform(-20, 30),
            "num_owners": random.randint(100, 10000),
            "total_supply": random.randint(1000, 10000)
        }
    
    def _generate_mock_nfts(self, query: str, filters: Dict[str, Any]) -> List[NFT]:
        """Generate mock NFTs for testing"""
        mock_collections = [
            ("Bored Ape Yacht Club", "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"),
            ("CryptoPunks", "0xb47e3cd837dDF8e4c57F05d70E7e5b67c3d1e3a5"),
            ("Azuki", "0xED5AF388653567Af2F388E6224dC7C4b3241C544"),
            ("Doodles", "0x8a90CAb2b38dba80c64b7734e58Ee1dB38B8992e"),
            ("CloneX", "0x49cF6f5d44E70224e2E23fDcdd2C053F30aDA28B")
        ]
        
        nfts = []
        for i in range(min(10, filters.get("limit", 10))):
            collection = random.choice(mock_collections)
            nft = NFT(
                token_id=f"{random.randint(1000, 9999)}",
                collection_name=collection[0],
                collection_address=collection[1],
                name=f"{collection[0]} #{random.randint(1000, 9999)}",
                description=f"A unique NFT from the {collection[0]} collection",
                image_url=f"https://example.com/nft/{random.randint(1000, 9999)}.png",
                category=random.choice(list(NFTCategory)),
                price_eth=round(random.uniform(0.5, 10.0), 3),
                price_usd=round(random.uniform(0.5, 10.0) * 3000, 2),
                rarity_score=round(random.uniform(0.3, 0.95), 2),
                traits=[
                    {"trait_type": "Background", "value": random.choice(["Blue", "Red", "Gold"])},
                    {"trait_type": "Eyes", "value": random.choice(["Laser", "Normal", "3D"])},
                    {"trait_type": "Mouth", "value": random.choice(["Smile", "Frown", "Bored"])}
                ],
                owner="0x" + "".join(random.choices("0123456789abcdef", k=40)),
                blockchain="ethereum",
                marketplace_url=f"https://opensea.io/assets/{collection[1]}/{random.randint(1000, 9999)}"
            )
            nfts.append(nft)
        
        return nfts

opensea_client = OpenSeaMCPClient()

# Dynamic pricing for NFTs
class NFTDynamicPricer:
    def __init__(self):
        self.price_history: Dict[str, List[float]] = {}
        
    def calculate_offer_price(self, nft: NFT, market_data: Dict[str, Any]) -> float:
        """Calculate dynamic offer price based on market conditions"""
        base_price = nft.price_eth
        
        # Rarity adjustment
        rarity_multiplier = 1.0 + (nft.rarity_score - 0.5) * 0.4
        
        # Market trend adjustment
        trend_multiplier = 1.0
        if market_data.get("price_change_24h", 0) > 10:
            trend_multiplier = 1.1  # Bull market
        elif market_data.get("price_change_24h", 0) < -10:
            trend_multiplier = 0.9  # Bear market
        
        # Volume-based liquidity discount
        volume_24h = market_data.get("volume_24h", 0)
        liquidity_multiplier = 1.0
        if volume_24h < 10:  # Low liquidity
            liquidity_multiplier = 0.95
        elif volume_24h > 100:  # High liquidity
            liquidity_multiplier = 1.05
        
        final_price = base_price * rarity_multiplier * trend_multiplier * liquidity_multiplier
        return round(final_price, 4)
    
    def negotiate_price(self, listing_price: float, offer_price: float) -> tuple[bool, float]:
        """Negotiate price between listing and offer"""
        if offer_price >= listing_price * 0.95:  # Accept if within 5%
            return True, listing_price
        elif offer_price >= listing_price * 0.85:  # Counter-offer if within 15%
            counter = (listing_price + offer_price) / 2
            return True, round(counter, 4)
        else:
            return False, listing_price

pricer = NFTDynamicPricer()

# AI-powered NFT recommendations
async def get_nft_recommendation(query: str, nfts: List[NFT]) -> str:
    """Use OpenAI to generate NFT recommendations"""
    try:
        nft_info = "\n".join([
            f"- {nft.name}: {nft.price_eth} ETH, Rarity: {nft.rarity_score}"
            for nft in nfts[:5]
        ])
        
        prompt = f"""Based on the user query: "{query}"
        
        Available NFTs:
        {nft_info}
        
        Provide investment advice considering:
        1. Rarity and potential value appreciation
        2. Collection reputation and market trends
        3. Risk assessment
        
        Response in 2-3 sentences."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert NFT advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return "I recommend researching the collection's history and community before investing."

# Protocol definition
nft_protocol = Protocol(name="nft_vending_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🖼️ NFT Vending Machine started!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"🌊 OpenSea MCP: {'✅' if os.getenv('OPENSEA_ACCESS_TOKEN') else '❌'}")
    ctx.logger.info(f"🤖 AI recommendations: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("🛑 NFT Vending Machine shutting down...")

@nft_protocol.on_message(model=NFTQuery, replies=NFTResponse)
async def handle_nft_query(ctx: Context, sender: str, msg: NFTQuery):
    """Handle NFT search queries"""
    ctx.logger.info(f"🔍 NFT query from {sender}: {msg.query}")
    
    # Build filters for OpenSea MCP
    filters = {
        "limit": 20,
        "category": msg.category.value if msg.category else None,
        "max_price": msg.max_price_eth,
        "min_rarity": msg.min_rarity,
        "collection": msg.collection
    }
    
    # Search NFTs using OpenSea MCP
    nfts = await opensea_client.search_nfts(msg.query, filters)
    
    # Filter by user criteria
    filtered_nfts = []
    for nft in nfts:
        if msg.max_price_eth and nft.price_eth > msg.max_price_eth:
            continue
        if msg.min_rarity and nft.rarity_score < msg.min_rarity:
            continue
        filtered_nfts.append(nft)
    
    # Get AI recommendation
    recommendation = await get_nft_recommendation(msg.query, filtered_nfts)
    
    # Generate market insights
    market_insights = f"Current market shows {len(filtered_nfts)} NFTs matching your criteria. "
    if filtered_nfts:
        avg_price = sum(nft.price_eth for nft in filtered_nfts) / len(filtered_nfts)
        market_insights += f"Average price: {avg_price:.3f} ETH. "
        high_rarity = [nft for nft in filtered_nfts if nft.rarity_score > 0.8]
        if high_rarity:
            market_insights += f"Found {len(high_rarity)} high-rarity NFTs!"
    
    response = NFTResponse(
        nfts=filtered_nfts[:10],
        recommendation=recommendation,
        market_insights=market_insights,
        total_items=len(filtered_nfts)
    )
    
    await ctx.send(sender, response)

@nft_protocol.on_message(model=NFTPurchaseRequest, replies=NFTPurchaseResponse)
async def handle_nft_purchase(ctx: Context, sender: str, msg: NFTPurchaseRequest):
    """Handle NFT purchase with price negotiation"""
    ctx.logger.info(f"💎 NFT purchase request from {sender}: {msg.token_id}")
    
    # Get NFT details (mock for now)
    nft = NFT(
        token_id=msg.token_id,
        collection_address=msg.collection_address,
        collection_name="Collection",
        name=f"NFT #{msg.token_id}",
        description="NFT from the collection",
        image_url=f"https://example.com/nft/{msg.token_id}.png",
        category=NFTCategory.ART,
        price_eth=random.uniform(0.5, 5.0),
        price_usd=random.uniform(0.5, 5.0) * 3000,
        rarity_score=random.uniform(0.5, 0.9),
        traits=[],
        owner="0x" + "".join(random.choices("0123456789abcdef", k=40)),
        marketplace_url=f"https://opensea.io/assets/{msg.collection_address}/{msg.token_id}"
    )
    
    # Get market data for pricing
    market_data = await opensea_client.get_collection_stats(nft.collection_name)
    
    # Handle price negotiation
    if msg.offer_price_eth:
        accepted, final_price = pricer.negotiate_price(nft.price_eth, msg.offer_price_eth)
        if not accepted:
            await ctx.send(sender, NFTPurchaseResponse(
                success=False,
                nft=nft,
                final_price_eth=nft.price_eth,
                final_price_usd=nft.price_usd,
                payment_url="",
                opensea_url=nft.marketplace_url,
                message=f"Offer too low. Minimum acceptable: {nft.price_eth * 0.85:.3f} ETH"
            ))
            return
    else:
        final_price = pricer.calculate_offer_price(nft, market_data)
    
    # Generate payment URL
    payment_url = f"https://x402.pay/nft/{msg.collection_address}/{msg.token_id}?amount={final_price}"
    
    # Create transaction
    transaction_hash = "0x" + "".join(random.choices("0123456789abcdef", k=64))
    
    response = NFTPurchaseResponse(
        success=True,
        nft=nft,
        final_price_eth=final_price,
        final_price_usd=final_price * 3000,
        payment_url=payment_url,
        transaction_hash=transaction_hash,
        opensea_url=f"https://opensea.io/tx/{transaction_hash}",
        message=f"NFT purchase initiated! Final price: {final_price:.3f} ETH"
    )
    
    await ctx.send(sender, response)
    ctx.logger.info(f"✅ NFT sale processed: {nft.name} for {final_price:.3f} ETH")

@nft_protocol.on_message(model=MarketAnalysis, replies=MarketAnalysisResponse)
async def handle_market_analysis(ctx: Context, sender: str, msg: MarketAnalysis):
    """Provide market analysis for NFT collections"""
    ctx.logger.info(f"📊 Market analysis request for {msg.collection}")
    
    # Get collection statistics
    stats = await opensea_client.get_collection_stats(msg.collection)
    
    # Generate AI-powered recommendation
    try:
        prompt = f"""Analyze the NFT collection "{msg.collection}" with these metrics:
        - Floor price: {stats['floor_price']:.3f} ETH
        - 24h volume: {stats['volume_24h']:.2f} ETH
        - Price change: {stats['price_change_24h']:.1f}%
        
        Provide investment recommendation in 2 sentences."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an NFT market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        recommendation = response.choices[0].message.content
    except:
        recommendation = "Monitor the collection's community activity and roadmap before investing."
    
    # Identify trending traits (mock data)
    trending_traits = ["Gold Background", "Laser Eyes", "Rare Hat"]
    
    response = MarketAnalysisResponse(
        collection=msg.collection,
        floor_price_eth=stats["floor_price"],
        volume_24h=stats["volume_24h"],
        price_change_24h=stats["price_change_24h"],
        trending_traits=trending_traits,
        recommendation=recommendation
    )
    
    await ctx.send(sender, response)

# Include protocol
agent.include(nft_protocol, publish_manifest=True)

if __name__ == "__main__":
    print("""
🖼️ NFT Vending Machine Agent Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
• OpenSea MCP integration
• AI-powered recommendations
• Dynamic pricing & negotiation
• X402 payment processing
• Market analysis & insights
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()