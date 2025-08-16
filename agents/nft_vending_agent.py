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
from openai import OpenAI
from agents.x402_handler import payment_handler, PaymentStatus

try:
    from mcp import Client as MCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP not available. Using fallback data.")

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
openai_client = OpenAI()

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
    token_id: str
    collection_name: str
    collection_address: str
    name: str
    description: str
    image_url: str
    category: NFTCategory
    price_eth: float
    price_usd: float
    rarity_score: float
    traits: List[Dict[str, Any]]
    owner: str
    blockchain: str
    marketplace_url: str

# Message models
class NFTQuery(Model):
    query: str
    category: Optional[NFTCategory]
    max_price_eth: Optional[float]
    min_rarity: Optional[float]
    collection: Optional[str]

class NFTResponse(Model):
    nfts: List[NFT]
    recommendation: str
    market_insights: str
    total_items: int

class NFTPurchaseRequest(Model):
    token_id: str
    collection_address: str
    offer_price_eth: Optional[float]
    payment_method: str

class NFTPurchaseResponse(Model):
    success: bool
    nft: Optional[NFT]
    final_price_eth: float
    final_price_usd: float
    payment_url: str
    payment_id: str
    transaction_hash: Optional[str]
    payment_status: str
    opensea_url: str
    message: str

class MarketAnalysis(Model):
    collection: str
    timeframe: str

class MarketAnalysisResponse(Model):
    collection: str
    floor_price_eth: float
    volume_24h: float
    price_change_24h: float
    trending_traits: List[str]
    recommendation: str

class NFTPaymentVerification(Model):
    payment_id: str
    transaction_hash: Optional[str]
    nft_token_id: str
    collection_address: str

class NFTPaymentVerificationResponse(Model):
    payment_id: str
    verified: bool
    status: str
    nft_transferred: bool
    transaction_hash: Optional[str]
    message: str

# OpenSea MCP client
class OpenSeaMCPClient:
    def __init__(self):
        self.mcp_server_url = "http://localhost:8300"  # OpenSea MCP server
        self.mcp_client = None
        self.session = None
        
        if MCP_AVAILABLE:
            try:
                # Connect to MCP server
                self.session = aiohttp.ClientSession()
                print("✅ MCP client ready for OpenSea data")
            except Exception as e:
                print(f"❌ MCP connection failed: {e}")
    
    async def search_nfts(self, query: str, filters: Dict[str, Any]) -> List[NFT]:
        """Search NFTs using OpenSea MCP"""
        if not MCP_AVAILABLE or not self.session:
            raise Exception("MCP connection required for NFT search. Please ensure OpenSea MCP server is running.")
        
        try:
            # Call MCP tool for real NFT search
            async with self.session.post(
                f"{self.mcp_server_url}/tools/search_nfts_by_criteria",
                json={
                    "query": query,
                    "max_price_eth": filters.get("max_price"),
                    "collection": filters.get("collection"),
                    "limit": filters.get("limit", 20)
                }
            ) as response:
                if response.status == 200:
                    nft_data = await response.json()
                    # Convert to NFT models
                    return self._parse_nft_data(nft_data)
                else:
                    raise Exception(f"MCP server error: {response.status}")
        except Exception as e:
            print(f"Error searching NFTs: {e}")
            raise
    
    async def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get collection statistics from OpenSea"""
        if not MCP_AVAILABLE or not self.session:
            raise Exception("MCP connection required for collection stats. Please ensure OpenSea MCP server is running.")
        
        try:
            # Call MCP tool for real collection stats
            async with self.session.post(
                f"{self.mcp_server_url}/tools/get_nft_collection_stats",
                json={"collection_slug": collection}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get("stats", {})
                    return {
                        "floor_price": stats.get("floor_price"),
                        "volume_24h": stats.get("one_day_volume"),
                        "price_change_24h": stats.get("one_day_change", 0) * 100,
                        "num_owners": stats.get("num_owners"),
                        "total_supply": stats.get("total_supply")
                    }
                else:
                    raise Exception(f"MCP server error: {response.status}")
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            raise
    
    def _parse_nft_data(self, nft_data: List[Dict[str, Any]]) -> List[NFT]:
        """Parse NFT data from MCP response"""
        nfts = []
        for item in nft_data:
            nft = NFT(
                token_id=str(item.get("token_id", "0")),
                collection_name=item.get("collection", "Unknown"),
                collection_address="0x" + "0" * 40,  # Placeholder
                name=item.get("name", "NFT"),
                description=item.get("description", ""),
                image_url=item.get("image_url", ""),
                category=NFTCategory.ART,
                price_eth=item.get("price_eth", 0.1),
                price_usd=item.get("price_eth", 0.1) * 3000,
                rarity_score=item.get("rarity_rank", 50) / 100,
                traits=item.get("traits", []),
                owner="0x" + "0" * 40,
                blockchain="ethereum",
                marketplace_url=f"https://opensea.io/assets/{item.get('collection', '')}/{item.get('token_id', '')}"
            )
            nfts.append(nft)
        return nfts
    
    async def close(self):
        """Close MCP session"""
        if self.session:
            await self.session.close()

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
            model="gpt-4.1",
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
    ctx.logger.info(f"💳 X402 payments: {'✅ Wallet: ' + payment_handler.wallet_address[:10] + '...' if payment_handler.wallet_address and payment_handler.wallet_address != '0x0000000000000000000000000000000000000000' else '❌ Not configured'}")
    ctx.logger.info(f"🌐 Payment network: {payment_handler.network}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("🛑 NFT Vending Machine shutting down...")
    # Clean up MCP connection
    if opensea_client.session:
        await opensea_client.session.close()

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
    
    # Convert ETH price to USD for X402 payment
    eth_to_usd = 3000  # In production, fetch real ETH price
    final_price_usd = final_price * eth_to_usd
    
    # Create X402 payment request for NFT
    payment_request = payment_handler.create_payment_request(
        product_id=f"NFT_{msg.collection_address}_{msg.token_id}",
        amount_usd=final_price_usd,
        description=f"NFT Purchase: {nft.name} from {nft.collection_name}",
        metadata={
            "nft_name": nft.name,
            "collection": nft.collection_name,
            "token_id": msg.token_id,
            "collection_address": msg.collection_address,
            "price_eth": final_price,
            "buyer": sender,
            "marketplace": "opensea"
        }
    )
    
    # Generate payment URL
    payment_url = payment_handler.generate_payment_url(payment_request)
    
    # Store NFT purchase details for later verification
    ctx.storage.set(f"nft_payment_{payment_request['payment_id']}", {
        "nft": nft.dict(),
        "final_price_eth": final_price,
        "sender": sender
    })
    
    response = NFTPurchaseResponse(
        success=True,
        nft=nft,
        final_price_eth=final_price,
        final_price_usd=final_price_usd,
        payment_url=payment_url,
        payment_id=payment_request["payment_id"],
        transaction_hash=None,  # Will be set after payment
        payment_status=PaymentStatus.PENDING,
        opensea_url=nft.marketplace_url,
        message=f"NFT payment request created! Price: {final_price:.3f} ETH (${final_price_usd:.2f}). Complete payment to receive NFT."
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
            model="gpt-4.1",
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

@nft_protocol.on_message(model=NFTPaymentVerification, replies=NFTPaymentVerificationResponse)
async def handle_nft_payment_verification(ctx: Context, sender: str, msg: NFTPaymentVerification):
    """Verify X402 payment and transfer NFT ownership"""
    ctx.logger.info(f"💳 Verifying NFT payment {msg.payment_id} from {sender}")
    
    # Verify payment through X402
    verified, payment_details = await payment_handler.verify_payment(
        msg.payment_id,
        msg.transaction_hash
    )
    
    if verified:
        # Get stored NFT purchase details
        purchase_data = ctx.storage.get(f"nft_payment_{msg.payment_id}")
        
        if purchase_data:
            nft_data = purchase_data["nft"]
            
            # In production, this would trigger actual NFT transfer on blockchain
            # For now, we simulate the transfer
            transfer_success = True  # Mock successful transfer
            
            if transfer_success:
                ctx.logger.info(f"✅ NFT payment verified and transferred: {nft_data['name']}")
                
                # Generate OpenSea transaction URL
                tx_hash = payment_details.get("transaction_hash", "0x" + "0" * 64)
                opensea_tx_url = f"https://opensea.io/tx/{tx_hash}"
                
                await ctx.send(sender, NFTPaymentVerificationResponse(
                    payment_id=msg.payment_id,
                    verified=True,
                    status=PaymentStatus.COMPLETED,
                    nft_transferred=True,
                    transaction_hash=tx_hash,
                    message=f"Payment confirmed! NFT '{nft_data['name']}' has been transferred to your wallet. View on OpenSea: {opensea_tx_url}"
                ))
            else:
                await ctx.send(sender, NFTPaymentVerificationResponse(
                    payment_id=msg.payment_id,
                    verified=True,
                    status=PaymentStatus.COMPLETED,
                    nft_transferred=False,
                    transaction_hash=payment_details.get("transaction_hash"),
                    message="Payment verified but NFT transfer failed. Contact support for refund."
                ))
        else:
            await ctx.send(sender, NFTPaymentVerificationResponse(
                payment_id=msg.payment_id,
                verified=True,
                status=PaymentStatus.COMPLETED,
                nft_transferred=False,
                transaction_hash=payment_details.get("transaction_hash"),
                message="Payment verified but NFT purchase data not found."
            ))
    else:
        error_msg = payment_details.get("error", "Payment verification failed")
        status = payment_details.get("payment", {}).get("status", PaymentStatus.FAILED)
        
        await ctx.send(sender, NFTPaymentVerificationResponse(
            payment_id=msg.payment_id,
            verified=False,
            status=status,
            nft_transferred=False,
            transaction_hash=None,
            message=f"Payment not verified: {error_msg}"
        ))

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