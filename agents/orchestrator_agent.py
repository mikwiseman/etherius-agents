"""
Orchestrator Agent - Intelligent Request Routing and Multi-Agent Coordination
Routes user requests to appropriate specialized agents
"""

import os
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, UTC
from enum import Enum
from dotenv import load_dotenv
import asyncio

from uagents import Agent, Context, Model, Protocol
import openai

load_dotenv()

# Agent configuration
agent = Agent(
    name="etherius_orchestrator",
    seed=os.getenv("AGENT_SEED_PHRASE", "orchestrator_unique_seed_2024"),
    port=int(os.getenv("ORCHESTRATOR_PORT", 8104)),
    endpoint=[f"http://localhost:{os.getenv('ORCHESTRATOR_PORT', 8104)}/submit"],
    mailbox=True
)

# OpenAI configuration
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Agent registry with addresses (will be populated dynamically in production)
AGENT_REGISTRY = {
    "vending_machine": {
        "address": "agent1q...",  # Replace with actual address
        "name": "AI Vending Machine",
        "capabilities": ["products", "inventory", "purchase", "recommendations", "food", "drinks"],
        "description": "Handles physical product vending with AI recommendations"
    },
    "nft_vending": {
        "address": "agent1q...",  # Replace with actual address
        "name": "NFT Vending Machine",
        "capabilities": ["nft", "opensea", "marketplace", "digital assets", "collectibles"],
        "description": "Sells and manages NFTs with OpenSea integration"
    },
    "nft_analyzer": {
        "address": "agent1q...",  # Replace with actual address
        "name": "NFT Analyzer",
        "capabilities": ["analysis", "trends", "valuation", "investment", "market data"],
        "description": "Provides deep NFT market analysis and predictions"
    },
    "memecoin_generator": {
        "address": "agent1q...",  # Replace with actual address
        "name": "Memecoin Generator",
        "capabilities": ["create", "deploy", "memecoin", "token", "launch", "liquidity"],
        "description": "Creates and deploys memecoins with Coinbase integration"
    }
}

# Request types
class RequestType(str, Enum):
    PRODUCT_QUERY = "product_query"
    NFT_QUERY = "nft_query"
    MARKET_ANALYSIS = "market_analysis"
    TOKEN_CREATION = "token_creation"
    GENERAL_HELP = "general_help"
    MULTI_AGENT = "multi_agent"

# Models
class UserRequest(Model):
    query: str
    context: Optional[Dict[str, Any]]
    preferred_agent: Optional[str]
    session_id: str

class RoutingDecision(Model):
    primary_agent: str
    secondary_agents: List[str]
    request_type: RequestType
    confidence: float
    reasoning: str

class OrchestratedResponse(Model):
    session_id: str
    primary_response: Dict[str, Any]
    supporting_responses: List[Dict[str, Any]]
    summary: str
    suggestions: List[str]
    agents_used: List[str]

class AgentStatus(Model):
    agent_name: str
    is_online: bool
    last_seen: str
    current_load: int
    capabilities: List[str]

class SystemStatus(Model):
    total_agents: int
    online_agents: int
    agents: List[AgentStatus]
    system_health: str

# Request Router
class IntelligentRouter:
    def __init__(self):
        self.routing_history: Dict[str, List[str]] = {}
        self.agent_performance: Dict[str, float] = {
            agent: 1.0 for agent in AGENT_REGISTRY.keys()
        }
        
    async def classify_request(self, query: str) -> Tuple[RequestType, List[str]]:
        """Classify request and extract keywords"""
        query_lower = query.lower()
        
        # Keyword-based classification
        if any(word in query_lower for word in ["buy", "purchase", "vending", "drink", "snack", "food"]):
            return RequestType.PRODUCT_QUERY, ["vending", "purchase"]
        elif any(word in query_lower for word in ["nft", "opensea", "collection", "mint"]):
            return RequestType.NFT_QUERY, ["nft", "digital"]
        elif any(word in query_lower for word in ["analyze", "trend", "market", "price", "investment"]):
            return RequestType.MARKET_ANALYSIS, ["analysis", "market"]
        elif any(word in query_lower for word in ["create", "deploy", "memecoin", "token", "launch"]):
            return RequestType.TOKEN_CREATION, ["creation", "deployment"]
        elif any(word in query_lower for word in ["help", "what can", "how to", "explain"]):
            return RequestType.GENERAL_HELP, ["help", "information"]
        else:
            # Use AI for complex classification
            return await self._ai_classify(query)
    
    async def _ai_classify(self, query: str) -> Tuple[RequestType, List[str]]:
        """Use AI for complex request classification"""
        try:
            prompt = f"""Classify this request into one of these categories:
            - product_query: Physical products, vending, food, drinks
            - nft_query: NFTs, digital collectibles, OpenSea
            - market_analysis: Analysis, trends, investment advice
            - token_creation: Creating tokens, memecoins, deployment
            - general_help: Help, information, capabilities
            - multi_agent: Requires multiple agents
            
            Query: "{query}"
            
            Respond with just the category name and 2-3 relevant keywords."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You classify user requests."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip().lower()
            parts = result.split(",")
            category = parts[0].strip()
            keywords = [k.strip() for k in parts[1:]] if len(parts) > 1 else []
            
            # Map to RequestType
            type_map = {
                "product_query": RequestType.PRODUCT_QUERY,
                "nft_query": RequestType.NFT_QUERY,
                "market_analysis": RequestType.MARKET_ANALYSIS,
                "token_creation": RequestType.TOKEN_CREATION,
                "general_help": RequestType.GENERAL_HELP,
                "multi_agent": RequestType.MULTI_AGENT
            }
            
            return type_map.get(category, RequestType.GENERAL_HELP), keywords
        except:
            return RequestType.GENERAL_HELP, []
    
    async def route_request(self, query: str, context: Optional[Dict] = None) -> RoutingDecision:
        """Determine optimal agent routing"""
        # Classify request
        request_type, keywords = await self.classify_request(query)
        
        # Score agents based on capabilities
        agent_scores = {}
        for agent_id, agent_info in AGENT_REGISTRY.items():
            score = 0
            for keyword in keywords:
                if any(keyword in cap for cap in agent_info["capabilities"]):
                    score += 1
            
            # Adjust for agent performance
            score *= self.agent_performance.get(agent_id, 1.0)
            agent_scores[agent_id] = score
        
        # Select primary agent
        if agent_scores:
            primary_agent = max(agent_scores, key=agent_scores.get)
            confidence = min(agent_scores[primary_agent] / max(len(keywords), 1), 1.0)
        else:
            primary_agent = "vending_machine"  # Default
            confidence = 0.3
        
        # Determine if secondary agents needed
        secondary_agents = []
        if request_type == RequestType.MULTI_AGENT:
            # Select top 2 other agents
            sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
            secondary_agents = [a[0] for a in sorted_agents[1:3] if a[1] > 0]
        
        # Generate reasoning
        reasoning = f"Based on keywords {keywords}, routing to {AGENT_REGISTRY[primary_agent]['name']}. "
        if secondary_agents:
            reasoning += f"Also consulting {', '.join([AGENT_REGISTRY[a]['name'] for a in secondary_agents])}."
        
        return RoutingDecision(
            primary_agent=primary_agent,
            secondary_agents=secondary_agents,
            request_type=request_type,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def update_performance(self, agent_id: str, success: bool):
        """Update agent performance metrics"""
        current = self.agent_performance.get(agent_id, 1.0)
        if success:
            self.agent_performance[agent_id] = min(current * 1.1, 2.0)
        else:
            self.agent_performance[agent_id] = max(current * 0.9, 0.5)

router = IntelligentRouter()

# Session Manager
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
    def create_session(self, session_id: str) -> None:
        """Create new session"""
        self.sessions[session_id] = {
            "created": datetime.now(UTC).isoformat(),
            "requests": [],
            "agents_used": set(),
            "context": {}
        }
    
    def update_session(self, session_id: str, request: str, agents: List[str]):
        """Update session with new request"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        session = self.sessions[session_id]
        session["requests"].append(request)
        session["agents_used"].update(agents)
        session["last_activity"] = datetime.now(UTC).isoformat()
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context"""
        if session_id in self.sessions:
            return self.sessions[session_id]["context"]
        return {}

session_manager = SessionManager()

# Response Aggregator
async def aggregate_responses(primary: Dict, secondary: List[Dict], query: str) -> str:
    """Aggregate multiple agent responses with AI"""
    try:
        if not secondary:
            return str(primary.get("response", "Response received"))
        
        all_responses = f"Primary: {primary}\n"
        for i, resp in enumerate(secondary):
            all_responses += f"Secondary {i+1}: {resp}\n"
        
        prompt = f"""User query: "{query}"
        
        Agent responses:
        {all_responses[:1000]}
        
        Create a coherent, unified response that combines the information. Keep it concise."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You aggregate multiple agent responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )
        
        return response.choices[0].message.content
    except:
        return str(primary.get("response", "Response aggregated"))

# Protocol definition
orchestrator_protocol = Protocol(name="orchestrator_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🎯 Orchestrator Agent started!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"🤖 Managing {len(AGENT_REGISTRY)} specialized agents")
    ctx.logger.info(f"🌐 Ready to route requests intelligently!")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("🛑 Orchestrator shutting down...")

@orchestrator_protocol.on_message(model=UserRequest, replies=OrchestratedResponse)
async def handle_user_request(ctx: Context, sender: str, msg: UserRequest):
    """Handle and route user requests"""
    ctx.logger.info(f"📨 Request from {sender}: {msg.query[:50]}...")
    
    # Create/update session
    session_manager.update_session(msg.session_id, msg.query, [])
    
    # Route request
    routing = await router.route_request(msg.query, msg.context)
    ctx.logger.info(f"🎯 Routing to {routing.primary_agent} (confidence: {routing.confidence:.2f})")
    
    # Simulate agent communication (in production, would actually send to agents)
    primary_response = {
        "agent": routing.primary_agent,
        "response": f"{AGENT_REGISTRY[routing.primary_agent]['name']} processed: {msg.query}",
        "data": {"status": "success", "details": "Mock response"}
    }
    
    # Get secondary responses if needed
    secondary_responses = []
    for agent_id in routing.secondary_agents:
        secondary_responses.append({
            "agent": agent_id,
            "response": f"{AGENT_REGISTRY[agent_id]['name']} supporting data",
            "data": {"status": "success"}
        })
    
    # Aggregate responses
    summary = await aggregate_responses(primary_response, secondary_responses, msg.query)
    
    # Generate follow-up suggestions
    suggestions = [
        f"Ask about {AGENT_REGISTRY[routing.primary_agent]['name']} capabilities",
        "Request detailed analysis",
        "Explore related features"
    ]
    
    # Update session
    agents_used = [routing.primary_agent] + routing.secondary_agents
    session_manager.update_session(msg.session_id, msg.query, agents_used)
    
    # Update performance metrics
    router.update_performance(routing.primary_agent, True)
    
    response = OrchestratedResponse(
        session_id=msg.session_id,
        primary_response=primary_response,
        supporting_responses=secondary_responses,
        summary=summary,
        suggestions=suggestions,
        agents_used=agents_used
    )
    
    await ctx.send(sender, response)

@orchestrator_protocol.on_message(model=SystemStatus)
async def handle_status_request(ctx: Context, sender: str, msg: Any):
    """Provide system status"""
    ctx.logger.info(f"📊 Status request from {sender}")
    
    # Check agent statuses (mock)
    agent_statuses = []
    online_count = 0
    
    for agent_id, agent_info in AGENT_REGISTRY.items():
        is_online = random.random() > 0.2  # 80% chance online
        if is_online:
            online_count += 1
        
        status = AgentStatus(
            agent_name=agent_info["name"],
            is_online=is_online,
            last_seen=datetime.now(UTC).isoformat(),
            current_load=random.randint(0, 10),
            capabilities=agent_info["capabilities"]
        )
        agent_statuses.append(status)
    
    # Determine system health
    if online_count == len(AGENT_REGISTRY):
        health = "Excellent - All systems operational"
    elif online_count >= len(AGENT_REGISTRY) * 0.75:
        health = "Good - Most systems operational"
    elif online_count >= len(AGENT_REGISTRY) * 0.5:
        health = "Fair - Some systems offline"
    else:
        health = "Poor - Multiple systems offline"
    
    response = SystemStatus(
        total_agents=len(AGENT_REGISTRY),
        online_agents=online_count,
        agents=agent_statuses,
        system_health=health
    )
    
    await ctx.send(sender, response)

# Include protocol
agent.include(orchestrator_protocol, publish_manifest=True)

if __name__ == "__main__":
    print("""
🎯 Orchestrator Agent Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
• Intelligent request routing
• Multi-agent coordination
• Session management
• AI-powered classification
• Performance optimization
• System health monitoring
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()