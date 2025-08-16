import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import EtheriusWorld from './components/EtheriusWorld';
import ChatInterface from './components/ChatInterface';
import AgentStatus from './components/AgentStatus';
import { AgentService } from './services/AgentService';
import { Agent, Message } from './types';

const App: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const agentService = useRef(new AgentService());

  useEffect(() => {
    // Initialize agent service
    agentService.current.connect();
    
    // Set up event listeners
    agentService.current.on('connected', () => {
      setIsConnected(true);
      loadAgents();
    });

    agentService.current.on('disconnected', () => {
      setIsConnected(false);
    });

    agentService.current.on('agentUpdate', (updatedAgent: Agent) => {
      setAgents(prev => prev.map(a => a.id === updatedAgent.id ? updatedAgent : a));
    });

    agentService.current.on('message', (message: Message) => {
      setMessages(prev => [...prev, message]);
    });

    return () => {
      agentService.current.disconnect();
    };
  }, []);

  const loadAgents = async () => {
    const agentList = await agentService.current.getAgents();
    setAgents(agentList);
  };

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgent(agent);
    setMessages([]);
  };

  const handleSendMessage = async (text: string) => {
    if (!selectedAgent) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date(),
      agentId: selectedAgent.id
    };

    setMessages(prev => [...prev, userMessage]);

    // Send to agent
    const response = await agentService.current.sendMessage(selectedAgent.id, text);
    
    const agentMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: response,
      sender: 'agent',
      timestamp: new Date(),
      agentId: selectedAgent.id,
      agentName: selectedAgent.name
    };

    setMessages(prev => [...prev, agentMessage]);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🌟 EtheriusVerse</h1>
        <div className="connection-status">
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </header>

      <div className="main-container">
        <div className="left-panel">
          <AgentStatus agents={agents} selectedAgent={selectedAgent} />
        </div>

        <div className="center-panel">
          <EtheriusWorld 
            agents={agents}
            selectedAgent={selectedAgent}
            onAgentClick={handleAgentClick}
          />
        </div>

        <div className="right-panel">
          {selectedAgent ? (
            <ChatInterface
              agent={selectedAgent}
              messages={messages}
              onSendMessage={handleSendMessage}
            />
          ) : (
            <div className="no-agent-selected">
              <p>Click on an agent to start chatting!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;