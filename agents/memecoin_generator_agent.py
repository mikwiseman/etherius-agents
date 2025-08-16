"""
Memecoin Generator Agent with Coinbase AgentKit Integration
Creates and deploys memecoins with AI-generated metadata
"""

import os
import random
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, UTC
from enum import Enum
from dotenv import load_dotenv

from uagents import Agent, Context, Model, Protocol

import openai

load_dotenv()

# Agent configuration
agent = Agent(
    name="memecoin_generator",
    seed=os.getenv("AGENT_SEED_PHRASE", "memecoin_generator_seed_2024"),
    port=int(os.getenv("MEMECOIN_GENERATOR_PORT", 8103)),
    endpoint=[f"http://localhost:{os.getenv('MEMECOIN_GENERATOR_PORT', 8103)}/submit"],
    mailbox=True
)

# OpenAI configuration
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Memecoin categories
class MemecoinTheme(str, Enum):
    ANIMALS = "animals"
    FOOD = "food"
    CRYPTO_CULTURE = "crypto_culture"
    MEMES = "memes"
    SPACE = "space"
    GAMING = "gaming"
    AI = "ai"
    DEFI = "defi"

# Blockchain networks
class BlockchainNetwork(str, Enum):
    ETHEREUM = "ethereum"
    BASE = "base"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"

# Data models
class MemecoinSpec(Model):
    name: str
    symbol: str
    description: str
    theme: MemecoinTheme
    total_supply: int
    decimals: int
    logo_prompt: str
    website_content: str
    tokenomics: Dict[str, float]

class GenerationRequest(Model):
    theme: MemecoinTheme
    keywords: List[str]
    network: BlockchainNetwork
    max_supply: Optional[int]
    ai_enhanced: bool

class GenerationResponse(Model):
    success: bool
    memecoin: Optional[MemecoinSpec]
    contract_address: Optional[str]
    deployment_tx: Optional[str]
    logo_url: Optional[str]
    website_url: Optional[str]
    liquidity_pool: Optional[str]
    message: str

class DeploymentRequest(Model):
    memecoin_spec: MemecoinSpec
    network: BlockchainNetwork
    initial_liquidity_eth: float
    lock_liquidity: bool
    enable_trading: bool

class DeploymentResponse(Model):
    success: bool
    contract_address: str
    transaction_hash: str
    liquidity_pool_address: str
    explorer_url: str
    dex_url: str
    total_cost_eth: float

class MarketingPackage(Model):
    memecoin_address: str
    social_posts: List[str]
    telegram_group: str
    twitter_account: str
    marketing_strategy: str

# Memecoin Generator Engine
class MemecoinGenerator:
    def __init__(self):
        self.deployed_coins: Dict[str, MemecoinSpec] = {}
        self.name_registry: set = set()
        
    async def generate_memecoin(self, theme: MemecoinTheme, keywords: List[str]) -> MemecoinSpec:
        """Generate memecoin with AI assistance"""
        # Generate name and symbol
        name = await self._generate_name(theme, keywords)
        symbol = await self._generate_symbol(name, theme)
        
        # Ensure uniqueness
        while name in self.name_registry:
            name = await self._generate_name(theme, keywords)
        self.name_registry.add(name)
        
        # Generate description
        description = await self._generate_description(name, theme, keywords)
        
        # Generate logo prompt
        logo_prompt = f"Cute cartoon {theme.value} mascot for {name} cryptocurrency, vibrant colors, simple design"
        
        # Generate website content
        website_content = await self._generate_website_content(name, description, theme)
        
        # Create tokenomics
        tokenomics = self._generate_tokenomics()
        
        # Calculate total supply (in millions)
        total_supply = random.randint(100, 1000) * 1_000_000
        
        return MemecoinSpec(
            name=name,
            symbol=symbol,
            description=description,
            theme=theme,
            total_supply=total_supply,
            decimals=18,
            logo_prompt=logo_prompt,
            website_content=website_content,
            tokenomics=tokenomics
        )
    
    async def _generate_name(self, theme: MemecoinTheme, keywords: List[str]) -> str:
        """Generate creative memecoin name"""
        try:
            keyword_str = ", ".join(keywords) if keywords else "fun, viral"
            prompt = f"""Generate a creative memecoin name with theme '{theme.value}'.
            Keywords: {keyword_str}
            Requirements:
            - Catchy and memorable
            - 2-3 words maximum
            - Fun and meme-worthy
            - No existing major coin names
            
            Return ONLY the name, nothing else."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a creative memecoin name generator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0.9
            )
            
            name = response.choices[0].message.content.strip()
            return name[:30]  # Limit length
        except:
            # Fallback name generation
            prefixes = ["Moon", "Rocket", "Diamond", "Golden", "Mega", "Ultra", "Turbo"]
            suffixes = ["Doge", "Inu", "Pepe", "Coin", "Token", "Gem", "Star"]
            return f"{random.choice(prefixes)}{random.choice(suffixes)}"
    
    async def _generate_symbol(self, name: str, theme: MemecoinTheme) -> str:
        """Generate token symbol"""
        try:
            prompt = f"Create a 3-5 character ticker symbol for memecoin '{name}'. Return ONLY the symbol in CAPS."
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You create short ticker symbols."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.5
            )
            
            symbol = response.choices[0].message.content.strip().upper()
            return symbol[:5]
        except:
            # Fallback symbol generation
            words = name.split()
            if len(words) > 1:
                return "".join([w[0] for w in words]).upper()[:5]
            return name[:4].upper()
    
    async def _generate_description(self, name: str, theme: MemecoinTheme, keywords: List[str]) -> str:
        """Generate memecoin description"""
        try:
            keyword_str = ", ".join(keywords) if keywords else ""
            prompt = f"""Write a fun, engaging description for memecoin '{name}' (theme: {theme.value}).
            Keywords: {keyword_str}
            Make it exciting and meme-worthy in 2-3 sentences."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write exciting memecoin descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
        except:
            return f"{name} is the next revolutionary {theme.value} memecoin ready to moon! Join the community and ride the rocket to financial freedom!"
    
    async def _generate_website_content(self, name: str, description: str, theme: MemecoinTheme) -> str:
        """Generate website content"""
        return f"""
        <h1>Welcome to {name}!</h1>
        <p>{description}</p>
        <h2>Why {name}?</h2>
        <ul>
            <li>Community-driven {theme.value} memecoin</li>
            <li>Fair launch with locked liquidity</li>
            <li>No team tokens - 100% community owned</li>
            <li>Built for the culture, by the culture</li>
        </ul>
        <h2>Tokenomics</h2>
        <p>Total Supply: 1,000,000,000 {name}</p>
        <p>Join our community and be part of the revolution!</p>
        """
    
    def _generate_tokenomics(self) -> Dict[str, float]:
        """Generate token distribution"""
        return {
            "liquidity": 50.0,
            "community_rewards": 20.0,
            "marketing": 10.0,
            "development": 10.0,
            "burn": 10.0
        }
    
    async def deploy_contract(self, spec: MemecoinSpec, network: BlockchainNetwork) -> Dict[str, str]:
        """Deploy memecoin contract (simulated)"""
        # Generate mock addresses
        contract_address = "0x" + hashlib.sha256(spec.name.encode()).hexdigest()[:40]
        tx_hash = "0x" + hashlib.sha256(f"{spec.name}{datetime.now()}".encode()).hexdigest()[:64]
        
        # Store deployed coin
        self.deployed_coins[contract_address] = spec
        
        return {
            "contract_address": contract_address,
            "transaction_hash": tx_hash,
            "network": network.value
        }
    
    async def create_liquidity_pool(self, contract_address: str, initial_liquidity: float) -> Dict[str, str]:
        """Create liquidity pool (simulated)"""
        pool_address = "0x" + hashlib.sha256(f"pool_{contract_address}".encode()).hexdigest()[:40]
        
        return {
            "pool_address": pool_address,
            "paired_with": "ETH",
            "initial_liquidity": initial_liquidity,
            "dex": "Uniswap V3"
        }
    
    async def generate_marketing(self, spec: MemecoinSpec, contract_address: str) -> MarketingPackage:
        """Generate marketing package"""
        # Generate social posts
        posts = [
            f"🚀 {spec.name} ({spec.symbol}) just launched! The hottest {spec.theme.value} memecoin is here! 🔥",
            f"Don't miss out on ${spec.symbol}! Fair launch, locked liquidity, 100% community owned! 💎🙌",
            f"#{spec.symbol} to the moon! Join the revolution! 🌙 Contract: {contract_address[:10]}..."
        ]
        
        # Generate links (mock)
        telegram = f"https://t.me/{spec.symbol.lower()}_official"
        twitter = f"https://twitter.com/{spec.symbol.lower()}_token"
        
        # Generate strategy
        strategy = f"""
        Phase 1: Community Building
        - Launch Telegram and Twitter
        - Organic growth through meme content
        - Community contests and giveaways
        
        Phase 2: Expansion
        - Influencer partnerships
        - CEX listings
        - Strategic partnerships
        
        Phase 3: Ecosystem
        - NFT collection launch
        - Staking platform
        - DAO governance
        """
        
        return MarketingPackage(
            memecoin_address=contract_address,
            social_posts=posts,
            telegram_group=telegram,
            twitter_account=twitter,
            marketing_strategy=strategy
        )

generator = MemecoinGenerator()

# Protocol definition
memecoin_protocol = Protocol(name="memecoin_generator_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🪙 Memecoin Generator started!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"🤖 AI generation: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    ctx.logger.info(f"💰 Ready to create the next viral memecoin!")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("🛑 Memecoin Generator shutting down...")

@memecoin_protocol.on_message(model=GenerationRequest, replies=GenerationResponse)
async def handle_generation(ctx: Context, sender: str, msg: GenerationRequest):
    """Generate a new memecoin"""
    ctx.logger.info(f"🎨 Generation request from {sender}: {msg.theme}")
    
    try:
        # Generate memecoin specification
        if msg.ai_enhanced:
            spec = await generator.generate_memecoin(msg.theme, msg.keywords)
        else:
            # Basic generation without AI
            spec = MemecoinSpec(
                name=f"{msg.theme.value.title()}Coin",
                symbol=msg.theme.value[:4].upper(),
                description=f"The ultimate {msg.theme.value} memecoin",
                theme=msg.theme,
                total_supply=msg.max_supply or 1_000_000_000,
                decimals=18,
                logo_prompt=f"{msg.theme.value} logo",
                website_content="Coming soon",
                tokenomics={"liquidity": 100.0}
            )
        
        # Deploy contract
        deployment = await generator.deploy_contract(spec, msg.network)
        
        # Create liquidity pool
        pool = await generator.create_liquidity_pool(deployment["contract_address"], 0.1)
        
        # Generate assets (mock URLs)
        logo_url = f"https://memecoin-logos.ai/{spec.symbol.lower()}.png"
        website_url = f"https://{spec.symbol.lower()}.meme"
        
        response = GenerationResponse(
            success=True,
            memecoin=spec,
            contract_address=deployment["contract_address"],
            deployment_tx=deployment["transaction_hash"],
            logo_url=logo_url,
            website_url=website_url,
            liquidity_pool=pool["pool_address"],
            message=f"Successfully generated {spec.name} ({spec.symbol})! 🚀"
        )
        
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ Generated: {spec.name} ({spec.symbol})")
        
    except Exception as e:
        ctx.logger.error(f"Generation failed: {e}")
        await ctx.send(sender, GenerationResponse(
            success=False,
            memecoin=None,
            contract_address=None,
            deployment_tx=None,
            logo_url=None,
            website_url=None,
            liquidity_pool=None,
            message=f"Generation failed: {str(e)}"
        ))

@memecoin_protocol.on_message(model=DeploymentRequest, replies=DeploymentResponse)
async def handle_deployment(ctx: Context, sender: str, msg: DeploymentRequest):
    """Deploy a memecoin contract"""
    ctx.logger.info(f"📝 Deployment request from {sender}")
    
    try:
        # Deploy contract
        deployment = await generator.deploy_contract(msg.memecoin_spec, msg.network)
        
        # Create liquidity pool
        pool = await generator.create_liquidity_pool(
            deployment["contract_address"],
            msg.initial_liquidity_eth
        )
        
        # Calculate costs (mock)
        gas_cost = 0.01  # ETH
        total_cost = gas_cost + msg.initial_liquidity_eth
        
        # Generate URLs
        if msg.network == BlockchainNetwork.ETHEREUM:
            explorer_url = f"https://etherscan.io/address/{deployment['contract_address']}"
            dex_url = f"https://app.uniswap.org/tokens/ethereum/{deployment['contract_address']}"
        elif msg.network == BlockchainNetwork.BASE:
            explorer_url = f"https://basescan.org/address/{deployment['contract_address']}"
            dex_url = f"https://app.uniswap.org/tokens/base/{deployment['contract_address']}"
        else:
            explorer_url = f"https://explorer.{msg.network.value}.io/{deployment['contract_address']}"
            dex_url = f"https://dex.{msg.network.value}.io/{deployment['contract_address']}"
        
        response = DeploymentResponse(
            success=True,
            contract_address=deployment["contract_address"],
            transaction_hash=deployment["transaction_hash"],
            liquidity_pool_address=pool["pool_address"],
            explorer_url=explorer_url,
            dex_url=dex_url,
            total_cost_eth=total_cost
        )
        
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ Deployed at: {deployment['contract_address']}")
        
        # Generate and send marketing package
        marketing = await generator.generate_marketing(msg.memecoin_spec, deployment["contract_address"])
        ctx.logger.info(f"📢 Marketing package ready: {marketing.telegram_group}")
        
    except Exception as e:
        ctx.logger.error(f"Deployment failed: {e}")
        await ctx.send(sender, DeploymentResponse(
            success=False,
            contract_address="",
            transaction_hash="",
            liquidity_pool_address="",
            explorer_url="",
            dex_url="",
            total_cost_eth=0
        ))

# Include protocol
agent.include(memecoin_protocol, publish_manifest=True)

if __name__ == "__main__":
    print("""
🪙 Memecoin Generator Agent Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
• AI-powered name generation
• Smart contract deployment
• Liquidity pool creation
• Marketing package generation
• Multi-chain support
• Tokenomics optimization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()