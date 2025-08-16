# Etherius Agents Development Guide

## 🚀 Project Setup

### Virtual Environment (REQUIRED)
```bash
# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install all dependencies
pip install -r requirements.txt
```

**IMPORTANT**: Always use the virtual environment when running agents or tests.

!!!! CRITICAL: DONT USE MOCK DATA, NEVER!!!!

## 🔍 CRITICAL: Documentation Search Instructions

**When searching for documentation, ALWAYS search for the latest documentation from August 2025 onwards.**
- Include "August 2025" or "2025" in your search queries
- Prioritize the most recent documentation versions
- Look for updated APIs and patterns from 2025

**ALWAYS follow the OpenSEA MCP documentation:**
- **OpenSEA MCP**: https://docs.opensea.io/docs/mcp
- Use this documentation when implementing OpenSEA MCP integrations

## 📚 Official Documentation Links for fetch.ai

**Always reference these official Fetch.ai Innovation Lab docs:**

### Core Documentation
- **Introduction**: https://innovationlab.fetch.ai/resources/docs/intro

### Agent Creation
- **uAgent Creation**: https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation
- **SDK Creation**: https://innovationlab.fetch.ai/resources/docs/agent-creation/sdk-creation
- **uAgents Adapter Guide**: https://innovationlab.fetch.ai/resources/docs/agent-creation/uagents-adapter-guide

### Agent Communication
- **Agent Chat Protocol**: https://innovationlab.fetch.ai/resources/docs/agent-communication/agent-chat-protocol
- **uAgent to uAgent Communication**: https://innovationlab.fetch.ai/resources/docs/agent-communication/uagent-uagent-communication
- **SDK to uAgent Communication**: https://innovationlab.fetch.ai/resources/docs/agent-communication/sdk-uagent-communication
- **SDK to SDK Communication**: https://innovationlab.fetch.ai/resources/docs/agent-communication/sdk-sdk-communication

### Agentverse
- **Agentverse Overview**: https://innovationlab.fetch.ai/resources/docs/agentverse/agentverse
- **Agentverse API Key**: https://innovationlab.fetch.ai/resources/docs/agentverse/agentverse-api-key
- **Searching Agents**: https://innovationlab.fetch.ai/resources/docs/agentverse/searching
- **Agentverse Applications**: https://innovationlab.fetch.ai/resources/docs/agentverse/agentverse-based-application

### ASI:One LLM Integration
- **ASI:One Mini Introduction**: https://innovationlab.fetch.ai/resources/docs/asione/asi1-mini-introduction
- **ASI:One Mini Getting Started**: https://innovationlab.fetch.ai/resources/docs/asione/asi1-mini-getting-started
- **ASI:One Mini API Reference**: https://innovationlab.fetch.ai/resources/docs/asione/asi1-mini-api-reference
- **ASI:One Mini Chat Completion**: https://innovationlab.fetch.ai/resources/docs/asione/asi1-mini-chat-completion
- **ASI:One Mini Function Calling**: https://innovationlab.fetch.ai/resources/docs/asione/asi1-mini-function-calling

### MCP Integration
- **What is MCP**: https://innovationlab.fetch.ai/resources/docs/mcp-integration/what-is-mcp

### Examples

#### On-Chain Integrations
- **On-Chain Agents**: https://innovationlab.fetch.ai/resources/docs/examples/on-chain-examples/on-chain-agents
- **Mettalex Agents**: https://innovationlab.fetch.ai/resources/docs/examples/on-chain-examples/mettalex-agents
- **Solana Agents**: https://innovationlab.fetch.ai/resources/docs/examples/on-chain-examples/solana-agents
- **BNB Chain Agents**: https://innovationlab.fetch.ai/resources/docs/examples/on-chain-examples/bnb-chain-agents

#### Other Agentic Frameworks
- **LangChain Integration**: https://innovationlab.fetch.ai/resources/docs/examples/other-frameworks/langchain
- **AutoGen Integration**: https://innovationlab.fetch.ai/resources/docs/examples/other-frameworks/autogen
- **CrewAI Integration**: https://innovationlab.fetch.ai/resources/docs/examples/other-frameworks/crewai
- **Financial Analysis AI Agent**: https://innovationlab.fetch.ai/resources/docs/examples/other-frameworks/financial-analysis-ai-agent

#### ASI:One Examples
- **ASI1 Mini Language Tutor**: https://innovationlab.fetch.ai/resources/docs/examples/asione/asi1-mini-language-tutor
- **ASI1 Chat System**: https://innovationlab.fetch.ai/resources/docs/examples/asione/asi1-chat-system
- **ASI DeFi AI Agent**: https://innovationlab.fetch.ai/resources/docs/examples/asione/asi-defi-ai-agent
- **ASI LangChain Tavily**: https://innovationlab.fetch.ai/resources/docs/examples/asione/asi-langchain-tavily

#### Chat Protocol Examples
- **ASI1 Compatible uAgents**: https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi1-compatible-uagents
- **Image Analysis Agent**: https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/image-analysis-agent
- **Image Generation Agent**: https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/image-generation-agent
- **Solana Wallet Agent**: https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/solana-wallet-agent

#### uAgents Adapter Examples
- **CrewAI Adapter Example**: https://innovationlab.fetch.ai/resources/docs/examples/adapters/crewai-adapter-example
- **LangGraph Adapter Example**: https://innovationlab.fetch.ai/resources/docs/examples/adapters/langgraph-adapter-example

#### TransactAI Examples
- **TransactAI Example**: https://innovationlab.fetch.ai/resources/docs/examples/transactAI/transactai-example

#### Integration Examples
- **Stripe Integration**: https://innovationlab.fetch.ai/resources/docs/examples/integrations/stripe-integration
- **Frontend Integration**: https://innovationlab.fetch.ai/resources/docs/examples/integrations/frontend-integration

#### MCP Integration Examples
- **LangGraph MCP Agent**: https://innovationlab.fetch.ai/resources/docs/examples/mcp-integration/langgraph-mcp-agent-example
- **Multi-Server Agent**: https://innovationlab.fetch.ai/resources/docs/examples/mcp-integration/multi-server-agent-example
- **Connect Agent to Multiple Remote MCP Servers**: https://innovationlab.fetch.ai/resources/docs/examples/mcp-integration/connect-an-agent-to-multiple-remote-mcp-servers
- **MCP Adapter Example**: https://innovationlab.fetch.ai/resources/docs/examples/mcp-integration/mcp-adapter-example

## Package Versions & Installation

**CRITICAL: Always use these exact versions for compatibility:**

```bash
# Core uAgents Framework
pip install uagents==0.22.5

# LangChain Integration
pip install langchain==0.3.23
pip install langchain-openai==0.2.14

# LangGraph for Stateful Agents
pip install langgraph==0.3.20

# CrewAI Integration
pip install crewai==0.126.0

# uAgents Adapter (includes LangChain, CrewAI, MCP support)
pip install uagents-adapter==0.4.0
```

**Installation Commands by Use Case:**

```bash
# Basic uAgent development
pip install uagents==0.22.5

# uAgent + LangChain integration
pip install uagents==0.22.5 langchain==0.3.23 langchain-openai==0.2.14

# uAgent + LangGraph workflows
pip install uagents==0.22.5 langgraph==0.3.20 langchain-openai==0.2.14

# uAgent + CrewAI integration
pip install uagents==0.22.5 crewai==0.126.0

# Full framework integration (all adapters)
pip install uagents==0.22.5 uagents-adapter==0.4.0 langchain==0.3.23 langgraph==0.3.20 crewai==0.126.0 langchain-openai==0.2.14
```

**Important Compatibility Notes:**
- `uagents==0.22.5` requires `pydantic` (auto-installed as dependency)
- `uagents-adapter==0.4.0` includes integrations for LangChain, CrewAI, and MCP
- These versions have been tested together and avoid Pydantic v1/v2 compatibility issues
- Always use virtual environments to prevent version conflicts
