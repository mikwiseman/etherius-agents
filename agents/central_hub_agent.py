"""
Central Hub Agent - Message Broadcaster and Aggregator
Receives user messages and broadcasts to all user agents
Aggregates responses and shows inter-agent discussions
"""

import os
import sys
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, UTC, timedelta
from collections import defaultdict
from dotenv import load_dotenv
import json

from uagents import Agent, Context, Model, Protocol
from uagents.storage import StorageAPI

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocols.collaboration_protocol import (
    collaboration_protocol,
    StrategyDiscussion,
    AgentOpinion,
    ConsensusRequest,
    ConsensusResponse,
    BroadcastMessage,
    AggregatedResponse,
    AgentRegistration,
    AgentDiscoveryRequest,
    AgentDiscoveryResponse,
    SessionStart,
    SessionEnd,
    DiscussionType
)

load_dotenv()

# Agent configuration
agent = Agent(
    name="central_hub",
    seed=os.getenv("HUB_SEED", "central_hub_broadcaster_seed_2024"),
    port=int(os.getenv("HUB_PORT", 8199)),
    endpoint=[f"http://localhost:{os.getenv('HUB_PORT', 8199)}/submit"],
    mailbox=True
)

# User agent registry - will be populated dynamically
USER_AGENTS = {
    "kartik": {
        "address": os.getenv("KARTIK_ADDRESS", "agent1q..."),
        "personality": "Visionary Builder",
        "emoji": "🔨",
        "port": 8200
    },
    "vitalik": {
        "address": os.getenv("VITALIK_ADDRESS", "agent1q..."),
        "personality": "Philosophical Analyst",
        "emoji": "🧮",
        "port": 8201
    },
    "mik": {
        "address": os.getenv("MIK_ADDRESS", "agent1q..."),
        "personality": "Street-Smart Trader",
        "emoji": "💰",
        "port": 8202
    }
}

# Vending agent registry
VENDING_AGENTS = {
    "nft_analyzer": {
        "address": os.getenv("NFT_ANALYZER_ADDRESS", "agent1q..."),
        "type": "analyzer",
        "port": 8102
    },
    "nft_vending": {
        "address": os.getenv("NFT_VENDING_ADDRESS", "agent1q..."),
        "type": "vending",
        "port": 8101
    },
    "orchestrator": {
        "address": os.getenv("ORCHESTRATOR_ADDRESS", "agent1q..."),
        "type": "orchestrator",
        "port": 8104
    }
}

# Session management
class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.discussion_logs: Dict[str, List[StrategyDiscussion]] = defaultdict(list)
        self.agent_responses: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.consensus_results: Dict[str, ConsensusResponse] = {}
        
    def create_session(self, session_id: str, user_query: str) -> None:
        """Create a new discussion session"""
        self.active_sessions[session_id] = {
            "query": user_query,
            "started": datetime.now(UTC).isoformat(),
            "participants": set(),
            "status": "active",
            "messages_sent": 0,
            "responses_received": 0
        }
        
    def add_discussion(self, session_id: str, discussion: StrategyDiscussion) -> None:
        """Add a discussion message to session log"""
        self.discussion_logs[session_id].append(discussion)
        self.active_sessions[session_id]["participants"].add(discussion.agent_name)
        
    def add_response(self, session_id: str, agent_name: str, response: Any) -> None:
        """Add an agent response"""
        self.agent_responses[session_id][agent_name] = response
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["responses_received"] += 1
            
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a session"""
        if session_id not in self.active_sessions:
            return {}
            
        return {
            "session": self.active_sessions[session_id],
            "discussions": len(self.discussion_logs[session_id]),
            "participants": list(self.active_sessions[session_id]["participants"]),
            "consensus": self.consensus_results.get(session_id)
        }
    
    def format_discussion_log(self, session_id: str) -> List[str]:
        """Format discussion log for display"""
        if session_id not in self.discussion_logs:
            return []
            
        formatted_log = []
        for msg in self.discussion_logs[session_id]:
            emoji = {"Kartik": "🔨", "Vitalik": "🧮", "Mik": "💰"}.get(msg.agent_name, "🤖")
            formatted_log.append(f"{emoji} {msg.agent_name}: {msg.message}")
            
        return formatted_log

session_manager = SessionManager()

# Hub protocol
hub_protocol = Protocol(name="hub_protocol", version="1.0")

# Models for hub-specific communication
class UserQuery(Model):
    """User query to be broadcasted"""
    query: str
    context: Optional[Dict[str, Any]]
    session_id: Optional[str]

class HubStatus(Model):
    """Hub status response"""
    active_sessions: int
    connected_agents: Dict[str, bool]
    last_activity: str

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🌐 Central Hub Agent starting up!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"👥 Managing {len(USER_AGENTS)} user agents")
    ctx.logger.info(f"📦 Connected to {len(VENDING_AGENTS)} vending agents")
    ctx.logger.info(f"🔄 Ready to broadcast and aggregate messages!")
    
    # Store hub info
    ctx.storage.set("hub_address", agent.address)
    ctx.storage.set("startup_time", datetime.now(UTC).isoformat())
    
    # Log agent registry
    for agent_name, info in USER_AGENTS.items():
        ctx.logger.info(f"  {info['emoji']} {agent_name}: {info['personality']}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info(f"🌐 Central Hub shutting down...")
    
    # End all active sessions
    for session_id in list(session_manager.active_sessions.keys()):
        session_manager.active_sessions[session_id]["status"] = "ended"

@hub_protocol.on_message(model=UserQuery)
async def handle_user_query(ctx: Context, sender: str, msg: UserQuery):
    """Handle user query and broadcast to all user agents"""
    ctx.logger.info(f"📨 Received user query: {msg.query}")
    
    # Create session
    session_id = msg.session_id or f"session_{datetime.now(UTC).timestamp()}"
    session_manager.create_session(session_id, msg.query)
    
    # Create broadcast message
    broadcast = BroadcastMessage(
        user_query=msg.query,
        session_id=session_id,
        context=msg.context,
        timestamp=datetime.now(UTC).isoformat()
    )
    
    # Broadcast to all user agents
    ctx.logger.info(f"📡 Broadcasting to {len(USER_AGENTS)} user agents...")
    broadcast_count = 0
    
    for agent_name, info in USER_AGENTS.items():
        if info["address"] != "agent1q...":
            try:
                await ctx.send(info["address"], broadcast)
                broadcast_count += 1
                ctx.logger.info(f"  ✅ Sent to {info['emoji']} {agent_name}")
            except Exception as e:
                ctx.logger.error(f"  ❌ Failed to send to {agent_name}: {e}")
        else:
            ctx.logger.warning(f"  ⚠️ {agent_name} address not configured")
    
    session_manager.active_sessions[session_id]["messages_sent"] = broadcast_count
    
    # Wait a bit for initial responses
    await asyncio.sleep(2)
    
    # Start aggregating responses
    ctx.logger.info(f"⏳ Waiting for agent discussions...")

@hub_protocol.on_message(model=StrategyDiscussion)
async def handle_strategy_discussion(ctx: Context, sender: str, msg: StrategyDiscussion):
    """Handle strategy discussions between agents"""
    ctx.logger.info(f"💬 Discussion from {msg.agent_name}: {msg.message[:50]}...")
    
    # Log the discussion
    session_manager.add_discussion(msg.session_id, msg)
    
    # Store in context for aggregation
    discussions = ctx.storage.get(f"discussions_{msg.session_id}") or []
    discussions.append({
        "agent": msg.agent_name,
        "personality": msg.agent_personality,
        "message": msg.message,
        "risk": msg.risk_assessment,
        "timestamp": msg.timestamp
    })
    ctx.storage.set(f"discussions_{msg.session_id}", discussions)
    
    # If this is a query result, track it
    if msg.discussion_type == DiscussionType.QUERY_RESULT:
        session_manager.add_response(msg.session_id, msg.agent_name, msg)

@hub_protocol.on_message(model=AgentOpinion)
async def handle_agent_opinion(ctx: Context, sender: str, msg: AgentOpinion):
    """Handle individual agent opinions"""
    ctx.logger.info(f"📊 Opinion from {msg.agent_name}: {msg.opinion_strength}")
    
    # Store opinion for consensus building
    opinions = ctx.storage.get("current_opinions") or []
    opinions.append(msg)
    ctx.storage.set("current_opinions", opinions)

@hub_protocol.on_message(model=ConsensusResponse)
async def handle_consensus_response(ctx: Context, sender: str, msg: ConsensusResponse):
    """Handle consensus responses from agents"""
    ctx.logger.info(f"🤝 Consensus from agent: {msg.consensus_reached}")
    
    # Store consensus result
    session_manager.consensus_results[msg.session_id] = msg

@hub_protocol.on_message(model=AgentRegistration)
async def handle_agent_registration(ctx: Context, sender: str, msg: AgentRegistration):
    """Handle new agent registration"""
    ctx.logger.info(f"📝 New agent registration: {msg.agent_name}")
    
    if msg.agent_type == "user":
        USER_AGENTS[msg.agent_name] = {
            "address": msg.agent_address,
            "personality": msg.personality or "Unknown",
            "emoji": "🤖",
            "port": msg.port
        }
    elif msg.agent_type == "vending":
        VENDING_AGENTS[msg.agent_name] = {
            "address": msg.agent_address,
            "type": msg.agent_type,
            "port": msg.port
        }
    
    ctx.logger.info(f"✅ Registered {msg.agent_name} as {msg.agent_type} agent")

@hub_protocol.on_message(model=AgentDiscoveryRequest)
async def handle_discovery_request(ctx: Context, sender: str, msg: AgentDiscoveryRequest):
    """Handle agent discovery requests"""
    ctx.logger.info(f"🔍 Agent discovery request")
    
    discovered_agents = []
    
    # Add user agents
    if not msg.agent_type or msg.agent_type == "user":
        for name, info in USER_AGENTS.items():
            discovered_agents.append({
                "name": name,
                "type": "user",
                "address": info["address"],
                "personality": info.get("personality", ""),
                "port": info.get("port", 0)
            })
    
    # Add vending agents
    if not msg.agent_type or msg.agent_type == "vending":
        for name, info in VENDING_AGENTS.items():
            discovered_agents.append({
                "name": name,
                "type": "vending",
                "address": info["address"],
                "port": info.get("port", 0)
            })
    
    response = AgentDiscoveryResponse(
        agents=discovered_agents,
        total_count=len(discovered_agents)
    )
    
    await ctx.send(sender, response)

# REST endpoints for external access
@agent.on_rest_get("/status", HubStatus)
async def get_hub_status(ctx: Context) -> HubStatus:
    """Get hub status via REST"""
    
    # Check agent connectivity
    connected = {}
    for name, info in USER_AGENTS.items():
        connected[name] = info["address"] != "agent1q..."
    
    return HubStatus(
        active_sessions=len(session_manager.active_sessions),
        connected_agents=connected,
        last_activity=datetime.now(UTC).isoformat()
    )

@agent.on_rest_post("/query", UserQuery, AggregatedResponse)
async def handle_rest_query(ctx: Context, req: UserQuery) -> AggregatedResponse:
    """Handle user query via REST and return aggregated response"""
    ctx.logger.info(f"🌐 REST query received: {req.query}")
    
    # Process the query
    await handle_user_query(ctx, "REST_CLIENT", req)
    
    # Wait for responses (simplified - in production use proper async waiting)
    await asyncio.sleep(5)
    
    # Aggregate responses
    session_id = req.session_id or list(session_manager.active_sessions.keys())[-1]
    discussions = session_manager.format_discussion_log(session_id)
    
    return AggregatedResponse(
        session_id=session_id,
        user_query=req.query,
        individual_responses=[],  # Would be populated from actual responses
        discussion_log=discussions,
        final_consensus=session_manager.consensus_results.get(session_id, {}).get("final_strategy"),
        recommended_actions=[
            "Consider Kartik's infrastructure focus",
            "Evaluate Vitalik's mechanism design analysis",
            "Review Mik's momentum trading signals"
        ],
        risk_summary="Mixed risk profile - balanced between conservative and aggressive strategies",
        timestamp=datetime.now(UTC).isoformat()
    )

# Periodic tasks
@agent.on_interval(period=30.0)
async def check_agent_health(ctx: Context):
    """Periodically check health of connected agents"""
    active_agents = 0
    
    for name, info in USER_AGENTS.items():
        if info["address"] != "agent1q...":
            active_agents += 1
    
    if active_agents < len(USER_AGENTS):
        ctx.logger.warning(f"⚠️ Only {active_agents}/{len(USER_AGENTS)} user agents configured")

@agent.on_interval(period=60.0)
async def cleanup_old_sessions(ctx: Context):
    """Clean up old sessions"""
    cutoff_time = datetime.now(UTC) - timedelta(minutes=30)
    
    for session_id, session in list(session_manager.active_sessions.items()):
        session_time = datetime.fromisoformat(session["started"].replace("Z", "+00:00"))
        if session_time < cutoff_time and session["status"] == "active":
            session["status"] = "expired"
            ctx.logger.info(f"🗑️ Expired session: {session_id}")

# Include protocols
agent.include(hub_protocol, publish_manifest=True)
agent.include(collaboration_protocol, publish_manifest=True)

if __name__ == "__main__":
    print(f"""
🌐 Central Hub Agent Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
• Message broadcasting to all user agents
• Discussion aggregation and logging
• Session management
• Agent discovery and registration
• REST API endpoints

Connected User Agents:
""")
    for name, info in USER_AGENTS.items():
        print(f"  {info['emoji']} {name}: {info['personality']}")
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready to orchestrate multi-agent discussions!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()