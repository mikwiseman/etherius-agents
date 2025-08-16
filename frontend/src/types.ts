export interface Agent {
  id: string;
  name: string;
  type: string;
  description: string;
  isOnline: boolean;
  address: string;
  port: number;
  capabilities: string[];
  personality?: string;
  emoji?: string;
}

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  agentId: string;
  agentName?: string;
}

// Multi-agent discussion types
export interface UserAgent {
  id: string;
  name: string;
  personality: string;
  emoji: string;
  color: string;
  riskTolerance: number;
  expertise: string[];
}

export interface StrategyDiscussion {
  agentName: string;
  agentPersonality: string;
  message: string;
  riskAssessment: string;
  timestamp: string;
  sessionId: string;
  emoji?: string;
}

export interface AgentOpinion {
  agentName: string;
  opinion: string;
  strength: 'strong_buy' | 'buy' | 'neutral' | 'sell' | 'strong_sell';
  confidence: number;
}

export interface ConsensusResponse {
  sessionId: string;
  consensusReached: boolean;
  finalStrategy: string;
  allocation: Record<string, number>;
  confidence: number;
  dissentingOpinions?: string[];
}

export interface BroadcastMessage {
  userQuery: string;
  sessionId: string;
  timestamp: string;
}

export interface AggregatedResponse {
  sessionId: string;
  userQuery: string;
  discussions: StrategyDiscussion[];
  consensus?: ConsensusResponse;
  recommendedActions: string[];
  riskSummary: string;
}