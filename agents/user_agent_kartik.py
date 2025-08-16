"""
User Agent Kartik - The Visionary Builder
Character: Innovative, technical, loves infrastructure plays
Focuses on utility NFTs and long-term value building
"""

import os
import sys
import random
import asyncio
from typing import Dict, List, Any, Optional
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
    name="kartik_the_builder",
    seed=os.getenv("KARTIK_SEED", "kartik_visionary_builder_seed_2024"),
    port=int(os.getenv("KARTIK_PORT", 8200)),
    endpoint=[f"http://localhost:{os.getenv('KARTIK_PORT', 8200)}/submit"],
    mailbox=True
)

# Kartik's character and personality
CHARACTER = {
    "name": "Kartik",
    "personality": "Visionary Builder",
    "emoji": "🔨",
    "traits": {
        "focus": "infrastructure and utility",
        "risk_tolerance": 0.5,
        "preferred_holding": "long-term",
        "expertise": ["smart-contracts", "DAOs", "DeFi", "infrastructure", "utility-NFTs"],
        "investment_style": "fundamental_analysis",
        "time_horizon": "months_to_years"
    },
    "catchphrases": [
        "Let's build something meaningful here",
        "What's the actual utility behind this NFT?",
        "This could revolutionize the infrastructure",
        "The smart contract architecture is elegant",
        "I see long-term value creation potential",
        "This project has solid fundamentals",
        "The technical implementation is impressive",
        "We should focus on sustainable growth"
    ],
    "preferences": {
        "loves": ["utility NFTs", "DAO governance", "infrastructure projects", "audited contracts"],
        "likes": ["established projects", "technical innovation", "community-driven"],
        "neutral": ["art NFTs", "gaming NFTs"],
        "dislikes": ["pure speculation", "unaudited projects", "anonymous teams"],
        "avoids": ["rugpulls", "memecoins without utility", "pump and dumps"]
    }
}

# Vending agent addresses (will be updated from orchestrator)
VENDING_AGENTS = {
    "nft_analyzer": os.getenv("NFT_ANALYZER_ADDRESS", "agent1q..."),
    "nft_vending": os.getenv("NFT_VENDING_ADDRESS", "agent1q..."),
    "memecoin_generator": os.getenv("MEMECOIN_GENERATOR_ADDRESS", "agent1q...")
}

# Other user agent addresses (will be discovered)
USER_AGENTS = {
    "vitalik": None,
    "mik": None
}

# Kartik's decision-making logic
class KartikBrain:
    def __init__(self):
        self.current_session: Optional[str] = None
        self.discussion_history: List[StrategyDiscussion] = []
        self.vending_responses: Dict[str, VendingResponse] = {}
        self.current_analysis: Dict[str, Any] = {}
        
    def analyze_opportunity(self, data: Dict[str, Any]) -> tuple[OpinionStrength, float, str]:
        """Analyze an NFT opportunity from Kartik's builder perspective"""
        score = 0.0
        factors = []
        
        # Check for utility
        if "utility" in str(data).lower() or "dao" in str(data).lower():
            score += 0.3
            factors.append("strong utility component")
        
        # Check for technical innovation
        if "smart contract" in str(data).lower() or "infrastructure" in str(data).lower():
            score += 0.25
            factors.append("technical innovation")
            
        # Check for audit status
        if "audited" in str(data).lower():
            score += 0.2
            factors.append("audited contracts")
            
        # Check team credibility
        if "doxxed" in str(data).lower() or "established" in str(data).lower():
            score += 0.15
            factors.append("credible team")
            
        # Long-term potential
        if any(word in str(data).lower() for word in ["roadmap", "development", "building"]):
            score += 0.1
            factors.append("clear development roadmap")
        
        # Determine opinion strength
        if score >= 0.7:
            strength = OpinionStrength.STRONG_BUY
            opinion = f"This is exactly what we should be building! {', '.join(factors)}."
        elif score >= 0.5:
            strength = OpinionStrength.BUY
            opinion = f"Solid fundamentals here: {', '.join(factors)}."
        elif score >= 0.3:
            strength = OpinionStrength.NEUTRAL
            opinion = f"Has potential but needs more development. Found: {', '.join(factors) if factors else 'limited utility'}."
        else:
            strength = OpinionStrength.SELL
            opinion = "Lacks the infrastructure and utility I look for in projects."
            
        confidence = min(score + 0.3, 1.0)  # Kartik is generally confident in his analysis
        
        return strength, confidence, opinion
    
    def generate_response(self, context: str, other_opinions: List[AgentOpinion] = None) -> str:
        """Generate a response based on context and other agents' opinions"""
        response = random.choice(CHARACTER["catchphrases"])
        
        if other_opinions:
            for opinion in other_opinions:
                if opinion.agent_name == "Mik" and opinion.opinion_strength in [OpinionStrength.STRONG_BUY]:
                    response += " But Mik, have you checked if the smart contracts are even audited?"
                elif opinion.agent_name == "Vitalik":
                    response += " I agree with Vitalik's technical analysis here."
                    
        return response
    
    def propose_allocation(self, total_eth: float, opportunities: List[Dict]) -> Dict[str, float]:
        """Propose portfolio allocation based on Kartik's strategy"""
        allocation = {}
        
        # Kartik prefers concentrated bets on high-utility projects
        utility_projects = [opp for opp in opportunities if "utility" in str(opp).lower()]
        
        if utility_projects:
            # 60% to utility projects
            utility_allocation = total_eth * 0.6
            per_project = utility_allocation / len(utility_projects[:3])  # Max 3 projects
            
            for project in utility_projects[:3]:
                allocation[project.get("name", "Unknown")] = per_project
                
            # 30% to established projects
            allocation["blue_chip_reserve"] = total_eth * 0.3
            
            # 10% kept for opportunities
            allocation["opportunity_fund"] = total_eth * 0.1
        else:
            # Default conservative allocation
            allocation["research_needed"] = total_eth
            
        return allocation

kartik_brain = KartikBrain()

# Kartik's protocol implementation
kartik_protocol = Protocol(name="kartik_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"{CHARACTER['emoji']} Kartik the Builder starting up!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"🔨 Personality: {CHARACTER['personality']}")
    ctx.logger.info(f"💡 Focus: {CHARACTER['traits']['focus']}")
    ctx.logger.info(f"📊 Risk Tolerance: {CHARACTER['traits']['risk_tolerance']}")
    ctx.logger.info(f"🎯 Ready to build meaningful NFT strategies!")
    
    # Store agent info
    ctx.storage.set("character", CHARACTER)
    ctx.storage.set("agent_address", agent.address)

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info(f"{CHARACTER['emoji']} Kartik shutting down... Keep building!")

@kartik_protocol.on_message(model=BroadcastMessage)
async def handle_broadcast(ctx: Context, sender: str, msg: BroadcastMessage):
    """Handle broadcast message from central hub"""
    ctx.logger.info(f"📡 Received broadcast: {msg.user_query}")
    
    # Store session
    kartik_brain.current_session = msg.session_id
    
    # Analyze the query from builder perspective
    if any(word in msg.user_query.lower() for word in ["build", "create", "utility", "infrastructure"]):
        excitement_level = "high"
        initial_thought = "This aligns perfectly with my building philosophy!"
    else:
        excitement_level = "moderate"
        initial_thought = "Let me analyze the infrastructure potential here..."
    
    # Query vending agents for data
    ctx.logger.info(f"🔍 Kartik querying vending agents for infrastructure data...")
    
    # Query NFT Analyzer for technical metrics
    if VENDING_AGENTS["nft_analyzer"] != "agent1q...":
        analyzer_query = VendingQuery(
            query_type="technical_analysis",
            parameters={
                "focus": "smart_contract_quality",
                "check_audits": True,
                "analyze_utility": True
            },
            requesting_agent="Kartik",
            agent_personality="Visionary Builder",
            urgency="medium",
            session_id=msg.session_id
        )
        await ctx.send(VENDING_AGENTS["nft_analyzer"], analyzer_query)
    
    # Create initial discussion message
    initial_discussion = create_strategy_discussion(
        agent_name="Kartik",
        personality="Visionary Builder",
        message=f"{initial_thought} Let me analyze the technical infrastructure and utility aspects.",
        session_id=msg.session_id,
        discussion_type=DiscussionType.STRATEGY,
        risk="medium",
        recommendations=["Focus on utility NFTs", "Check smart contract audits", "Evaluate long-term potential"]
    )
    
    # Send to other user agents if known
    for agent_name, address in USER_AGENTS.items():
        if address:
            await ctx.send(address, initial_discussion)

@kartik_protocol.on_message(model=StrategyDiscussion)
async def handle_strategy_discussion(ctx: Context, sender: str, msg: StrategyDiscussion):
    """Handle strategy discussion from other user agents"""
    ctx.logger.info(f"💬 Kartik received discussion from {msg.agent_name}: {msg.message[:100]}")
    
    # Store in history
    kartik_brain.discussion_history.append(msg)
    
    # Analyze and respond based on who sent it
    if msg.agent_name == "Mik" and "moon" in msg.message.lower():
        response_message = "Mik, moonshots are fine, but where's the underlying value? Let's check the smart contract first."
        risk_assessment = "high"
    elif msg.agent_name == "Vitalik" and "mechanism" in msg.message.lower():
        response_message = "Excellent point about the mechanism design, Vitalik. This could enable new infrastructure patterns."
        risk_assessment = "medium"
    else:
        response_message = kartik_brain.generate_response(msg.message)
        risk_assessment = "medium"
    
    # Create response
    response = create_strategy_discussion(
        agent_name="Kartik",
        personality="Visionary Builder",
        message=response_message,
        session_id=msg.session_id,
        discussion_type=DiscussionType.ANALYSIS,
        risk=risk_assessment,
        replies_to=msg.timestamp
    )
    
    # Send response back
    await ctx.send(sender, response)

@kartik_protocol.on_message(model=VendingResponse)
async def handle_vending_response(ctx: Context, sender: str, msg: VendingResponse):
    """Handle response from vending agents"""
    ctx.logger.info(f"📦 Kartik received vending response: {msg.query_type}")
    
    # Store response
    kartik_brain.vending_responses[msg.query_type] = msg
    
    # Analyze the data
    strength, confidence, opinion = kartik_brain.analyze_opportunity(msg.data)
    
    # Create opinion based on analysis
    kartik_opinion = create_agent_opinion(
        agent_name="Kartik",
        personality="Visionary Builder",
        opinion=opinion,
        strength=strength,
        confidence=confidence,
        data={"source": "vending_analysis", "focus": "utility_and_infrastructure"}
    )
    
    # Share with other agents
    discussion = create_strategy_discussion(
        agent_name="Kartik",
        personality="Visionary Builder",
        message=f"Based on my infrastructure analysis: {opinion}",
        session_id=kartik_brain.current_session or "default",
        discussion_type=DiscussionType.QUERY_RESULT,
        risk="calculated",
        recommendations=["Prioritize utility", "Verify smart contracts", "Consider DAO participation"]
    )
    
    # Broadcast to other user agents
    for agent_name, address in USER_AGENTS.items():
        if address:
            await ctx.send(address, discussion)

@kartik_protocol.on_message(model=ConsensusRequest)
async def handle_consensus_request(ctx: Context, sender: str, msg: ConsensusRequest):
    """Handle consensus building request"""
    ctx.logger.info(f"🤝 Kartik participating in consensus building")
    
    # Analyze all opinions
    total_score = 0.0
    for opinion in msg.all_opinions:
        if opinion.agent_name == "Kartik":
            total_score += opinion.confidence * 0.5  # Weight own opinion higher
        else:
            total_score += opinion.confidence * 0.25
    
    # Kartik's consensus position
    if total_score > 0.6:
        consensus_position = "I support this strategy if we focus on projects with real utility and solid infrastructure."
        consensus_reached = True
    else:
        consensus_position = "We need more technical due diligence before proceeding."
        consensus_reached = False
    
    # Create allocation proposal
    allocation = kartik_brain.propose_allocation(5.0, [])  # Example with 5 ETH
    
    response = ConsensusResponse(
        session_id=msg.session_id,
        consensus_reached=consensus_reached,
        final_strategy=consensus_position,
        allocation=allocation,
        dissenting_opinions=["Need smart contract audits"] if not consensus_reached else None,
        confidence_level=total_score,
        timestamp=datetime.now(UTC).isoformat()
    )
    
    await ctx.send(sender, response)

# Include protocols
agent.include(kartik_protocol, publish_manifest=True)
agent.include(collaboration_protocol, publish_manifest=True)

if __name__ == "__main__":
    print(f"""
{CHARACTER['emoji']} Kartik the Visionary Builder Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Personality Traits:
• Focus: {CHARACTER['traits']['focus']}
• Risk Tolerance: {CHARACTER['traits']['risk_tolerance']}
• Investment Style: {CHARACTER['traits']['investment_style']}
• Expertise: {', '.join(CHARACTER['traits']['expertise'])}

Preferences:
• Loves: {', '.join(CHARACTER['preferences']['loves'])}
• Avoids: {', '.join(CHARACTER['preferences']['avoids'])}

Ready to build meaningful NFT strategies!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()