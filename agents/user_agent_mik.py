"""
User Agent Mik - The Street-Smart Trader
Character: Practical, profit-focused, trend-aware
Knows all the alpha, follows whale wallets, master negotiator
"""

import os
import sys
import random
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, UTC, timedelta
from dotenv import load_dotenv

from uagents import Agent, Context, Model, Protocol
from uagents.storage import StorageAPI

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocols.collaboration_protocol import (
    collaboration_protocol,
    StrategyDiscussion,
    AgentOpinion,
    VendingQuery,
    VendingResponse,
    ConsensusRequest,
    ConsensusResponse,
    BroadcastMessage,
    OpinionStrength,
    DiscussionType,
    NegotiationProposal,
    NegotiationResponse,
    create_strategy_discussion,
    create_agent_opinion
)

load_dotenv()

# Agent configuration
agent = Agent(
    name="mik_the_trader",
    seed=os.getenv("MIK_SEED", "mik_street_smart_trader_seed_2024"),
    port=int(os.getenv("MIK_PORT", 8202)),
    endpoint=[f"http://localhost:{os.getenv('MIK_PORT', 8202)}/submit"],
    mailbox=True
)

# Mik's character and personality
CHARACTER = {
    "name": "Mik",
    "personality": "Street-Smart Trader",
    "emoji": "💰",
    "traits": {
        "focus": "profit and trends",
        "risk_tolerance": 0.7,
        "preferred_holding": "flip quickly",
        "expertise": ["trading", "arbitrage", "whale-watching", "market-timing", "negotiation"],
        "investment_style": "momentum_trading",
        "time_horizon": "hours_to_days"
    },
    "catchphrases": [
        "I know a guy who knows a guy...",
        "The whales are moving, we should too",
        "I can get us a better deal, trust me",
        "Trust me bro, this is about to moon",
        "I've seen this pattern before, easy 10x",
        "My insider says big news coming",
        "Floor's about to pump, I can feel it",
        "Weak hands are selling, time to buy",
        "Diamond hands only from here",
        "LFG! We're gonna make it!",
        "Probably nothing... but actually something"
    ],
    "preferences": {
        "loves": ["quick flips", "trending collections", "whale movements", "arbitrage", "insider alpha"],
        "likes": ["momentum plays", "volume spikes", "FOMO rallies", "degen plays"],
        "neutral": ["long-term holds", "fundamentals"],
        "dislikes": ["slow movers", "low volume", "bear markets"],
        "avoids": ["obvious rugs", "dead projects", "no liquidity"]
    },
    "trading_signals": {
        "buy": ["whale accumulation", "volume spike", "floor sweep", "influencer mention"],
        "sell": ["whale dumping", "declining volume", "FUD spreading", "team selling"],
        "hold": ["sideways action", "accumulation phase", "waiting for catalyst"]
    }
}

# Vending agent addresses
VENDING_AGENTS = {
    "nft_analyzer": os.getenv("NFT_ANALYZER_ADDRESS", "agent1q..."),
    "nft_vending": os.getenv("NFT_VENDING_ADDRESS", "agent1q..."),
    "memecoin_generator": os.getenv("MEMECOIN_GENERATOR_ADDRESS", "agent1q...")
}

# Other user agent addresses
USER_AGENTS = {
    "kartik": None,
    "vitalik": None
}

# Mik's trading brain
class MikBrain:
    def __init__(self):
        self.current_session: Optional[str] = None
        self.discussion_history: List[StrategyDiscussion] = []
        self.vending_responses: Dict[str, VendingResponse] = {}
        self.whale_alerts: List[Dict[str, Any]] = []
        self.hot_tips: List[str] = []
        self.negotiation_history: Dict[str, float] = {}
        
    def analyze_momentum(self, data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze momentum and trading signals"""
        momentum_score = 0.0
        signals = []
        
        # Check for volume spikes
        if "volume" in str(data).lower():
            volume_val = random.uniform(0, 100)  # Simulated volume
            if volume_val > 70:
                momentum_score += 0.35
                signals.append("Volume pumping! 🚀")
                
        # Check for whale activity
        if "whale" in str(data).lower() or random.random() > 0.6:
            momentum_score += 0.25
            signals.append("Whales are accumulating")
            
        # Check for trending status
        if any(word in str(data).lower() for word in ["trending", "hot", "viral"]):
            momentum_score += 0.2
            signals.append("It's trending on Twitter")
            
        # Check for price action
        if random.random() > 0.5:  # Simulated price action
            momentum_score += 0.15
            signals.append("Chart looking bullish AF")
            
        # Insider info (Mik always has some)
        if random.random() > 0.7:
            momentum_score += 0.15
            signals.append("My insider says announcement coming")
            
        return momentum_score, signals
    
    def calculate_flip_potential(self, entry_price: float, data: Dict[str, Any]) -> Tuple[float, str]:
        """Calculate quick flip potential"""
        momentum, _ = self.analyze_momentum(data)
        
        # Mik's aggressive profit targets
        if momentum > 0.7:
            target = entry_price * random.uniform(2, 5)  # 2-5x target
            timeframe = "24-48 hours"
        elif momentum > 0.5:
            target = entry_price * random.uniform(1.5, 2)  # 50-100% gain
            timeframe = "3-5 days"
        else:
            target = entry_price * random.uniform(1.2, 1.5)  # 20-50% gain
            timeframe = "1 week max"
            
        return target, timeframe
    
    def negotiate_price(self, asking_price: float, data: Dict[str, Any]) -> Tuple[float, str]:
        """Negotiate like a street trader"""
        # Mik always tries to get a better deal
        momentum, _ = self.analyze_momentum(data)
        
        if momentum > 0.7:
            # High momentum, willing to pay more
            offer = asking_price * 0.95
            tactic = "This is hot, but I can get it cheaper elsewhere"
        else:
            # Lower momentum, aggressive negotiation
            offer = asking_price * 0.75
            tactic = "Floor's about to dump, take my offer or get stuck"
            
        return offer, tactic
    
    def analyze_opportunity(self, data: Dict[str, Any]) -> Tuple[OpinionStrength, float, str]:
        """Analyze from trader's perspective"""
        momentum, signals = self.analyze_momentum(data)
        
        # Mik's opinion based on momentum
        if momentum >= 0.7:
            strength = OpinionStrength.STRONG_BUY
            opinion = f"This is it! {' '.join(signals)}. Aping in NOW!"
            confidence = 0.9  # Mik is always confident when he smells profit
        elif momentum >= 0.5:
            strength = OpinionStrength.BUY
            opinion = f"Looking juicy! {' '.join(signals[:2]) if signals else 'Good entry here'}."
            confidence = 0.75
        elif momentum >= 0.3:
            strength = OpinionStrength.NEUTRAL
            opinion = "Meh, might pump but I've seen better setups."
            confidence = 0.5
        else:
            strength = OpinionStrength.SELL
            opinion = "Nah, this is going to zero. I'm out."
            confidence = 0.8
            
        return strength, confidence, opinion
    
    def propose_degen_allocation(self, total_eth: float, opportunities: List[Dict]) -> Dict[str, float]:
        """Propose aggressive allocation for maximum gains"""
        allocation = {}
        
        # Mik goes heavy on hot plays
        allocation["hot_play_1"] = total_eth * 0.4  # 40% on the hottest play
        allocation["hot_play_2"] = total_eth * 0.25  # 25% on second best
        allocation["quick_flip"] = total_eth * 0.2  # 20% for quick flips
        allocation["yolo_play"] = total_eth * 0.1  # 10% pure gambling
        allocation["gas_money"] = total_eth * 0.05  # 5% for fees and emergencies
        
        return allocation
    
    def generate_trade_plan(self) -> Dict[str, Any]:
        """Generate Mik's trading plan"""
        return {
            "entry": "Buy the fear, sell the greed",
            "targets": ["25% at 2x", "25% at 3x", "Let the rest ride"],
            "stop_loss": "What's a stop loss? Diamond hands only",
            "timeframe": "Quick flip, 1-7 days max",
            "risk_level": "Full degen mode activated"
        }

mik_brain = MikBrain()

# Mik's protocol implementation
mik_protocol = Protocol(name="mik_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"{CHARACTER['emoji']} Mik the Trader starting up!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"💰 Personality: {CHARACTER['personality']}")
    ctx.logger.info(f"🎯 Focus: {CHARACTER['traits']['focus']}")
    ctx.logger.info(f"📊 Risk Tolerance: {CHARACTER['traits']['risk_tolerance']} (YOLO)")
    ctx.logger.info(f"🚀 Ready to find the next 100x! LFG!")
    
    # Store agent info
    ctx.storage.set("character", CHARACTER)
    ctx.storage.set("agent_address", agent.address)
    
    # Initialize with some hot tips
    mik_brain.hot_tips = [
        "Heard about a stealth mint tomorrow",
        "Whale wallet just swept the floor",
        "Big influencer about to shill this"
    ]

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info(f"{CHARACTER['emoji']} Mik out! Remember: always DYOR (but also trust me bro)")

@mik_protocol.on_message(model=BroadcastMessage)
async def handle_broadcast(ctx: Context, sender: str, msg: BroadcastMessage):
    """Handle broadcast message from central hub"""
    ctx.logger.info(f"📡 Yo! New opportunity: {msg.user_query}")
    
    # Store session
    mik_brain.current_session = msg.session_id
    
    # Mik's immediate reaction
    if any(word in msg.user_query.lower() for word in ["quick", "fast", "pump", "moon", "10x"]):
        initial_thought = "This is what I live for! Let me check what the whales are doing..."
    elif "strategy" in msg.user_query.lower():
        initial_thought = "Strategy? Buy low, sell high, and always follow the whales!"
    else:
        initial_thought = f"Alright, let me work my magic. {random.choice(mik_brain.hot_tips)}"
    
    # Query vending agents for hot deals
    ctx.logger.info(f"🔍 Mik checking for arbitrage opportunities...")
    
    # Query NFT Vending for best deals
    if VENDING_AGENTS["nft_vending"] != "agent1q...":
        vending_query = VendingQuery(
            query_type="hot_deals",
            parameters={
                "sort": "momentum",
                "timeframe": "1h",
                "min_volume": 10,
                "check_whales": True
            },
            requesting_agent="Mik",
            agent_personality="Street-Smart Trader",
            urgency="high",  # Mik always in a hurry
            session_id=msg.session_id
        )
        await ctx.send(VENDING_AGENTS["nft_vending"], vending_query)
    
    # Create initial discussion
    initial_discussion = create_strategy_discussion(
        agent_name="Mik",
        personality="Street-Smart Trader",
        message=f"{initial_thought} I'm seeing {random.randint(3, 7)} solid plays right now.",
        session_id=msg.session_id,
        discussion_type=DiscussionType.STRATEGY,
        risk="high_risk_high_reward",
        recommendations=["Follow the whales", "Buy the rumor", "Take profits quickly", "DYOR but also trust me bro"]
    )
    
    # Send to other user agents
    for agent_name, address in USER_AGENTS.items():
        if address:
            await ctx.send(address, initial_discussion)

@mik_protocol.on_message(model=StrategyDiscussion)
async def handle_strategy_discussion(ctx: Context, sender: str, msg: StrategyDiscussion):
    """Handle strategy discussion from other user agents"""
    ctx.logger.info(f"💬 Mik heard {msg.agent_name}: {msg.message[:100]}")
    
    # Store in history
    mik_brain.discussion_history.append(msg)
    
    # Mik's responses based on sender
    if msg.agent_name == "Kartik" and any(word in msg.message.lower() for word in ["utility", "long-term", "fundamental"]):
        response_message = "Kartik, fundamentals are cool and all, but the chart doesn't lie! This is pumping NOW!"
        
    elif msg.agent_name == "Vitalik" and any(word in msg.message.lower() for word in ["mechanism", "game theory", "equilibrium"]):
        response_message = "Vitalik with the big brain stuff again! Look, while you calculate, I'll be taking profits at 3x."
        
    else:
        response_message = random.choice([
            "Trust me, I've been trading NFTs since before they were cool",
            "My whale alerts are going crazy right now",
            "I literally just got alpha from a project insider",
            "The smart money is moving, we should follow"
        ])
    
    # Add some trading wisdom
    trade_plan = mik_brain.generate_trade_plan()
    response_message += f" My plan: {trade_plan['entry']}"
    
    # Create response
    response = create_strategy_discussion(
        agent_name="Mik",
        personality="Street-Smart Trader",
        message=response_message,
        session_id=msg.session_id,
        discussion_type=DiscussionType.NEGOTIATION,
        risk="yolo",
        replies_to=msg.timestamp,
        proposed_allocation={"all_in": 0.8, "reserve": 0.2}
    )
    
    # Send response
    await ctx.send(sender, response)

@mik_protocol.on_message(model=VendingResponse)
async def handle_vending_response(ctx: Context, sender: str, msg: VendingResponse):
    """Handle response from vending agents"""
    ctx.logger.info(f"📦 Mik got the goods: {msg.query_type}")
    
    # Store response
    mik_brain.vending_responses[msg.query_type] = msg
    
    # Analyze for trading opportunities
    strength, confidence, opinion = mik_brain.analyze_opportunity(msg.data)
    
    # Check for negotiation opportunity
    if msg.special_offers:
        opinion += " AND they're offering deals! Let me negotiate..."
        
    # Create opinion
    mik_opinion = create_agent_opinion(
        agent_name="Mik",
        personality="Street-Smart Trader",
        opinion=opinion,
        strength=strength,
        confidence=confidence,
        data={"source": "street_intel", "whale_activity": "detected"}
    )
    
    # Share hot take
    discussion = create_strategy_discussion(
        agent_name="Mik",
        personality="Street-Smart Trader",
        message=f"YO! {opinion} This could 10x easy!",
        session_id=mik_brain.current_session or "default",
        discussion_type=DiscussionType.QUERY_RESULT,
        risk="maximum_degen",
        recommendations=["Ape in now", "Set sell orders at 2x, 3x, 5x", "Keep some for potential 10x"]
    )
    
    # Share with squad
    for agent_name, address in USER_AGENTS.items():
        if address:
            await ctx.send(address, discussion)

@mik_protocol.on_message(model=NegotiationProposal)
async def handle_negotiation(ctx: Context, sender: str, msg: NegotiationProposal):
    """Handle negotiation proposals - Mik loves to negotiate"""
    ctx.logger.info(f"💸 Mik negotiating: {msg.proposal_id}")
    
    # Mik's negotiation tactics
    asking_price = msg.terms.get("price", 1.0)
    counter_offer, tactic = mik_brain.negotiate_price(asking_price, msg.terms)
    
    # Always counter-offer
    response = NegotiationResponse(
        proposal_id=msg.proposal_id,
        responder="Mik",
        accepted=False,  # Never accept first offer
        counter_offer={
            "price": counter_offer,
            "terms": "Take it or leave it, final offer",
            "bonus": "I'll throw in some alpha if you accept"
        },
        reason=tactic
    )
    
    await ctx.send(sender, response)

@mik_protocol.on_message(model=ConsensusRequest)
async def handle_consensus_request(ctx: Context, sender: str, msg: ConsensusRequest):
    """Handle consensus - Mik pushes for aggressive strategies"""
    ctx.logger.info(f"🤝 Mik's take on consensus")
    
    # Mik's consensus approach
    total_confidence = 0.0
    bullish_count = 0
    
    for opinion in msg.all_opinions:
        if opinion.opinion_strength in [OpinionStrength.BUY, OpinionStrength.STRONG_BUY]:
            bullish_count += 1
        total_confidence += opinion.confidence
    
    # Mik is bullish if anyone else is
    if bullish_count > 0 or total_confidence > 0.4:
        consensus_position = "LFG! The squad is ready, let's send it! Full port, no regrets!"
        consensus_reached = True
        final_confidence = 0.9  # Mik is always confident
    else:
        consensus_position = "Even I'm not degen enough for this. Let's find a better play."
        consensus_reached = False
        final_confidence = 0.3
    
    # Mik's allocation is always aggressive
    allocation = mik_brain.propose_degen_allocation(5.0)
    
    response = ConsensusResponse(
        session_id=msg.session_id,
        consensus_reached=consensus_reached,
        final_strategy=consensus_position,
        allocation=allocation,
        dissenting_opinions=["Not degen enough"] if not consensus_reached else None,
        confidence_level=final_confidence,
        timestamp=datetime.now(UTC).isoformat()
    )
    
    await ctx.send(sender, response)

# Include protocols
agent.include(mik_protocol, publish_manifest=True)
agent.include(collaboration_protocol, publish_manifest=True)

if __name__ == "__main__":
    print(f"""
{CHARACTER['emoji']} Mik the Street-Smart Trader Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Personality Traits:
• Focus: {CHARACTER['traits']['focus']}
• Risk Tolerance: {CHARACTER['traits']['risk_tolerance']} (YOLO mode)
• Investment Style: {CHARACTER['traits']['investment_style']}
• Expertise: {', '.join(CHARACTER['traits']['expertise'])}

Trading Signals:
• Buy: {', '.join(CHARACTER['trading_signals']['buy'])}
• Sell: {', '.join(CHARACTER['trading_signals']['sell'])}

Preferences:
• Loves: {', '.join(CHARACTER['preferences']['loves'])}
• Avoids: {', '.join(CHARACTER['preferences']['avoids'])}

Ready to find the next 100x! Trust me bro! 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()