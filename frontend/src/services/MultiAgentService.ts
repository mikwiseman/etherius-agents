import { 
  UserAgent, 
  StrategyDiscussion, 
  ConsensusResponse, 
  AggregatedResponse,
  BroadcastMessage 
} from '../types';

export class MultiAgentService {
  private hubUrl: string = 'http://localhost:8199';
  private ws: WebSocket | null = null;
  private eventListeners: Map<string, Function[]> = new Map();
  private sessionId: string = '';
  
  // User agents configuration
  private userAgents: UserAgent[] = [
    {
      id: 'kartik',
      name: 'Kartik',
      personality: 'Visionary Builder',
      emoji: '🔨',
      color: '#3498db',
      riskTolerance: 0.5,
      expertise: ['infrastructure', 'utility', 'smart-contracts', 'DAOs']
    },
    {
      id: 'vitalik',
      name: 'Vitalik',
      personality: 'Philosophical Analyst',
      emoji: '🧮',
      color: '#9b59b6',
      riskTolerance: 0.4,
      expertise: ['game-theory', 'tokenomics', 'mechanism-design', 'mathematics']
    },
    {
      id: 'mik',
      name: 'Mik',
      personality: 'Street-Smart Trader',
      emoji: '💰',
      color: '#f39c12',
      riskTolerance: 0.7,
      expertise: ['trading', 'momentum', 'whale-watching', 'arbitrage']
    }
  ];

  constructor() {
    this.sessionId = this.generateSessionId();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // For now, use REST API since WebSocket might not be configured
        // In production, this would be a WebSocket connection
        this.emit('connected');
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.emit('disconnected');
  }

  getUserAgents(): UserAgent[] {
    return this.userAgents;
  }

  async broadcastQuery(query: string): Promise<AggregatedResponse> {
    try {
      const response = await fetch(`${this.hubUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          session_id: this.sessionId,
          context: {
            timestamp: new Date().toISOString()
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Emit events for UI updates
      this.emit('response', data);
      
      // Simulate real-time discussion updates
      this.simulateDiscussion(query);
      
      return data;
    } catch (error) {
      console.error('Error broadcasting query:', error);
      // Return mock data for demo
      return this.getMockResponse(query);
    }
  }

  private simulateDiscussion(query: string): void {
    const discussions: StrategyDiscussion[] = [];
    
    // Kartik's initial response
    setTimeout(() => {
      const kartikMsg: StrategyDiscussion = {
        agentName: 'Kartik',
        agentPersonality: 'Visionary Builder',
        message: "Let me analyze the infrastructure and utility aspects of available NFTs...",
        riskAssessment: 'medium',
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId,
        emoji: '🔨'
      };
      discussions.push(kartikMsg);
      this.emit('discussion', kartikMsg);
    }, 1000);

    // Vitalik's response
    setTimeout(() => {
      const vitalikMsg: StrategyDiscussion = {
        agentName: 'Vitalik',
        agentPersonality: 'Philosophical Analyst',
        message: "Interesting problem. Let me calculate the Nash equilibrium and optimal strategy...",
        riskAssessment: 'calculated',
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId,
        emoji: '🧮'
      };
      discussions.push(vitalikMsg);
      this.emit('discussion', vitalikMsg);
    }, 2000);

    // Mik's response
    setTimeout(() => {
      const mikMsg: StrategyDiscussion = {
        agentName: 'Mik',
        agentPersonality: 'Street-Smart Trader',
        message: "Guys, the floor is pumping! I see 3 hot plays right now. Trust me bro! 🚀",
        riskAssessment: 'high',
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId,
        emoji: '💰'
      };
      discussions.push(mikMsg);
      this.emit('discussion', mikMsg);
    }, 3000);

    // More discussion
    setTimeout(() => {
      const kartikReply: StrategyDiscussion = {
        agentName: 'Kartik',
        agentPersonality: 'Visionary Builder',
        message: "Mik, have you checked if the smart contracts are audited? We need solid fundamentals.",
        riskAssessment: 'medium',
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId,
        emoji: '🔨'
      };
      discussions.push(kartikReply);
      this.emit('discussion', kartikReply);
    }, 4500);

    setTimeout(() => {
      const vitalikReply: StrategyDiscussion = {
        agentName: 'Vitalik',
        agentPersonality: 'Philosophical Analyst',
        message: "The game theory suggests a mixed strategy: 60% established projects, 40% emerging opportunities.",
        riskAssessment: 'calculated',
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId,
        emoji: '🧮'
      };
      discussions.push(vitalikReply);
      this.emit('discussion', vitalikReply);
    }, 6000);

    setTimeout(() => {
      const mikReply: StrategyDiscussion = {
        agentName: 'Mik',
        agentPersonality: 'Street-Smart Trader',
        message: "Fine, but we're missing out on gains! My whale alerts are going crazy! At least put 20% in the hot play!",
        riskAssessment: 'yolo',
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId,
        emoji: '💰'
      };
      discussions.push(mikReply);
      this.emit('discussion', mikReply);
    }, 7500);

    // Final consensus
    setTimeout(() => {
      const consensus: ConsensusResponse = {
        sessionId: this.sessionId,
        consensusReached: true,
        finalStrategy: "Balanced NFT portfolio with focus on utility and calculated risks",
        allocation: {
          'Blue-chip NFTs (BAYC, Punks)': 0.4,
          'Utility NFTs (Gaming, DAOs)': 0.3,
          'Emerging Projects': 0.2,
          'Reserve for opportunities': 0.1
        },
        confidence: 0.75,
        dissentingOpinions: ["Mik wants more allocation to trending projects"]
      };
      this.emit('consensus', consensus);
    }, 9000);
  }

  private getMockResponse(query: string): AggregatedResponse {
    return {
      sessionId: this.sessionId,
      userQuery: query,
      discussions: [
        {
          agentName: 'Kartik',
          agentPersonality: 'Visionary Builder',
          message: "I recommend focusing on NFTs with real utility and strong infrastructure.",
          riskAssessment: 'medium',
          timestamp: new Date().toISOString(),
          sessionId: this.sessionId,
          emoji: '🔨'
        },
        {
          agentName: 'Vitalik',
          agentPersonality: 'Philosophical Analyst',
          message: "The mechanism design of these projects shows interesting game-theoretic properties.",
          riskAssessment: 'calculated',
          timestamp: new Date().toISOString(),
          sessionId: this.sessionId,
          emoji: '🧮'
        },
        {
          agentName: 'Mik',
          agentPersonality: 'Street-Smart Trader',
          message: "Floor's about to pump! I'm seeing whale accumulation. Time to ape in!",
          riskAssessment: 'high',
          timestamp: new Date().toISOString(),
          sessionId: this.sessionId,
          emoji: '💰'
        }
      ],
      consensus: {
        sessionId: this.sessionId,
        consensusReached: true,
        finalStrategy: "Diversified NFT portfolio balancing utility and speculation",
        allocation: {
          'Established Collections': 0.5,
          'Utility NFTs': 0.3,
          'Speculative Plays': 0.2
        },
        confidence: 0.7,
        dissentingOpinions: []
      },
      recommendedActions: [
        "Research smart contract audits",
        "Monitor whale wallet activity",
        "Set stop-loss at -15%",
        "Take profits at 2x on speculative positions"
      ],
      riskSummary: "Medium risk with potential for high returns. Balanced between conservative and aggressive strategies."
    };
  }

  on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)?.push(callback);
  }

  off(event: string, callback: Function): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, ...args: any[]): void {
    const listeners = this.eventListeners.get(event) || [];
    listeners.forEach(listener => listener(...args));
  }
}

export default MultiAgentService;