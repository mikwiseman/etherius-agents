# 🌟 EtheriusVerse - Multi-Agent AI Ecosystem on Fetch.ai

Welcome to **EtheriusVerse**, an advanced multi-agent ecosystem built on Fetch.ai's uAgents framework. This project features intelligent autonomous agents that handle everything from NFT trading to memecoin generation, all orchestrated through a beautiful 2D interactive frontend.

## 🚀 Overview

EtheriusVerse is a comprehensive demonstration of decentralized AI agents working together to create a vibrant digital economy. Each agent specializes in different aspects of the crypto and commerce ecosystem, communicating seamlessly through the Fetch.ai network.

## 🤖 Agent Roster

### 1. **AI Vending Machine Agent** 🎰
- **Capabilities**: Product inventory, dynamic pricing, AI recommendations
- **Features**: 
  - OpenAI-powered product recommendations
  - Dynamic pricing based on demand and inventory
  - X402 payment protocol integration
  - Real-time stock management

### 2. **NFT Vending Machine Agent** 🖼️
- **Capabilities**: NFT sales, OpenSea integration, price negotiation
- **Features**:
  - OpenSea MCP integration for marketplace data
  - Dynamic NFT pricing and negotiation
  - Rarity-based valuation
  - X402 payment processing

### 3. **NFT Analyzer Agent** 📊
- **Capabilities**: Market analysis, trend prediction, investment insights
- **Features**:
  - Deep collection analysis
  - Price predictions with confidence scores
  - Risk assessment and opportunity scoring
  - Multi-collection comparison

### 4. **Memecoin Generator Agent** 🪙
- **Capabilities**: Token creation, deployment, marketing
- **Features**:
  - AI-powered name and symbol generation
  - Smart contract deployment (simulated)
  - Liquidity pool creation
  - Marketing package generation

### 5. **Orchestrator Agent** 🎯
- **Capabilities**: Request routing, multi-agent coordination
- **Features**:
  - Intelligent request classification
  - Multi-agent task distribution
  - Session management
  - Performance optimization

### 6. **Etherius Mother Agent** 🌟
- **Capabilities**: Agent generation, code synthesis, evolution
- **Features**:
  - Natural language to agent creation
  - Template-based code generation
  - Agent evolution and self-improvement
  - Dynamic deployment

## 🛠️ Technology Stack

- **Backend**: Python 3.9+, Fetch.ai uAgents
- **AI Integration**: OpenAI GPT-4, LangChain
- **Blockchain**: Web3.py, Coinbase AgentKit
- **Frontend**: React, TypeScript, Canvas API
- **Communication**: WebSocket, REST APIs
- **Payments**: X402 Protocol, OpenSea MCP

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- Fetch.ai Agentverse account
- OpenAI API key
- OpenSea MCP access (beta)

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/etherius-agents.git
cd etherius-agents
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Start agents:
```bash
# Start individual agents
python agents/orchestrator_agent.py

# Or use the launcher script
python launch_all_agents.py
```

### Frontend Setup

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

## 🎮 Usage

### Via Frontend
1. Open http://localhost:3000 in your browser
2. Watch agents move around in the 2D world
3. Click on any agent to start chatting
4. Use natural language to interact

### Via API
```python
# Example: Query the orchestrator
import requests

response = requests.post("http://localhost:8104/query", json={
    "query": "I want to buy an NFT under 1 ETH",
    "session_id": "user123"
})
```

### Via Fetch.ai Agentverse
Agents are registered on Agentverse and can be accessed through the DeltaV interface.

## 🏗️ Architecture

```
EtheriusVerse/
├── agents/                 # Agent implementations
│   ├── vending_machine_agent.py
│   ├── nft_vending_agent.py
│   ├── nft_analyzer_agent.py
│   ├── memecoin_generator_agent.py
│   ├── orchestrator_agent.py
│   └── etherius_mother_agent.py
├── protocols/             # Communication protocols
├── utils/                 # Utility modules
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── services/      # API services
│   │   └── App.tsx
│   └── package.json
├── config/                # Configuration files
├── requirements.txt       # Python dependencies
└── README.md

```

## 🔑 Key Features

### Dynamic Pricing
Agents implement sophisticated pricing algorithms that respond to:
- Supply and demand
- Market conditions
- Bulk purchases
- Scarcity factors

### AI-Powered Intelligence
Every agent leverages OpenAI for:
- Natural language understanding
- Recommendation generation
- Market analysis
- Content creation

### Decentralized Communication
Agents communicate using:
- Fetch.ai protocols
- Structured message passing
- Session management
- Error handling

### Visual Interaction
The frontend provides:
- Real-time 2D agent visualization
- Interactive chat interfaces
- Status monitoring
- Speech bubbles and animations

## 🚦 Agent Status Monitoring

Monitor agent health through:
- Frontend status panel
- REST API endpoints
- Agentverse dashboard
- Log files

## 🔐 Security Considerations

- Never commit real API keys
- Use environment variables
- Implement rate limiting
- Validate all inputs
- Monitor for anomalies

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📚 Documentation

- [Fetch.ai Docs](https://docs.fetch.ai)
- [uAgents Framework](https://github.com/fetchai/uAgents)
- [OpenAI API](https://platform.openai.com/docs)
- [OpenSea MCP](https://docs.opensea.io/docs/mcp)

## 🐛 Troubleshooting

### Common Issues

1. **Agents not connecting**: Check Agentverse API key
2. **OpenAI errors**: Verify API key and rate limits
3. **Frontend not loading**: Ensure all agents are running
4. **WebSocket errors**: Check port availability

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Fetch.ai team for the uAgents framework
- OpenAI for GPT-4 integration
- OpenSea for MCP access
- Coinbase for AgentKit
- The Web3 community

## 🚀 Future Roadmap

- [ ] Real blockchain deployment
- [ ] Advanced agent learning
- [ ] Cross-chain integration
- [ ] Mobile app
- [ ] DAO governance
- [ ] Agent marketplace

---

**Built with ❤️ for the decentralized future**

*"From one genesis agent, an entire universe emerges..."* - Etherius Mother