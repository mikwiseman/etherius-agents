import { Agent, Message } from '../types';

export class AgentService {
  private baseUrl: string = 'http://localhost:8104';
  private eventListeners: Map<string, Function[]> = new Map();
  
  connect() {
    // Simulate connection
    setTimeout(() => {
      this.emit('connected');
    }, 1000);
  }
  
  disconnect() {
    this.emit('disconnected');
  }
  
  async getAgents(): Promise<Agent[]> {
    // Mock agents based on what we have running
    return [
      {
        id: 'vending_machine',
        name: 'AI Vending Machine',
        type: 'vending_machine',
        description: 'Smart vending with AI recommendations',
        isOnline: true,
        address: 'agent1qg3yhqaexf2cwfsfjaqvgffxv95tutglme8rdr7eqha0ml6ltemcqc2lf90',
        port: 8100,
        capabilities: ['products', 'pricing', 'recommendations']
      },
      {
        id: 'orchestrator',
        name: 'Orchestrator',
        type: 'orchestrator',
        description: 'Routes requests to appropriate agents',
        isOnline: true,
        address: 'agent1qg3yhqaexf2cwfsfjaqvgffxv95tutglme8rdr7eqha0ml6ltemcqc2lf90',
        port: 8104,
        capabilities: ['routing', 'coordination', 'management']
      },
      {
        id: 'nft_vending',
        name: 'NFT Vending Machine',
        type: 'nft_vending',
        description: 'NFT marketplace with OpenSea integration',
        isOnline: false,
        address: 'agent1q...',
        port: 8101,
        capabilities: ['nft', 'opensea', 'trading']
      },
      {
        id: 'nft_analyzer',
        name: 'NFT Analyzer',
        type: 'nft_analyzer',
        description: 'Deep NFT market analysis',
        isOnline: false,
        address: 'agent1q...',
        port: 8102,
        capabilities: ['analysis', 'predictions', 'trends']
      },
      {
        id: 'memecoin_generator',
        name: 'Memecoin Generator',
        type: 'memecoin_generator',
        description: 'Create and deploy memecoins',
        isOnline: false,
        address: 'agent1q...',
        port: 8103,
        capabilities: ['creation', 'deployment', 'marketing']
      },
      {
        id: 'etherius_mother',
        name: 'Etherius Mother',
        type: 'etherius_mother',
        description: 'The genesis agent that creates new agents',
        isOnline: false,
        address: 'agent1q...',
        port: 8105,
        capabilities: ['generation', 'evolution', 'management']
      }
    ];
  }
  
  async sendMessage(agentId: string, text: string): Promise<string> {
    // Simulate agent response
    const responses: { [key: string]: string[] } = {
      vending_machine: [
        "I have Coca-Cola for $2.50, Smart Water for $3.00, and Snickers for $1.75!",
        "Based on your preferences, I recommend the Kind Bar - it's healthy and delicious!",
        "Special offer: Buy 3 items and get 10% off!"
      ],
      orchestrator: [
        "I'm routing your request to the best agent for the job.",
        "Multiple agents are collaborating on your request.",
        "Request processed successfully by the specialist agents!"
      ],
      nft_vending: [
        "Check out the latest NFT drops from top collections!",
        "Current floor price for Bored Apes: 25 ETH",
        "I can help you find rare NFTs within your budget."
      ],
      nft_analyzer: [
        "Market analysis shows bullish trends for gaming NFTs.",
        "Risk score: 6.5/10, Opportunity score: 8/10",
        "This collection has strong fundamentals and growing community."
      ],
      memecoin_generator: [
        "Generated MoonDoge coin with 1B supply!",
        "Deployment successful! Contract: 0xabc123...",
        "Marketing package ready with social media content!"
      ],
      etherius_mother: [
        "I can create a new agent from your description.",
        "Agent successfully spawned and deployed!",
        "The new agent is learning and evolving..."
      ]
    };
    
    const agentResponses = responses[agentId] || ["I'm processing your request..."];
    return agentResponses[Math.floor(Math.random() * agentResponses.length)];
  }
  
  on(event: string, callback: Function) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)?.push(callback);
  }
  
  private emit(event: string, ...args: any[]) {
    const listeners = this.eventListeners.get(event) || [];
    listeners.forEach(listener => listener(...args));
  }
}