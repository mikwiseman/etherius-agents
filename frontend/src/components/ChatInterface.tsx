import React, { useState, useRef, useEffect } from 'react';
import { Agent, Message } from '../types';
import './ChatInterface.css';

interface Props {
  agent: Agent;
  messages: Message[];
  onSendMessage: (text: string) => void;
}

const ChatInterface: React.FC<Props> = ({ agent, messages, onSendMessage }) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      onSendMessage(inputText);
      setInputText('');
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>{agent.name}</h3>
        <span className={`status ${agent.isOnline ? 'online' : 'offline'}`}>
          {agent.isOnline ? '🟢 Online' : '🔴 Offline'}
        </span>
      </div>
      
      <div className="messages-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            <div className="message-content">
              {msg.text}
            </div>
            <div className="message-meta">
              {msg.sender === 'agent' && msg.agentName}
              {' • '}
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={`Ask ${agent.name} something...`}
          className="chat-input"
        />
        <button type="submit" className="send-button">
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;