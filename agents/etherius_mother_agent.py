"""
Etherius Mother Agent - The Genesis Agent
Creates new agents from natural language descriptions and manages the EtheriusVerse
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, UTC
from enum import Enum
from dotenv import load_dotenv
import subprocess
import tempfile
from pathlib import Path

from uagents import Agent, Context, Model, Protocol

import openai

load_dotenv()

# Agent configuration
agent = Agent(
    name="etherius_mother",
    seed=os.getenv("AGENT_SEED_PHRASE", "etherius_mother_genesis_seed_2024"),
    port=int(os.getenv("ETHERIUS_MOTHER_PORT", 8105)),
    endpoint=[f"http://localhost:{os.getenv('ETHERIUS_MOTHER_PORT', 8105)}/submit"],
    mailbox=True
)

# OpenAI configuration
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Agent types
class AgentType(str, Enum):
    SERVICE = "service"
    ANALYZER = "analyzer"
    TRADER = "trader"
    CREATOR = "creator"
    MONITOR = "monitor"
    CONNECTOR = "connector"
    UTILITY = "utility"

# Agent templates
AGENT_TEMPLATES = {
    AgentType.SERVICE: """
from uagents import Agent, Context, Model, Protocol

from datetime import datetime, UTC

agent = Agent(
    name="{name}",
    seed="{seed}",
    port={port},
    endpoint=["http://localhost:{port}/submit"],
    mailbox=True
)

class RequestModel(Model):
    query: str

class ResponseModel(Model):
    result: str
    timestamp: str

protocol = Protocol(name="{name}_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🚀 {display_name} started!")
    ctx.logger.info(f"📍 Address: {{agent.address}}")

@protocol.on_message(model=RequestModel, replies=ResponseModel)
async def handle_request(ctx: Context, sender: str, msg: RequestModel):
    ctx.logger.info(f"Request from {{sender}}: {{msg.query}}")
    # {custom_logic}
    response = ResponseModel(
        result="Processed: " + msg.query,
        timestamp=datetime.now(UTC).isoformat()
    )
    await ctx.send(sender, response)

agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
""",
    AgentType.ANALYZER: """
from uagents import Agent, Context, Model, Protocol

from typing import Dict, List, Any
import random

agent = Agent(
    name="{name}",
    seed="{seed}",
    port={port},
    endpoint=["http://localhost:{port}/submit"],
    mailbox=True
)

class AnalysisRequest(Model):
    target: str
    depth: str

class AnalysisResult(Model):
    metrics: Dict[str, Any]
    insights: List[str]
    score: float

protocol = Protocol(name="{name}_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"📊 {display_name} Analyzer started!")

@protocol.on_message(model=AnalysisRequest, replies=AnalysisResult)
async def analyze(ctx: Context, sender: str, msg: AnalysisRequest):
    # {custom_logic}
    metrics = {{"analyzed": msg.target, "status": "complete"}}
    insights = ["Insight 1", "Insight 2"]
    score = random.uniform(0, 10)
    
    response = AnalysisResult(
        metrics=metrics,
        insights=insights,
        score=score
    )
    await ctx.send(sender, response)

agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
"""
}

# Models
class AgentSpecification(Model):
    name: str
    display_name: str
    description: str
    agent_type: AgentType
    capabilities: List[str]
    port: int
    custom_logic: str
    dependencies: List[str]

class CreationRequest(Model):
    description: str
    agent_type: Optional[AgentType]
    capabilities: Optional[List[str]]
    auto_deploy: bool

class CreationResponse(Model):
    success: bool
    agent_spec: Optional[AgentSpecification]
    file_path: Optional[str]
    agent_address: Optional[str]
    deployment_status: str
    message: str

class AgentListRequest(Model):
    include_status: bool
    filter_type: Optional[AgentType]

class AgentListResponse(Model):
    agents: List[Dict[str, Any]]
    total_count: int
    online_count: int

class AgentUpdateRequest(Model):
    agent_name: str
    new_logic: Optional[str]
    new_capabilities: Optional[List[str]]
    restart: bool

# Agent Generator
class AgentGenerator:
    def __init__(self):
        self.created_agents: Dict[str, AgentSpecification] = {}
        self.next_port = 8200  # Starting port for generated agents
        
    async def generate_from_description(self, description: str, agent_type: Optional[AgentType] = None) -> AgentSpecification:
        """Generate agent specification from natural language"""
        # Use AI to understand requirements
        spec = await self._ai_generate_spec(description, agent_type)
        
        # Ensure unique port
        spec.port = self.next_port
        self.next_port += 1
        
        # Store specification
        self.created_agents[spec.name] = spec
        
        return spec
    
    async def _ai_generate_spec(self, description: str, agent_type: Optional[AgentType]) -> AgentSpecification:
        """Use AI to generate agent specification"""
        try:
            prompt = f"""Create an agent specification from this description:
            "{description}"
            
            Agent type hint: {agent_type.value if agent_type else 'auto-detect'}
            
            Generate:
            1. A snake_case name (max 20 chars)
            2. A display name
            3. A clear description
            4. 3-5 capabilities (single words)
            5. Python code for the main logic (2-3 lines)
            
            Format as JSON with keys: name, display_name, description, agent_type, capabilities, custom_logic"""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You generate agent specifications."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Parse response
            result = response.choices[0].message.content
            
            # Extract JSON (simplified parsing)
            try:
                # Find JSON in response
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    spec_data = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found")
            except:
                # Fallback spec
                spec_data = {
                    "name": "custom_agent",
                    "display_name": "Custom Agent",
                    "description": description,
                    "agent_type": agent_type.value if agent_type else "service",
                    "capabilities": ["process", "respond", "assist"],
                    "custom_logic": "# Process request\nresult = await process_custom_logic(msg)"
                }
            
            # Create specification
            return AgentSpecification(
                name=spec_data.get("name", "custom_agent")[:20],
                display_name=spec_data.get("display_name", "Custom Agent"),
                description=spec_data.get("description", description),
                agent_type=AgentType(spec_data.get("agent_type", "service")),
                capabilities=spec_data.get("capabilities", ["process"]),
                port=8200,  # Will be updated
                custom_logic=spec_data.get("custom_logic", "# Custom logic here"),
                dependencies=[]
            )
            
        except Exception as e:
            # Fallback generation
            name = "agent_" + hashlib.md5(description.encode()).hexdigest()[:8]
            return AgentSpecification(
                name=name,
                display_name="Generated Agent",
                description=description,
                agent_type=agent_type or AgentType.SERVICE,
                capabilities=["general", "processing"],
                port=8200,
                custom_logic="# Auto-generated logic\nresult = 'Processed'",
                dependencies=[]
            )
    
    def generate_agent_code(self, spec: AgentSpecification) -> str:
        """Generate Python code for agent"""
        template = AGENT_TEMPLATES.get(spec.agent_type, AGENT_TEMPLATES[AgentType.SERVICE])
        
        # Generate unique seed
        seed = f"{spec.name}_seed_{datetime.now(UTC).timestamp()}"
        
        # Fill template
        code = template.format(
            name=spec.name,
            display_name=spec.display_name,
            seed=seed,
            port=spec.port,
            custom_logic=spec.custom_logic
        )
        
        return code
    
    async def deploy_agent(self, spec: AgentSpecification, code: str) -> Dict[str, str]:
        """Deploy agent to filesystem and optionally start it"""
        # Create agent file
        file_path = Path("agents") / f"{spec.name}.py"
        file_path.write_text(code)
        
        # Calculate agent address (mock - in production would compute from seed)
        agent_address = "agent1q" + hashlib.sha256(spec.name.encode()).hexdigest()[:58]
        
        return {
            "file_path": str(file_path),
            "agent_address": agent_address,
            "status": "created"
        }
    
    def list_created_agents(self) -> List[Dict[str, Any]]:
        """List all created agents"""
        agents = []
        for name, spec in self.created_agents.items():
            agents.append({
                "name": spec.name,
                "display_name": spec.display_name,
                "type": spec.agent_type.value,
                "capabilities": spec.capabilities,
                "port": spec.port,
                "created": True
            })
        return agents

generator = AgentGenerator()

# Agent Evolution System
class AgentEvolution:
    """System for agents to improve themselves"""
    
    def __init__(self):
        self.evolution_history: Dict[str, List[Dict]] = {}
        
    async def suggest_improvements(self, agent_name: str, performance_data: Dict) -> List[str]:
        """Suggest improvements based on performance"""
        suggestions = []
        
        if performance_data.get("error_rate", 0) > 0.1:
            suggestions.append("Add better error handling")
        
        if performance_data.get("response_time", 0) > 2.0:
            suggestions.append("Optimize processing logic")
        
        if performance_data.get("user_satisfaction", 1.0) < 0.8:
            suggestions.append("Improve response quality")
        
        return suggestions
    
    async def evolve_agent(self, agent_name: str, suggestions: List[str]) -> str:
        """Generate evolved agent code"""
        # This would use AI to improve the agent code based on suggestions
        evolved_code = f"# Evolved version of {agent_name}\n# Improvements: {', '.join(suggestions)}"
        
        # Track evolution
        if agent_name not in self.evolution_history:
            self.evolution_history[agent_name] = []
        
        self.evolution_history[agent_name].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "improvements": suggestions,
            "version": len(self.evolution_history[agent_name]) + 1
        })
        
        return evolved_code

evolution_system = AgentEvolution()

# Protocol definition
mother_protocol = Protocol(name="etherius_mother_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🌟 Etherius Mother - Genesis Agent started!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"🧬 Ready to spawn new agents into the EtheriusVerse!")
    ctx.logger.info(f"🤖 AI-powered agent generation: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("🛑 Etherius Mother shutting down...")
    ctx.logger.info(f"👶 Created {len(generator.created_agents)} agents during session")

@mother_protocol.on_message(model=CreationRequest, replies=CreationResponse)
async def handle_creation(ctx: Context, sender: str, msg: CreationRequest):
    """Create new agent from description"""
    ctx.logger.info(f"🧬 Creation request from {sender}: {msg.description[:50]}...")
    
    try:
        # Generate agent specification
        spec = await generator.generate_from_description(msg.description, msg.agent_type)
        
        # Add requested capabilities
        if msg.capabilities:
            spec.capabilities.extend(msg.capabilities)
        
        # Generate agent code
        code = generator.generate_agent_code(spec)
        
        # Deploy agent
        deployment = await generator.deploy_agent(spec, code)
        
        # Auto-deploy if requested
        deployment_status = "created"
        if msg.auto_deploy:
            try:
                # In production, would actually start the agent process
                subprocess.Popen(
                    ["python", deployment["file_path"]],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                deployment_status = "deployed and running"
            except:
                deployment_status = "created but not running"
        
        response = CreationResponse(
            success=True,
            agent_spec=spec,
            file_path=deployment["file_path"],
            agent_address=deployment["agent_address"],
            deployment_status=deployment_status,
            message=f"Successfully created {spec.display_name}!"
        )
        
        ctx.logger.info(f"✅ Created agent: {spec.name} at port {spec.port}")
        
    except Exception as e:
        ctx.logger.error(f"Creation failed: {e}")
        response = CreationResponse(
            success=False,
            agent_spec=None,
            file_path=None,
            agent_address=None,
            deployment_status="failed",
            message=f"Creation failed: {str(e)}"
        )
    
    await ctx.send(sender, response)

@mother_protocol.on_message(model=AgentListRequest, replies=AgentListResponse)
async def handle_list_agents(ctx: Context, sender: str, msg: AgentListRequest):
    """List all created agents"""
    ctx.logger.info(f"📋 Agent list request from {sender}")
    
    agents = generator.list_created_agents()
    
    # Filter by type if requested
    if msg.filter_type:
        agents = [a for a in agents if a["type"] == msg.filter_type.value]
    
    # Check status if requested (mock)
    online_count = 0
    if msg.include_status:
        for agent_info in agents:
            # Simulate status check
            agent_info["online"] = hash(agent_info["name"]) % 3 != 0  # Mock: 2/3 online
            if agent_info["online"]:
                online_count += 1
    
    response = AgentListResponse(
        agents=agents,
        total_count=len(agents),
        online_count=online_count
    )
    
    await ctx.send(sender, response)

@mother_protocol.on_message(model=AgentUpdateRequest)
async def handle_update(ctx: Context, sender: str, msg: AgentUpdateRequest):
    """Update existing agent"""
    ctx.logger.info(f"🔧 Update request for {msg.agent_name}")
    
    if msg.agent_name in generator.created_agents:
        spec = generator.created_agents[msg.agent_name]
        
        # Update specification
        if msg.new_logic:
            spec.custom_logic = msg.new_logic
        if msg.new_capabilities:
            spec.capabilities = msg.new_capabilities
        
        # Regenerate code
        new_code = generator.generate_agent_code(spec)
        
        # Update file
        file_path = Path("agents") / f"{spec.name}.py"
        file_path.write_text(new_code)
        
        ctx.logger.info(f"✅ Updated {msg.agent_name}")
        
        # Suggest evolution
        suggestions = await evolution_system.suggest_improvements(
            msg.agent_name,
            {"error_rate": 0.05, "response_time": 1.5, "user_satisfaction": 0.9}
        )
        
        if suggestions:
            ctx.logger.info(f"💡 Suggested improvements: {', '.join(suggestions)}")

# Include protocol
agent.include(mother_protocol, publish_manifest=True)

if __name__ == "__main__":
    print("""
🌟 Etherius Mother - Genesis Agent Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
• AI-powered agent generation
• Natural language to code
• Automatic deployment
• Agent evolution system
• Template-based creation
• Self-improvement capabilities
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"From one, many shall rise..."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()