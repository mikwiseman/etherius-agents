import React from 'react';
import { Agent } from '../types';
import './AgentStatus.css';

interface Props {
  agents: Agent[];
  selectedAgent: Agent | null;
}

const AgentStatus: React.FC<Props> = ({ agents, selectedAgent }) => {
  return (
    <div className="agent-status">
      <h2>Agent Status</h2>
      <div className="agent-list">
        {agents.map((agent) => (
          <div 
            key={agent.id} 
            className={`agent-card ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
          >
            <div className="agent-icon">
              {agent.type === 'vending_machine' && '🎰'}
              {agent.type === 'nft_vending' && '🖼️'}
              {agent.type === 'nft_analyzer' && '📊'}
              {agent.type === 'memecoin_generator' && '🪙'}
              {agent.type === 'orchestrator' && '🎯'}
              {agent.type === 'etherius_mother' && '🌟'}
            </div>
            <div className="agent-info">
              <h4>{agent.name}</h4>
              <p className="agent-type">{agent.type}</p>
              <div className="agent-capabilities">
                {agent.capabilities.slice(0, 2).map((cap, i) => (
                  <span key={i} className="capability-tag">{cap}</span>
                ))}
              </div>
            </div>
            <div className={`agent-status-indicator ${agent.isOnline ? 'online' : 'offline'}`}>
              {agent.isOnline ? '●' : '●'}
            </div>
          </div>
        ))}
      </div>
      
      <div className="system-stats">
        <h3>System Statistics</h3>
        <div className="stat">
          <span>Total Agents:</span>
          <strong>{agents.length}</strong>
        </div>
        <div className="stat">
          <span>Online:</span>
          <strong>{agents.filter(a => a.isOnline).length}</strong>
        </div>
        <div className="stat">
          <span>System Health:</span>
          <strong className="health-good">Operational</strong>
        </div>
      </div>
    </div>
  );
};

export default AgentStatus;