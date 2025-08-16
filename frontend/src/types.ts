export interface Agent {
  id: string;
  name: string;
  type: string;
  description: string;
  isOnline: boolean;
  address: string;
  port: number;
  capabilities: string[];
}

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  agentId: string;
  agentName?: string;
}