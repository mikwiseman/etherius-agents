import React, { useState } from 'react';
import './App.css';
import EtheriusVerse from './components/EtheriusVerse';
import MultiAgentChat from './components/MultiAgentChat';

const App: React.FC = () => {
  const [view, setView] = useState<'world' | 'chat'>('world');

  return (
    <div className="App">
      <div className="view-switcher">
        <button 
          className={`view-button ${view === 'chat' ? 'active' : ''}`}
          onClick={() => setView('chat')}
        >
          💬 Multi-Agent Chat
        </button>
        <button 
          className={`view-button ${view === 'world' ? 'active' : ''}`}
          onClick={() => setView('world')}
        >
          🌍 EtheriusVerse
        </button>
      </div>
      
      {view === 'chat' ? (
        <MultiAgentChat />
      ) : (
        <EtheriusVerse />
      )}
    </div>
  );
};

export default App;