"""
Simple Test Hub for Frontend WebSocket Connection
"""

import asyncio
import json
from aiohttp import web, WSMsgType
import aiohttp_cors
from datetime import datetime

# Store WebSocket connections
websockets = set()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    websockets.add(ws)
    
    print(f"✅ WebSocket client connected. Total connections: {len(websockets)}")
    
    # Send initial connection message
    await ws.send_json({
        "type": "connected",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                print(f"📨 Received: {data}")
                
                # Handle different message types
                if data.get("type") == "agent:status:request":
                    # Send mock agent status
                    await ws.send_json({
                        "type": "agent:status",
                        "agents": [
                            {
                                "agentId": "kartik",
                                "agentName": "Kartik",
                                "state": "thinking",
                                "activity": "Analyzing blockchain data",
                                "mood": "thinking",
                                "position": {"x": 3, "y": 3}
                            },
                            {
                                "agentId": "vitalik",
                                "agentName": "Vitalik",
                                "state": "talking",
                                "activity": "Discussing smart contracts",
                                "mood": "happy",
                                "position": {"x": 17, "y": 3}
                            },
                            {
                                "agentId": "mik",
                                "agentName": "Mik",
                                "state": "idle",
                                "activity": "Monitoring markets",
                                "mood": "neutral",
                                "position": {"x": 10, "y": 10}
                            }
                        ]
                    })
                    
                elif data.get("type") in ["query", "user_query"]:
                    # Extract query from payload if it's a user_query
                    query_text = ""
                    session_id = "test"
                    
                    if data.get("type") == "user_query" and "payload" in data:
                        query_text = data["payload"].get("query", "")
                        session_id = data["payload"].get("sessionId", "test")
                    else:
                        query_text = data.get("query", "")
                        session_id = data.get("sessionId", "test")
                    
                    print(f"📝 Processing query: {query_text}")
                    
                    # Simulate agent discussion
                    await asyncio.sleep(1)
                    await ws.send_json({
                        "type": "discussion",
                        "agentName": "Kartik",
                        "agentPersonality": "Visionary Builder",
                        "message": "Great question! Let me analyze this from a technical perspective.",
                        "riskAssessment": "calculated",
                        "timestamp": datetime.utcnow().isoformat(),
                        "sessionId": session_id,
                        "emoji": "🔨"
                    })
                    
                    await asyncio.sleep(2)
                    await ws.send_json({
                        "type": "discussion",
                        "agentName": "Vitalik",
                        "agentPersonality": "Philosophical Analyst",
                        "message": "From a game theory perspective, this approach has interesting implications.",
                        "riskAssessment": "low",
                        "timestamp": datetime.utcnow().isoformat(),
                        "sessionId": session_id,
                        "emoji": "🧮"
                    })
                    
                    await asyncio.sleep(1.5)
                    await ws.send_json({
                        "type": "discussion",
                        "agentName": "Mik",
                        "agentPersonality": "Street-Smart Trader",
                        "message": "Looking at the market momentum, I see potential for a 2-3x return in the short term.",
                        "riskAssessment": "medium",
                        "timestamp": datetime.utcnow().isoformat(),
                        "sessionId": session_id,
                        "emoji": "💰"
                    })
                    
                    await asyncio.sleep(1)
                    await ws.send_json({
                        "type": "consensus",
                        "consensusReached": True,
                        "finalStrategy": "Deploy smart contract with optimized gas fees",
                        "allocation": {
                            "infrastructure": 0.4,
                            "marketing": 0.2,
                            "development": 0.3,
                            "reserve": 0.1
                        },
                        "confidence": 0.85,
                        "dissentingOpinions": []
                    })
                    
                # Echo command for testing
                elif data.get("type") == "command":
                    await ws.send_json({
                        "type": "log",
                        "level": "info",
                        "source": "Hub",
                        "message": f"Command received: {data.get('payload', {}).get('command', 'unknown')}"
                    })
                    
            elif msg.type == WSMsgType.ERROR:
                print(f'❌ WebSocket error: {ws.exception()}')
                
    except Exception as e:
        print(f"❌ WebSocket handler error: {e}")
    finally:
        websockets.remove(ws)
        print(f"👋 WebSocket client disconnected. Remaining connections: {len(websockets)}")
        
    return ws

async def status_handler(request):
    """REST endpoint for hub status"""
    return web.json_response({
        "totalAgents": 3,
        "onlineAgents": 3,
        "activeDiscussions": 0,
        "agents": [
            {
                "id": "kartik",
                "name": "Kartik",
                "address": "agent1q...",
                "personality": "Visionary Builder",
                "emoji": "🔨",
                "isOnline": True,
                "currentActivity": "thinking",
                "capabilities": ["smart_contracts", "defi", "infrastructure"],
                "port": 8200
            },
            {
                "id": "vitalik",
                "name": "Vitalik",
                "address": "agent1q...",
                "personality": "Philosophical Analyst",
                "emoji": "🧮",
                "isOnline": True,
                "currentActivity": "analyzing",
                "capabilities": ["game_theory", "consensus", "research"],
                "port": 8201
            },
            {
                "id": "mik",
                "name": "Mik",
                "address": "agent1q...",
                "personality": "Street-Smart Trader",
                "emoji": "💰",
                "isOnline": True,
                "currentActivity": "trading",
                "capabilities": ["trading", "momentum", "market_analysis"],
                "port": 8202
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    })

async def query_handler(request):
    """REST endpoint for queries"""
    data = await request.json()
    return web.json_response({
        "sessionId": data.get("session_id", f"session_{datetime.utcnow().timestamp()}"),
        "primaryResponse": {
            "agent": "hub",
            "message": "Query received and processed"
        },
        "supportingResponses": [],
        "summary": "Agents are analyzing your request",
        "suggestions": ["Ask about NFT strategies", "Explore DeFi opportunities"],
        "agentsUsed": ["kartik", "vitalik", "mik"]
    })

def create_app():
    app = web.Application()
    
    # Setup CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_get('/ws', websocket_handler)
    app.router.add_get('/status', status_handler)
    app.router.add_post('/query', query_handler)
    
    # Configure CORS for all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app

if __name__ == '__main__':
    print("""
🌐 Test Hub Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• WebSocket: ws://localhost:8199/ws
• Status: http://localhost:8199/status
• Query: http://localhost:8199/query
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8199)