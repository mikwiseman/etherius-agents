import React, { useEffect, useRef, useState } from 'react';
import { Agent } from '../types';
import './EtheriusWorld.css';

interface Props {
  agents: Agent[];
  selectedAgent: Agent | null;
  onAgentClick: (agent: Agent) => void;
}

interface AgentSprite {
  agent: Agent;
  x: number;
  y: number;
  vx: number;
  vy: number;
  targetX: number;
  targetY: number;
  message: string | null;
  messageTimer: number;
  color: string;
  emoji: string;
}

const AGENT_EMOJIS: { [key: string]: string } = {
  vending_machine: '🎰',
  nft_vending: '🖼️',
  nft_analyzer: '📊',
  memecoin_generator: '🪙',
  orchestrator: '🎯',
  etherius_mother: '🌟'
};

const AGENT_COLORS: { [key: string]: string } = {
  vending_machine: '#FF6B6B',
  nft_vending: '#4ECDC4',
  nft_analyzer: '#45B7D1',
  memecoin_generator: '#F9CA24',
  orchestrator: '#A55EEA',
  etherius_mother: '#FFD93D'
};

const EtheriusWorld: React.FC<Props> = ({ agents, selectedAgent, onAgentClick }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [agentSprites, setAgentSprites] = useState<AgentSprite[]>([]);
  const animationRef = useRef<number>();
  const [hoveredAgent, setHoveredAgent] = useState<Agent | null>(null);

  useEffect(() => {
    // Initialize agent sprites
    const sprites: AgentSprite[] = agents.map((agent, index) => ({
      agent,
      x: Math.random() * 800,
      y: Math.random() * 600,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      targetX: 400 + Math.cos(index * Math.PI * 2 / agents.length) * 200,
      targetY: 300 + Math.sin(index * Math.PI * 2 / agents.length) * 150,
      message: null,
      messageTimer: 0,
      color: AGENT_COLORS[agent.type] || '#999999',
      emoji: AGENT_EMOJIS[agent.type] || '🤖'
    }));
    setAgentSprites(sprites);
  }, [agents]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw background
      drawBackground(ctx, canvas.width, canvas.height);
      
      // Update and draw agents
      agentSprites.forEach(sprite => {
        updateAgentPosition(sprite);
        drawAgent(ctx, sprite, sprite.agent === selectedAgent, sprite.agent === hoveredAgent);
        
        // Draw speech bubble if message exists
        if (sprite.message && sprite.messageTimer > 0) {
          drawSpeechBubble(ctx, sprite.x, sprite.y - 40, sprite.message);
          sprite.messageTimer--;
        }
      });

      // Draw connections between agents
      drawConnections(ctx, agentSprites);

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [agentSprites, selectedAgent, hoveredAgent]);

  const updateAgentPosition = (sprite: AgentSprite) => {
    // Move towards target with some randomness
    const dx = sprite.targetX - sprite.x;
    const dy = sprite.targetY - sprite.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance > 5) {
      sprite.vx += (dx / distance) * 0.1;
      sprite.vy += (dy / distance) * 0.1;
    }

    // Add random movement
    sprite.vx += (Math.random() - 0.5) * 0.2;
    sprite.vy += (Math.random() - 0.5) * 0.2;

    // Apply friction
    sprite.vx *= 0.95;
    sprite.vy *= 0.95;

    // Update position
    sprite.x += sprite.vx;
    sprite.y += sprite.vy;

    // Keep within bounds
    sprite.x = Math.max(50, Math.min(750, sprite.x));
    sprite.y = Math.max(50, Math.min(550, sprite.y));

    // Occasionally change target
    if (Math.random() < 0.01) {
      sprite.targetX = 400 + (Math.random() - 0.5) * 400;
      sprite.targetY = 300 + (Math.random() - 0.5) * 300;
    }
  };

  const drawBackground = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    // Gradient background
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, '#1a1a2e');
    gradient.addColorStop(1, '#16213e');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // Grid pattern
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 50) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 50) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
  };

  const drawAgent = (
    ctx: CanvasRenderingContext2D, 
    sprite: AgentSprite, 
    isSelected: boolean,
    isHovered: boolean
  ) => {
    const size = isSelected ? 50 : (isHovered ? 45 : 40);
    
    // Draw glow effect
    if (isSelected || isHovered) {
      ctx.shadowColor = sprite.color;
      ctx.shadowBlur = 20;
    }

    // Draw circle
    ctx.beginPath();
    ctx.arc(sprite.x, sprite.y, size / 2, 0, Math.PI * 2);
    ctx.fillStyle = sprite.color;
    ctx.fill();
    
    if (isSelected) {
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 3;
      ctx.stroke();
    }

    ctx.shadowBlur = 0;

    // Draw emoji
    ctx.font = `${size * 0.6}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(sprite.emoji, sprite.x, sprite.y);

    // Draw name
    ctx.font = '12px Arial';
    ctx.fillStyle = '#fff';
    ctx.fillText(sprite.agent.name, sprite.x, sprite.y + size / 2 + 15);

    // Draw status indicator
    const statusColor = sprite.agent.isOnline ? '#00ff00' : '#ff0000';
    ctx.beginPath();
    ctx.arc(sprite.x + size / 2 - 5, sprite.y - size / 2 + 5, 4, 0, Math.PI * 2);
    ctx.fillStyle = statusColor;
    ctx.fill();
  };

  const drawSpeechBubble = (ctx: CanvasRenderingContext2D, x: number, y: number, text: string) => {
    ctx.font = '14px Arial';
    const metrics = ctx.measureText(text);
    const padding = 10;
    const width = metrics.width + padding * 2;
    const height = 30;

    // Draw bubble
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.beginPath();
    ctx.roundRect(x - width / 2, y - height, width, height, 10);
    ctx.fill();

    // Draw tail
    ctx.beginPath();
    ctx.moveTo(x - 5, y);
    ctx.lineTo(x + 5, y);
    ctx.lineTo(x, y + 10);
    ctx.closePath();
    ctx.fill();

    // Draw text
    ctx.fillStyle = '#000';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y - height / 2);
  };

  const drawConnections = (ctx: CanvasRenderingContext2D, sprites: AgentSprite[]) => {
    // Draw subtle connections between nearby agents
    sprites.forEach((sprite1, i) => {
      sprites.slice(i + 1).forEach(sprite2 => {
        const dx = sprite2.x - sprite1.x;
        const dy = sprite2.y - sprite1.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 150) {
          const opacity = 1 - (distance / 150);
          ctx.strokeStyle = `rgba(255, 255, 255, ${opacity * 0.2})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(sprite1.x, sprite1.y);
          ctx.lineTo(sprite2.x, sprite2.y);
          ctx.stroke();
        }
      });
    });
  };

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Check if click is on any agent
    agentSprites.forEach(sprite => {
      const dx = x - sprite.x;
      const dy = y - sprite.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 25) {
        onAgentClick(sprite.agent);
        
        // Show message bubble
        sprite.message = "Hello! 👋";
        sprite.messageTimer = 120; // Show for 2 seconds at 60fps
      }
    });
  };

  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Check if hovering over any agent
    let foundHover = false;
    agentSprites.forEach(sprite => {
      const dx = x - sprite.x;
      const dy = y - sprite.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 25) {
        setHoveredAgent(sprite.agent);
        foundHover = true;
        canvas.style.cursor = 'pointer';
      }
    });

    if (!foundHover) {
      setHoveredAgent(null);
      canvas.style.cursor = 'default';
    }
  };

  // Simulate agent activity
  useEffect(() => {
    const interval = setInterval(() => {
      if (agentSprites.length > 0) {
        const randomSprite = agentSprites[Math.floor(Math.random() * agentSprites.length)];
        const messages = [
          "Processing...",
          "Ready! ✨",
          "Working 🔧",
          "Active 🟢",
          "Analyzing 📊"
        ];
        randomSprite.message = messages[Math.floor(Math.random() * messages.length)];
        randomSprite.messageTimer = 90;
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [agentSprites]);

  return (
    <div className="etherius-world">
      <canvas
        ref={canvasRef}
        width={800}
        height={600}
        onClick={handleCanvasClick}
        onMouseMove={handleCanvasMouseMove}
      />
      {hoveredAgent && (
        <div className="agent-tooltip">
          <h3>{hoveredAgent.name}</h3>
          <p>{hoveredAgent.description}</p>
          <p>Status: {hoveredAgent.isOnline ? '🟢 Online' : '🔴 Offline'}</p>
        </div>
      )}
    </div>
  );
};

export default EtheriusWorld;