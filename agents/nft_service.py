from uagents import Model

class NFTQueryRequest(Model):
    query: str  # Natural language NFT query

class NFTQueryResponse(Model):
    results: str

async def get_nft_info(query: str) -> str:
    """
    Process NFT query using the SimpleOpenSeaMCP client
    """
    try:
        # Import the existing MCP client functionality
        from etherius_agent import SimpleOpenSeaMCP
        from uagents import Context
        
        # Create a minimal context for the MCP client
        class MinimalContext:
            class Logger:
                def info(self, msg): pass
                def error(self, msg): print(f"ERROR: {msg}")
                def warning(self, msg): print(f"WARNING: {msg}")
            logger = Logger()
        
        # Initialize MCP client
        ctx = MinimalContext()
        mcp_client = SimpleOpenSeaMCP(ctx)
        
        # Use the existing query_with_gpt method
        result = await mcp_client.query_with_gpt(query)
        return result
        
    except Exception as e:
        return f"Error fetching NFT information: {str(e)}"