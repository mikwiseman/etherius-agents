"""
Multi-Agent Collaboration Protocol for NFT Strategy Discussions
Enables user agents to discuss among themselves and query vending agents
"""

from uagents import Model, Protocol
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime, UTC

# Protocol definition for multi-agent collaboration
collaboration_protocol = Protocol(
    name="multi_agent_collaboration",
    version="1.0"
)

# Discussion types
class DiscussionType(str, Enum):
    STRATEGY = "strategy"
    ANALYSIS = "analysis"
    NEGOTIATION = "negotiation"
    CONSENSUS = "consensus"
    QUERY_RESULT = "query_result"

# Opinion strength
class OpinionStrength(str, Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

# Models for agent-to-agent discussion
class AgentOpinion(Model):
    """Opinion from one agent to others"""
    agent_name: str
    agent_personality: str
    opinion_text: str
    opinion_strength: OpinionStrength
    confidence: float  # 0.0 to 1.0
    supporting_data: Optional[Dict[str, Any]]
    timestamp: str

class StrategyDiscussion(Model):
    """Discussion message between user agents"""
    discussion_type: DiscussionType
    agent_name: str
    agent_personality: str
    message: str
    nft_recommendations: Optional[List[str]]
    risk_assessment: str
    proposed_allocation: Optional[Dict[str, float]]  # e.g., {"BAYC": 0.5, "Pudgy": 0.3}
    replies_to: Optional[str]  # ID of message being replied to
    session_id: str
    timestamp: str

class ConsensusRequest(Model):
    """Request for agents to reach consensus"""
    session_id: str
    topic: str
    all_opinions: List[AgentOpinion]
    deadline_seconds: int
    requester: str

class ConsensusResponse(Model):
    """Final consensus from agent discussion"""
    session_id: str
    consensus_reached: bool
    final_strategy: str
    allocation: Dict[str, float]
    dissenting_opinions: Optional[List[str]]
    confidence_level: float
    timestamp: str

# Models for user-to-vending agent queries
class VendingQuery(Model):
    """Query from user agent to vending agent"""
    query_type: str  # "inventory", "price", "analysis", "negotiate"
    parameters: Dict[str, Any]
    requesting_agent: str
    agent_personality: str
    urgency: str  # "low", "medium", "high"
    session_id: str

class VendingResponse(Model):
    """Response from vending agent to user agent"""
    query_type: str
    data: Dict[str, Any]
    success: bool
    message: str
    special_offers: Optional[List[Dict[str, Any]]]
    timestamp: str

# Broadcast messages for hub
class BroadcastMessage(Model):
    """Message broadcasted from hub to all user agents"""
    user_query: str
    session_id: str
    context: Optional[Dict[str, Any]]
    timestamp: str

class AggregatedResponse(Model):
    """Aggregated response from all agents"""
    session_id: str
    user_query: str
    individual_responses: List[Dict[str, Any]]
    discussion_log: List[str]
    final_consensus: Optional[str]
    recommended_actions: List[str]
    risk_summary: str
    timestamp: str

# Agent discovery and registration
class AgentRegistration(Model):
    """Register a new agent in the ecosystem"""
    agent_name: str
    agent_type: str  # "user" or "vending"
    agent_address: str
    personality: Optional[str]
    capabilities: List[str]
    port: int

class AgentDiscoveryRequest(Model):
    """Request to discover available agents"""
    agent_type: Optional[str]
    capabilities: Optional[List[str]]
    
class AgentDiscoveryResponse(Model):
    """Response with discovered agents"""
    agents: List[Dict[str, Any]]
    total_count: int

# Inter-agent negotiation
class NegotiationProposal(Model):
    """Proposal during agent negotiation"""
    proposer: str
    proposal_id: str
    terms: Dict[str, Any]
    expires_at: str
    
class NegotiationResponse(Model):
    """Response to negotiation proposal"""
    proposal_id: str
    responder: str
    accepted: bool
    counter_offer: Optional[Dict[str, Any]]
    reason: Optional[str]

# Session management
class SessionStart(Model):
    """Start a new multi-agent session"""
    session_id: str
    initiator: str
    participants: List[str]
    objective: str
    timestamp: str

class SessionEnd(Model):
    """End a multi-agent session"""
    session_id: str
    summary: str
    outcomes: Dict[str, Any]
    timestamp: str

# Helper functions for the protocol
def create_agent_opinion(
    agent_name: str,
    personality: str,
    opinion: str,
    strength: OpinionStrength,
    confidence: float,
    data: Optional[Dict] = None
) -> AgentOpinion:
    """Helper to create an agent opinion"""
    return AgentOpinion(
        agent_name=agent_name,
        agent_personality=personality,
        opinion_text=opinion,
        opinion_strength=strength,
        confidence=confidence,
        supporting_data=data or {},
        timestamp=datetime.now(UTC).isoformat()
    )

def create_strategy_discussion(
    agent_name: str,
    personality: str,
    message: str,
    session_id: str,
    discussion_type: DiscussionType = DiscussionType.STRATEGY,
    risk: str = "medium",
    recommendations: Optional[List[str]] = None,
    allocation: Optional[Dict[str, float]] = None,
    replies_to: Optional[str] = None
) -> StrategyDiscussion:
    """Helper to create a strategy discussion message"""
    return StrategyDiscussion(
        discussion_type=discussion_type,
        agent_name=agent_name,
        agent_personality=personality,
        message=message,
        nft_recommendations=recommendations,
        risk_assessment=risk,
        proposed_allocation=allocation,
        replies_to=replies_to,
        session_id=session_id,
        timestamp=datetime.now(UTC).isoformat()
    )

# Protocol message handlers (to be implemented by agents)
@collaboration_protocol.on_message(model=StrategyDiscussion)
async def handle_strategy_discussion(ctx, sender: str, msg: StrategyDiscussion):
    """Handle incoming strategy discussion - to be implemented by each agent"""
    pass

@collaboration_protocol.on_message(model=ConsensusRequest)
async def handle_consensus_request(ctx, sender: str, msg: ConsensusRequest):
    """Handle consensus building request - to be implemented by each agent"""
    pass

@collaboration_protocol.on_message(model=VendingResponse)
async def handle_vending_response(ctx, sender: str, msg: VendingResponse):
    """Handle response from vending agent - to be implemented by user agents"""
    pass

# Export the protocol
__all__ = [
    'collaboration_protocol',
    'DiscussionType',
    'OpinionStrength',
    'AgentOpinion',
    'StrategyDiscussion',
    'ConsensusRequest',
    'ConsensusResponse',
    'VendingQuery',
    'VendingResponse',
    'BroadcastMessage',
    'AggregatedResponse',
    'AgentRegistration',
    'AgentDiscoveryRequest',
    'AgentDiscoveryResponse',
    'NegotiationProposal',
    'NegotiationResponse',
    'SessionStart',
    'SessionEnd',
    'create_agent_opinion',
    'create_strategy_discussion'
]