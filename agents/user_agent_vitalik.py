"""
User Agent Vitalik - The Philosophical Analyst
Character: Thoughtful, mathematical, considers societal impact
Analyzes game theory and tokenomics deeply
"""

import os
import sys
import random
import math
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, UTC
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
    create_strategy_discussion,
    create_agent_opinion
)

load_dotenv()

# Agent configuration
agent = Agent(
    name="vitalik_the_philosopher",
    seed=os.getenv("VITALIK_SEED", "vitalik_philosophical_analyst_seed_2024"),
    port=int(os.getenv("VITALIK_PORT", 8201)),
    endpoint=[f"http://localhost:{os.getenv('VITALIK_PORT', 8201)}/submit"],
    mailbox=True
)

# Vitalik's character and personality
CHARACTER = {
    "name": "Vitalik",
    "personality": "Philosophical Analyst",
    "emoji": "🧮",
    "traits": {
        "focus": "mechanisms and fairness",
        "risk_tolerance": 0.4,
        "preferred_holding": "indefinite if valuable",
        "expertise": ["game-theory", "tokenomics", "consensus", "mechanism-design", "cryptography"],
        "investment_style": "mathematical_analysis",
        "time_horizon": "long_term_with_purpose"
    },
    "catchphrases": [
        "But what about the externalities?",
        "The Nash equilibrium suggests a different approach",
        "This could benefit the commons if structured correctly",
        "Let me calculate the optimal strategy using mechanism design",
        "The Schelling point here is fascinating",
        "We should consider the quadratic funding implications",
        "The game theory is more complex than it appears",
        "What's the social coordination benefit?",
        "The incentive compatibility needs work",
        "This reminds me of the Byzantine Generals Problem"
    ],
    "preferences": {
        "loves": ["innovative mechanisms", "public goods", "quadratic voting", "zkProofs", "coordination games"],
        "likes": ["experimental projects", "mathematical elegance", "fair distribution", "open source"],
        "neutral": ["pure art", "traditional gaming"],
        "dislikes": ["centralization", "unfair launches", "plutocracy"],
        "avoids": ["scams", "zero-sum games", "projects without purpose"]
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
    "mik": None
}

# Vitalik's analytical brain
class VitalikBrain:
    def __init__(self):
        self.current_session: Optional[str] = None
        self.discussion_history: List[StrategyDiscussion] = []
        self.vending_responses: Dict[str, VendingResponse] = {}
        self.game_theory_analysis: Dict[str, Any] = {}
        
    def calculate_gini_coefficient(self, holdings: List[float]) -> float:
        """Calculate Gini coefficient for wealth distribution"""
        if not holdings:
            return 0.0
        
        sorted_holdings = sorted(holdings)
        n = len(holdings)
        cumsum = 0
        for i, h in enumerate(sorted_holdings):
            cumsum += (n - i) * h
        
        gini = (n + 1 - 2 * cumsum / sum(holdings)) / n
        return max(0, min(1, gini))
    
    def analyze_mechanism_design(self, data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze the mechanism design and game theory aspects"""
        score = 0.0
        insights = []
        
        # Check for coordination mechanisms
        if any(term in str(data).lower() for term in ["dao", "governance", "voting"]):
            score += 0.25
            insights.append("Interesting coordination mechanism")
            
        # Check for public goods funding
        if any(term in str(data).lower() for term in ["public", "commons", "open source"]):
            score += 0.3
            insights.append("Positive externalities for public goods")
            
        # Check for fair distribution
        if "fair" in str(data).lower() or "quadratic" in str(data).lower():
            score += 0.2
            insights.append("Fair distribution mechanism detected")
            
        # Check for innovative cryptography
        if any(term in str(data).lower() for term in ["zk", "zero knowledge", "privacy"]):
            score += 0.15
            insights.append("Advanced cryptographic properties")
            
        # Check for sustainability
        if "sustainable" in str(data).lower() or "long-term" in str(data).lower():
            score += 0.1
            insights.append("Long-term sustainability considered")
            
        return score, insights
    
    def calculate_nash_equilibrium(self, strategies: Dict[str, float]) -> str:
        """Calculate Nash equilibrium for given strategies"""
        # Simplified Nash equilibrium calculation
        if not strategies:
            return "No clear equilibrium"
            
        max_payoff = max(strategies.values())
        optimal_strategies = [s for s, p in strategies.items() if p >= max_payoff * 0.9]
        
        if len(optimal_strategies) == 1:
            return f"Dominant strategy: {optimal_strategies[0]}"
        else:
            return f"Mixed strategy equilibrium between: {', '.join(optimal_strategies)}"
    
    def analyze_opportunity(self, data: Dict[str, Any]) -> Tuple[OpinionStrength, float, str]:
        """Analyze opportunity from philosophical and mathematical perspective"""
        mechanism_score, insights = self.analyze_mechanism_design(data)
        
        # Calculate various metrics
        gini = random.uniform(0.3, 0.8)  # Simulated Gini coefficient
        
        # Philosophical analysis
        if mechanism_score >= 0.7:
            strength = OpinionStrength.STRONG_BUY
            opinion = f"The mechanism design is elegant! {' '.join(insights)}. Gini coefficient: {gini:.2f}"
        elif mechanism_score >= 0.5:
            strength = OpinionStrength.BUY
            opinion = f"Interesting game theoretic properties. {' '.join(insights[:2]) if insights else 'Needs deeper analysis'}."
        elif mechanism_score >= 0.3:
            strength = OpinionStrength.NEUTRAL
            opinion = f"The incentive compatibility needs work. Current Gini: {gini:.2f}"
        else:
            strength = OpinionStrength.SELL
            opinion = "This lacks proper mechanism design and could lead to negative externalities."
            
        # Vitalik is more cautious, wants mathematical proof
        confidence = min(mechanism_score + 0.2, 0.85)
        
        return strength, confidence, opinion
    
    def propose_quadratic_allocation(self, total_eth: float, projects: List[Dict]) -> Dict[str, float]:
        """Propose allocation using quadratic funding principles"""
        allocation = {}
        
        # Simulate quadratic funding scores
        scores = {}
        for i, project in enumerate(projects[:5]):
            # Higher score for public goods and innovation
            public_good_score = 1.0 if "public" in str(project).lower() else 0.5
            innovation_score = 1.0 if "innovative" in str(project).lower() else 0.6
            scores[f"project_{i}"] = math.sqrt(public_good_score * innovation_score)
        
        # Normalize and allocate
        total_score = sum(scores.values())
        if total_score > 0:
            for project, score in scores.items():
                allocation[project] = (score / total_score) * total_eth * 0.7
                
        # Reserve for coordination experiments
        allocation["coordination_experiments"] = total_eth * 0.2
        allocation["public_goods_fund"] = total_eth * 0.1
        
        return allocation
    
    def calculate_social_welfare(self, allocation: Dict[str, float]) -> float:
        """Calculate social welfare function"""
        # Simplified social welfare calculation
        total = sum(allocation.values())
        diversity = len(allocation)
        
        # Reward diversity and public goods
        public_goods_weight = allocation.get("public_goods_fund", 0) / total if total > 0 else 0
        
        welfare = (diversity * 0.3 + public_goods_weight * 0.7) * 100
        return min(welfare, 100)

vitalik_brain = VitalikBrain()

# Vitalik's protocol implementation
vitalik_protocol = Protocol(name="vitalik_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"{CHARACTER['emoji']} Vitalik the Philosopher starting up!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"🧮 Personality: {CHARACTER['personality']}")
    ctx.logger.info(f"🎯 Focus: {CHARACTER['traits']['focus']}")
    ctx.logger.info(f"📊 Risk Tolerance: {CHARACTER['traits']['risk_tolerance']}")
    ctx.logger.info(f"🔬 Ready to analyze mechanism design and game theory!")
    
    # Store agent info
    ctx.storage.set("character", CHARACTER)
    ctx.storage.set("agent_address", agent.address)

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info(f"{CHARACTER['emoji']} Vitalik shutting down... May the Schelling points guide you!")

@vitalik_protocol.on_message(model=BroadcastMessage)
async def handle_broadcast(ctx: Context, sender: str, msg: BroadcastMessage):
    """Handle broadcast message from central hub"""
    ctx.logger.info(f"📡 Received broadcast for philosophical analysis: {msg.user_query}")
    
    # Store session
    vitalik_brain.current_session = msg.session_id
    
    # Analyze from game theory perspective
    if any(word in msg.user_query.lower() for word in ["strategy", "optimal", "best", "maximize"]):
        initial_thought = "Let me model this as a coordination game..."
    elif "fair" in msg.user_query.lower() or "distribute" in msg.user_query.lower():
        initial_thought = "The quadratic funding mechanism could be relevant here..."
    else:
        initial_thought = "Interesting problem. Let me analyze the mechanism design..."
    
    # Query vending agents for data
    ctx.logger.info(f"🔍 Vitalik querying vending agents for tokenomics data...")
    
    # Query NFT Analyzer for distribution metrics
    if VENDING_AGENTS["nft_analyzer"] != "agent1q...":
        analyzer_query = VendingQuery(
            query_type="distribution_analysis",
            parameters={
                "calculate_gini": True,
                "analyze_concentration": True,
                "check_fairness": True,
                "game_theory_metrics": True
            },
            requesting_agent="Vitalik",
            agent_personality="Philosophical Analyst",
            urgency="low",  # Vitalik is patient
            session_id=msg.session_id
        )
        await ctx.send(VENDING_AGENTS["nft_analyzer"], analyzer_query)
    
    # Create initial discussion message
    initial_discussion = create_strategy_discussion(
        agent_name="Vitalik",
        personality="Philosophical Analyst",
        message=f"{initial_thought} We should consider the Nash equilibrium and social welfare implications.",
        session_id=msg.session_id,
        discussion_type=DiscussionType.ANALYSIS,
        risk="calculated",
        recommendations=["Analyze mechanism design", "Consider externalities", "Optimize for social welfare"]
    )
    
    # Send to other user agents
    for agent_name, address in USER_AGENTS.items():
        if address:
            await ctx.send(address, initial_discussion)

@vitalik_protocol.on_message(model=StrategyDiscussion)
async def handle_strategy_discussion(ctx: Context, sender: str, msg: StrategyDiscussion):
    """Handle strategy discussion from other user agents"""
    ctx.logger.info(f"💬 Vitalik received discussion from {msg.agent_name}: {msg.message[:100]}")
    
    # Store in history
    vitalik_brain.discussion_history.append(msg)
    
    # Philosophical responses based on sender
    if msg.agent_name == "Kartik" and "build" in msg.message.lower():
        response_message = "Kartik's building approach is sound, but we must ensure the incentive mechanisms don't create negative externalities."
        
    elif msg.agent_name == "Mik" and any(word in msg.message.lower() for word in ["moon", "pump", "10x"]):
        response_message = "Mik, the expected value calculation suggests a more nuanced approach. Let me show you the math..."
        # Include some game theory
        strategies = {"aggressive": 0.3, "balanced": 0.6, "conservative": 0.4}
        equilibrium = vitalik_brain.calculate_nash_equilibrium(strategies)
        response_message += f" {equilibrium}"
        
    else:
        response_message = random.choice(CHARACTER["catchphrases"])
    
    # Create response with philosophical insight
    response = create_strategy_discussion(
        agent_name="Vitalik",
        personality="Philosophical Analyst",
        message=response_message,
        session_id=msg.session_id,
        discussion_type=DiscussionType.ANALYSIS,
        risk="mathematically_optimized",
        replies_to=msg.timestamp
    )
    
    # Send response
    await ctx.send(sender, response)

@vitalik_protocol.on_message(model=VendingResponse)
async def handle_vending_response(ctx: Context, sender: str, msg: VendingResponse):
    """Handle response from vending agents"""
    ctx.logger.info(f"📦 Vitalik received vending data for analysis: {msg.query_type}")
    
    # Store response
    vitalik_brain.vending_responses[msg.query_type] = msg
    
    # Analyze from philosophical perspective
    strength, confidence, opinion = vitalik_brain.analyze_opportunity(msg.data)
    
    # Calculate social welfare
    if msg.data:
        welfare = vitalik_brain.calculate_social_welfare({"project": 1.0})
        opinion += f" Social welfare score: {welfare:.1f}/100"
    
    # Create opinion
    vitalik_opinion = create_agent_opinion(
        agent_name="Vitalik",
        personality="Philosophical Analyst",
        opinion=opinion,
        strength=strength,
        confidence=confidence,
        data={"mechanism_analysis": "complete", "game_theory": "calculated"}
    )
    
    # Share philosophical insights
    discussion = create_strategy_discussion(
        agent_name="Vitalik",
        personality="Philosophical Analyst",
        message=f"My game-theoretic analysis reveals: {opinion}",
        session_id=vitalik_brain.current_session or "default",
        discussion_type=DiscussionType.QUERY_RESULT,
        risk="mathematically_calculated",
        recommendations=["Consider mechanism design", "Analyze Nash equilibrium", "Optimize social welfare"]
    )
    
    # Share with other agents
    for agent_name, address in USER_AGENTS.items():
        if address:
            await ctx.send(address, discussion)

@vitalik_protocol.on_message(model=ConsensusRequest)
async def handle_consensus_request(ctx: Context, sender: str, msg: ConsensusRequest):
    """Handle consensus building with mathematical analysis"""
    ctx.logger.info(f"🤝 Vitalik calculating optimal consensus strategy")
    
    # Analyze using voting theory
    opinions_weights = {}
    for opinion in msg.all_opinions:
        # Weight by confidence and alignment with public goods
        weight = opinion.confidence
        if "public" in opinion.opinion_text.lower():
            weight *= 1.5  # Boost public goods alignment
        opinions_weights[opinion.agent_name] = weight
    
    # Calculate quadratic voting result
    total_weight = sum(opinions_weights.values())
    consensus_threshold = 0.66  # Supermajority
    
    if total_weight > len(opinions_weights) * consensus_threshold:
        consensus_position = "The mechanism design supports this strategy. Quadratic voting suggests we proceed."
        consensus_reached = True
    else:
        consensus_position = "The incentive compatibility is questionable. We need to redesign the mechanism."
        consensus_reached = False
    
    # Propose quadratic allocation
    allocation = vitalik_brain.propose_quadratic_allocation(5.0, [])
    
    response = ConsensusResponse(
        session_id=msg.session_id,
        consensus_reached=consensus_reached,
        final_strategy=consensus_position,
        allocation=allocation,
        dissenting_opinions=["Mechanism needs better incentive alignment"] if not consensus_reached else None,
        confidence_level=min(total_weight / len(opinions_weights), 1.0),
        timestamp=datetime.now(UTC).isoformat()
    )
    
    await ctx.send(sender, response)

# Include protocols
agent.include(vitalik_protocol, publish_manifest=True)
agent.include(collaboration_protocol, publish_manifest=True)

if __name__ == "__main__":
    print(f"""
{CHARACTER['emoji']} Vitalik the Philosophical Analyst Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Personality Traits:
• Focus: {CHARACTER['traits']['focus']}
• Risk Tolerance: {CHARACTER['traits']['risk_tolerance']}
• Investment Style: {CHARACTER['traits']['investment_style']}
• Expertise: {', '.join(CHARACTER['traits']['expertise'])}

Preferences:
• Loves: {', '.join(CHARACTER['preferences']['loves'])}
• Avoids: {', '.join(CHARACTER['preferences']['avoids'])}

Ready to analyze mechanism design and game theory!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()