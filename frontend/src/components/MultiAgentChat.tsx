import React, { useState, useEffect, useRef } from 'react';
import { 
  UserAgent, 
  StrategyDiscussion, 
  ConsensusResponse,
  AggregatedResponse 
} from '../types';
import MultiAgentService from '../services/MultiAgentService';
import './MultiAgentChat.css';

const MultiAgentChat: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [discussions, setDiscussions] = useState<StrategyDiscussion[]>([]);
  const [consensus, setConsensus] = useState<ConsensusResponse | null>(null);
  const [userAgents, setUserAgents] = useState<UserAgent[]>([]);
  const [sessionActive, setSessionActive] = useState(false);
  
  const serviceRef = useRef<MultiAgentService | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize service
    const service = new MultiAgentService();
    serviceRef.current = service;
    
    // Get user agents
    setUserAgents(service.getUserAgents());
    
    // Set up event listeners
    service.on('connected', () => {
      console.log('Connected to Multi-Agent Hub');
    });
    
    service.on('discussion', (discussion: StrategyDiscussion) => {
      setDiscussions(prev => [...prev, discussion]);
      scrollToBottom();
    });
    
    service.on('consensus', (consensus: ConsensusResponse) => {
      setConsensus(consensus);
      setIsLoading(false);
      setSessionActive(false);
    });
    
    // Connect to hub
    service.connect();
    
    return () => {
      service.disconnect();
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !serviceRef.current) return;
    
    setIsLoading(true);
    setSessionActive(true);
    setDiscussions([]);
    setConsensus(null);
    
    try {
      await serviceRef.current.broadcastQuery(query);
    } catch (error) {
      console.error('Error broadcasting query:', error);
      setIsLoading(false);
      setSessionActive(false);
    }
  };

  const getAgentStyle = (agentName: string): React.CSSProperties => {
    const agent = userAgents.find(a => a.name === agentName);
    return {
      borderLeft: `4px solid ${agent?.color || '#999'}`,
      backgroundColor: agent ? `${agent.color}10` : '#f5f5f5'
    };
  };

  const formatAllocation = (allocation: Record<string, number>): string => {
    return Object.entries(allocation)
      .map(([key, value]) => `${key}: ${(value * 100).toFixed(0)}%`)
      .join(' | ');
  };

  return (
    <div className="multi-agent-chat">
      <div className="chat-header">
        <h2>🤖 Multi-Agent NFT Strategy Discussion</h2>
        <div className="agent-indicators">
          {userAgents.map(agent => (
            <div key={agent.id} className="agent-indicator">
              <span className="agent-emoji">{agent.emoji}</span>
              <span className="agent-name">{agent.name}</span>
              <span className="agent-personality">{agent.personality}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="discussion-area">
        {discussions.length === 0 && !sessionActive && (
          <div className="welcome-message">
            <h3>Welcome to Multi-Agent NFT Strategy!</h3>
            <p>Ask our team of experts about NFT investments:</p>
            <ul>
              <li>🔨 <strong>Kartik</strong> - Focuses on utility and infrastructure</li>
              <li>🧮 <strong>Vitalik</strong> - Analyzes game theory and mechanisms</li>
              <li>💰 <strong>Mik</strong> - Tracks momentum and trading opportunities</li>
            </ul>
            <p>Try asking: "Find the best NFT strategy for 5 ETH"</p>
          </div>
        )}

        {sessionActive && discussions.length === 0 && (
          <div className="loading-agents">
            <div className="loading-spinner"></div>
            <p>Agents are analyzing your request...</p>
          </div>
        )}

        {discussions.map((discussion, index) => (
          <div 
            key={index} 
            className="discussion-message"
            style={getAgentStyle(discussion.agentName)}
          >
            <div className="message-header">
              <span className="agent-emoji">{discussion.emoji}</span>
              <span className="agent-name">{discussion.agentName}</span>
              <span className="agent-personality">({discussion.agentPersonality})</span>
              <span className="risk-badge risk-{discussion.riskAssessment}">
                Risk: {discussion.riskAssessment}
              </span>
            </div>
            <div className="message-content">
              {discussion.message}
            </div>
            <div className="message-timestamp">
              {new Date(discussion.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}

        {consensus && (
          <div className="consensus-section">
            <h3>📊 Final Consensus</h3>
            <div className="consensus-content">
              <div className="consensus-status">
                {consensus.consensusReached ? '✅ Consensus Reached' : '⚠️ No Full Consensus'}
              </div>
              <div className="consensus-strategy">
                <strong>Strategy:</strong> {consensus.finalStrategy}
              </div>
              <div className="consensus-allocation">
                <strong>Recommended Allocation:</strong>
                <div className="allocation-breakdown">
                  {Object.entries(consensus.allocation).map(([category, percentage]) => (
                    <div key={category} className="allocation-item">
                      <span className="allocation-category">{category}</span>
                      <div className="allocation-bar">
                        <div 
                          className="allocation-fill"
                          style={{ width: `${percentage * 100}%` }}
                        />
                      </div>
                      <span className="allocation-percentage">
                        {(percentage * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="consensus-confidence">
                <strong>Confidence Level:</strong>
                <div className="confidence-meter">
                  <div 
                    className="confidence-fill"
                    style={{ width: `${consensus.confidence * 100}%` }}
                  />
                </div>
                <span>{(consensus.confidence * 100).toFixed(0)}%</span>
              </div>
              {consensus.dissentingOpinions && consensus.dissentingOpinions.length > 0 && (
                <div className="dissenting-opinions">
                  <strong>Dissenting Opinions:</strong>
                  <ul>
                    {consensus.dissentingOpinions.map((opinion, idx) => (
                      <li key={idx}>{opinion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about NFT strategies... (e.g., 'Find the best NFT strategy for 5 ETH')"
          className="query-input"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="broadcast-button"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? (
            <>
              <span className="button-spinner"></span>
              Analyzing...
            </>
          ) : (
            <>
              📡 Broadcast to All Agents
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default MultiAgentChat;