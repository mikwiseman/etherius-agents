import os
import sys
from dotenv import load_dotenv
from uagents import Agent, Context, Model
from hyperon import MeTTa, E, S, ValueAtom

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Agent configuration
agent = Agent(
    name="metta_agent",
    seed="metta_agent_seed_2025",
    port=8233,
    endpoint=[f"http://localhost:8233/submit"]
)

# Message models
class MettaQueryRequest(Model):
    query: str

class BroadcastMessage(Model):
    message: str
    original_sender: str

# Initialize MeTTa instance
metta = MeTTa()

def initialize_nft_knowledge():
    """Initialize the NFT/Ethereum knowledge graph"""
    
    # NFT Collections → Chains
    metta.space().add_atom(E(S("collection"), S("pudgy-penguins"), S("ethereum")))
    metta.space().add_atom(E(S("collection"), S("bored-apes"), S("ethereum")))
    metta.space().add_atom(E(S("collection"), S("azuki"), S("ethereum")))
    metta.space().add_atom(E(S("collection"), S("doodles"), S("ethereum")))
    metta.space().add_atom(E(S("collection"), S("cryptopunks"), S("ethereum")))
    metta.space().add_atom(E(S("collection"), S("moonbirds"), S("ethereum")))
    metta.space().add_atom(E(S("collection"), S("degods"), S("solana")))
    metta.space().add_atom(E(S("collection"), S("okay-bears"), S("solana")))
    metta.space().add_atom(E(S("collection"), S("base-punks"), S("base")))
    metta.space().add_atom(E(S("collection"), S("polygon-apes"), S("polygon")))
    
    # Collections → Floor Prices (example values)
    metta.space().add_atom(E(S("floor_price"), S("pudgy-penguins"), ValueAtom("12.5 ETH")))
    metta.space().add_atom(E(S("floor_price"), S("bored-apes"), ValueAtom("25.0 ETH")))
    metta.space().add_atom(E(S("floor_price"), S("azuki"), ValueAtom("8.5 ETH")))
    metta.space().add_atom(E(S("floor_price"), S("doodles"), ValueAtom("3.2 ETH")))
    metta.space().add_atom(E(S("floor_price"), S("cryptopunks"), ValueAtom("45.0 ETH")))
    metta.space().add_atom(E(S("floor_price"), S("moonbirds"), ValueAtom("2.8 ETH")))
    metta.space().add_atom(E(S("floor_price"), S("degods"), ValueAtom("5.5 SOL")))
    metta.space().add_atom(E(S("floor_price"), S("okay-bears"), ValueAtom("3.2 SOL")))
    
    # Collections → Categories
    metta.space().add_atom(E(S("category"), S("pudgy-penguins"), S("pfp")))
    metta.space().add_atom(E(S("category"), S("bored-apes"), S("pfp")))
    metta.space().add_atom(E(S("category"), S("azuki"), S("anime")))
    metta.space().add_atom(E(S("category"), S("art-blocks"), S("generative-art")))
    metta.space().add_atom(E(S("category"), S("cryptopunks"), S("og-pfp")))
    metta.space().add_atom(E(S("category"), S("moonbirds"), S("pfp")))
    
    # Collections → Trending Status
    metta.space().add_atom(E(S("trending"), S("pudgy-penguins"), S("up")))
    metta.space().add_atom(E(S("trending"), S("bored-apes"), S("stable")))
    metta.space().add_atom(E(S("trending"), S("azuki"), S("down")))
    metta.space().add_atom(E(S("trending"), S("base-punks"), S("up")))
    
    # Similar Collections
    metta.space().add_atom(E(S("similar_to"), S("pudgy-penguins"), S("doodles")))
    metta.space().add_atom(E(S("similar_to"), S("bored-apes"), S("mutant-apes")))
    metta.space().add_atom(E(S("similar_to"), S("cryptopunks"), S("base-punks")))
    metta.space().add_atom(E(S("similar_to"), S("azuki"), S("moonbirds")))
    
    # DeFi Protocols → Types
    metta.space().add_atom(E(S("defi"), S("uniswap"), S("dex")))
    metta.space().add_atom(E(S("defi"), S("sushiswap"), S("dex")))
    metta.space().add_atom(E(S("defi"), S("aave"), S("lending")))
    metta.space().add_atom(E(S("defi"), S("compound"), S("lending")))
    metta.space().add_atom(E(S("defi"), S("opensea"), S("marketplace")))
    metta.space().add_atom(E(S("defi"), S("blur"), S("marketplace")))
    metta.space().add_atom(E(S("defi"), S("looksrare"), S("marketplace")))
    metta.space().add_atom(E(S("defi"), S("maker"), S("stablecoin")))
    metta.space().add_atom(E(S("defi"), S("curve"), S("dex")))
    
    # DeFi → Chains
    metta.space().add_atom(E(S("defi_chain"), S("uniswap"), S("ethereum")))
    metta.space().add_atom(E(S("defi_chain"), S("aave"), S("multi-chain")))
    metta.space().add_atom(E(S("defi_chain"), S("opensea"), S("multi-chain")))
    metta.space().add_atom(E(S("defi_chain"), S("blur"), S("ethereum")))
    
    # Gas Patterns
    metta.space().add_atom(E(S("gas_pattern"), S("weekend"), ValueAtom("lower")))
    metta.space().add_atom(E(S("gas_pattern"), S("weekday_morning"), ValueAtom("higher")))
    metta.space().add_atom(E(S("gas_pattern"), S("nft_mint"), ValueAtom("spike")))
    metta.space().add_atom(E(S("gas_pattern"), S("late_night"), ValueAtom("lowest")))
    metta.space().add_atom(E(S("gas_pattern"), S("defi_farming"), ValueAtom("elevated")))
    
    # Wallet Types
    metta.space().add_atom(E(S("wallet_type"), S("whale"), ValueAtom(">1000 ETH")))
    metta.space().add_atom(E(S("wallet_type"), S("dolphin"), ValueAtom("100-1000 ETH")))
    metta.space().add_atom(E(S("wallet_type"), S("fish"), ValueAtom("10-100 ETH")))
    metta.space().add_atom(E(S("wallet_type"), S("shrimp"), ValueAtom("<10 ETH")))
    
    # NFT Traits → Rarity
    metta.space().add_atom(E(S("trait_rarity"), S("golden-background"), ValueAtom("0.5%")))
    metta.space().add_atom(E(S("trait_rarity"), S("laser-eyes"), ValueAtom("2%")))
    metta.space().add_atom(E(S("trait_rarity"), S("diamond-hands"), ValueAtom("1%")))
    metta.space().add_atom(E(S("trait_rarity"), S("zombie-skin"), ValueAtom("0.3%")))
    
    # Market Signals
    metta.space().add_atom(E(S("market_signal"), S("high_volume"), S("bullish")))
    metta.space().add_atom(E(S("market_signal"), S("whale_accumulation"), S("bullish")))
    metta.space().add_atom(E(S("market_signal"), S("listing_spike"), S("bearish")))
    metta.space().add_atom(E(S("market_signal"), S("holder_decrease"), S("bearish")))

def format_results(results):
    """Format MeTTa query results into readable text"""
    if not results or results == [[]]:
        return "No results found for this query."
    
    # Flatten results if nested
    flat_results = []
    for item in results:
        if isinstance(item, list):
            for subitem in item:
                flat_results.append(str(subitem))
        else:
            flat_results.append(str(item))
    
    if len(flat_results) == 1:
        return f"Result: {flat_results[0]}"
    else:
        return "Results:\n" + "\n".join(f"• {r}" for r in flat_results)

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"MeTTa Agent starting with address: {agent.address}")
    ctx.logger.info("Initializing NFT/Ethereum knowledge graph...")
    initialize_nft_knowledge()
    ctx.logger.info("Knowledge graph initialized successfully")
    ctx.logger.info("Ready to process MeTTa queries")

@agent.on_message(model=MettaQueryRequest)
async def handle_metta_query(ctx: Context, sender: str, msg: MettaQueryRequest):
    ctx.logger.info(f"Received MeTTa query from {sender}: {msg.query}")
    
    try:
        # Add the ! prefix back if it was removed
        query = msg.query
        if not query.startswith("!"):
            query = "!" + query
            
        ctx.logger.info(f"Executing query: {query}")
        
        # Execute the MeTTa query
        results = metta.run(query)
        
        ctx.logger.info(f"Query results: {results}")
        
        # Format the results
        formatted_results = format_results(results)
        
        # Send results back to the sender
        response = BroadcastMessage(
            message=f"MeTTa Query Results:\n{formatted_results}",
            original_sender="metta"
        )
        
        await ctx.send(sender, response)
        ctx.logger.info(f"Sent results back to {sender}")
        
    except Exception as e:
        ctx.logger.error(f"Error processing MeTTa query: {e}")
        error_response = BroadcastMessage(
            message=f"Error processing MeTTa query: {str(e)}",
            original_sender="metta"
        )
        await ctx.send(sender, error_response)

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("MeTTa Agent shutting down")

if __name__ == "__main__":
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MeTTa Knowledge Graph Agent - NFT/Ethereum Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Processes MeTTa queries about NFTs and Ethereum
• Knowledge graph includes collections, DeFi, gas patterns
• Listens on port 8233
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example queries:
• !(match &self (collection $name ethereum) $name)
• !(match &self (floor_price pudgy-penguins $price) $price)
• !(match &self (defi $protocol dex) $protocol)
• !(match &self (trending $collection up) $collection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()