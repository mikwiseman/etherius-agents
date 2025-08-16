import React, { useEffect, useRef, useState } from 'react';
import './SimsWorld.css';

interface Agent {
  id: string;
  name: string;
  type: string;
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  emoji: string;
  color: string;
  speech: string | null;
  speechTimer: number;
  activity: string;
}

interface VendingMachine {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  emoji: string;
  active: boolean;
}

const SimsWorld: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [vendingMachines, setVendingMachines] = useState<VendingMachine[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [hoveredObject, setHoveredObject] = useState<any>(null);
  const animationRef = useRef<number>();

  // Isometric conversion functions
  const toIsometric = (x: number, y: number) => {
    const isoX = (x - y) * 1;
    const isoY = (x + y) * 0.5;
    return { x: isoX + 400, y: isoY + 200 };
  };

  useEffect(() => {
    // Initialize vending machines in the room
    const machines: VendingMachine[] = [
      {
        id: 'vm1',
        type: 'drinks',
        x: 100,
        y: 100,
        width: 60,
        height: 80,
        color: '#FF6B6B',
        emoji: '🥤',
        active: true
      },
      {
        id: 'vm2',
        type: 'snacks',
        x: 200,
        y: 100,
        width: 60,
        height: 80,
        color: '#4ECDC4',
        emoji: '🍿',
        active: true
      },
      {
        id: 'vm3',
        type: 'nft',
        x: 300,
        y: 100,
        width: 60,
        height: 80,
        color: '#9B59B6',
        emoji: '🖼️',
        active: false
      },
      {
        id: 'vm4',
        type: 'crypto',
        x: 100,
        y: 300,
        width: 60,
        height: 80,
        color: '#F39C12',
        emoji: '🪙',
        active: false
      }
    ];
    setVendingMachines(machines);

    // Initialize agents
    const initialAgents: Agent[] = [
      {
        id: 'agent1',
        name: 'Alice',
        type: 'customer',
        x: 250,
        y: 250,
        targetX: 250,
        targetY: 250,
        emoji: '👩',
        color: '#FF69B4',
        speech: null,
        speechTimer: 0,
        activity: 'idle'
      },
      {
        id: 'agent2',
        name: 'Bob',
        type: 'technician',
        x: 150,
        y: 200,
        targetX: 150,
        targetY: 200,
        emoji: '👨‍🔧',
        color: '#4169E1',
        speech: null,
        speechTimer: 0,
        activity: 'idle'
      },
      {
        id: 'agent3',
        name: 'Eve',
        type: 'manager',
        x: 350,
        y: 350,
        targetX: 350,
        targetY: 350,
        emoji: '👩‍💼',
        color: '#32CD32',
        speech: null,
        speechTimer: 0,
        activity: 'idle'
      }
    ];
    setAgents(initialAgents);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw room floor (isometric)
      drawIsometricFloor(ctx);
      
      // Draw walls
      drawWalls(ctx);
      
      // Draw vending machines
      vendingMachines.forEach(machine => {
        drawVendingMachine(ctx, machine);
      });
      
      // Sort agents by y position for proper depth rendering
      const sortedAgents = [...agents].sort((a, b) => a.y - b.y);
      
      // Update and draw agents
      sortedAgents.forEach(agent => {
        updateAgent(agent);
        drawAgent(ctx, agent);
      });
      
      // Draw UI elements
      if (selectedAgent) {
        drawSelectedIndicator(ctx, selectedAgent);
      }
      
      if (hoveredObject) {
        drawTooltip(ctx, hoveredObject);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [agents, vendingMachines, selectedAgent, hoveredObject]);

  const drawIsometricFloor = (ctx: CanvasRenderingContext2D) => {
    const tileSize = 50;
    const rows = 10;
    const cols = 10;
    
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const x = col * tileSize;
        const y = row * tileSize;
        const iso = toIsometric(x, y);
        
        ctx.fillStyle = (row + col) % 2 === 0 ? '#E8DCC0' : '#D4C4A0';
        ctx.beginPath();
        const p1 = toIsometric(x, y);
        const p2 = toIsometric(x + tileSize, y);
        const p3 = toIsometric(x + tileSize, y + tileSize);
        const p4 = toIsometric(x, y + tileSize);
        
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.lineTo(p3.x, p3.y);
        ctx.lineTo(p4.x, p4.y);
        ctx.closePath();
        ctx.fill();
        
        // Add subtle grid lines
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }
    }
  };

  const drawWalls = (ctx: CanvasRenderingContext2D) => {
    // Back wall
    ctx.fillStyle = '#8B7355';
    const wallHeight = 150;
    
    // Left wall
    ctx.beginPath();
    const leftWall1 = toIsometric(0, 0);
    const leftWall2 = toIsometric(0, 500);
    ctx.moveTo(leftWall1.x, leftWall1.y);
    ctx.lineTo(leftWall1.x, leftWall1.y - wallHeight);
    ctx.lineTo(leftWall2.x, leftWall2.y - wallHeight);
    ctx.lineTo(leftWall2.x, leftWall2.y);
    ctx.closePath();
    ctx.fill();
    
    // Right wall
    ctx.fillStyle = '#A0826D';
    ctx.beginPath();
    const rightWall1 = toIsometric(500, 0);
    const rightWall2 = toIsometric(0, 0);
    ctx.moveTo(rightWall1.x, rightWall1.y);
    ctx.lineTo(rightWall1.x, rightWall1.y - wallHeight);
    ctx.lineTo(rightWall2.x, rightWall2.y - wallHeight);
    ctx.lineTo(rightWall2.x, rightWall2.y);
    ctx.closePath();
    ctx.fill();
    
    // Add wall decorations
    drawWallDecorations(ctx);
  };

  const drawWallDecorations = (ctx: CanvasRenderingContext2D) => {
    // Add posters on walls
    ctx.fillStyle = '#FFE4B5';
    const poster1 = toIsometric(50, 0);
    ctx.fillRect(poster1.x - 20, poster1.y - 100, 40, 50);
    ctx.fillStyle = '#000';
    ctx.font = '20px Arial';
    ctx.fillText('🎨', poster1.x - 10, poster1.y - 65);
    
    // Clock on wall
    const clock = toIsometric(250, 0);
    ctx.beginPath();
    ctx.arc(clock.x, clock.y - 100, 20, 0, Math.PI * 2);
    ctx.fillStyle = '#FFF';
    ctx.fill();
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.font = '16px Arial';
    ctx.fillStyle = '#000';
    ctx.fillText('🕐', clock.x - 8, clock.y - 95);
  };

  const drawVendingMachine = (ctx: CanvasRenderingContext2D, machine: VendingMachine) => {
    const iso = toIsometric(machine.x, machine.y);
    
    // Machine body (3D effect)
    ctx.fillStyle = machine.color;
    
    // Front face
    ctx.fillRect(iso.x - machine.width/2, iso.y - machine.height, machine.width, machine.height);
    
    // Side face (darker)
    ctx.fillStyle = shadeColor(machine.color, -20);
    ctx.beginPath();
    ctx.moveTo(iso.x + machine.width/2, iso.y - machine.height);
    ctx.lineTo(iso.x + machine.width/2 + 15, iso.y - machine.height - 10);
    ctx.lineTo(iso.x + machine.width/2 + 15, iso.y - 10);
    ctx.lineTo(iso.x + machine.width/2, iso.y);
    ctx.closePath();
    ctx.fill();
    
    // Top face (lighter)
    ctx.fillStyle = shadeColor(machine.color, 20);
    ctx.beginPath();
    ctx.moveTo(iso.x - machine.width/2, iso.y - machine.height);
    ctx.lineTo(iso.x - machine.width/2 + 15, iso.y - machine.height - 10);
    ctx.lineTo(iso.x + machine.width/2 + 15, iso.y - machine.height - 10);
    ctx.lineTo(iso.x + machine.width/2, iso.y - machine.height);
    ctx.closePath();
    ctx.fill();
    
    // Screen/Display
    ctx.fillStyle = machine.active ? '#00FF00' : '#333';
    ctx.fillRect(iso.x - machine.width/3, iso.y - machine.height + 10, machine.width * 2/3, 20);
    
    // Emoji icon
    ctx.font = '30px Arial';
    ctx.fillText(machine.emoji, iso.x - 15, iso.y - machine.height/2);
    
    // Status light
    ctx.beginPath();
    ctx.arc(iso.x + machine.width/3, iso.y - machine.height + 20, 5, 0, Math.PI * 2);
    ctx.fillStyle = machine.active ? '#0F0' : '#F00';
    ctx.fill();
    
    // Dispensing slot
    ctx.fillStyle = '#000';
    ctx.fillRect(iso.x - machine.width/3, iso.y - 20, machine.width * 2/3, 10);
  };

  const drawAgent = (ctx: CanvasRenderingContext2D, agent: Agent) => {
    const iso = toIsometric(agent.x, agent.y);
    
    // Shadow
    ctx.beginPath();
    ctx.ellipse(iso.x, iso.y + 5, 20, 10, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fill();
    
    // Body (simple cylinder)
    ctx.fillStyle = agent.color;
    ctx.fillRect(iso.x - 15, iso.y - 40, 30, 35);
    
    // Head (emoji)
    ctx.font = '35px Arial';
    ctx.fillText(agent.emoji, iso.x - 17, iso.y - 35);
    
    // Name tag
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillRect(iso.x - 25, iso.y - 60, 50, 18);
    ctx.fillStyle = '#000';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(agent.name, iso.x, iso.y - 47);
    
    // Activity indicator
    if (agent.activity !== 'idle') {
      ctx.fillStyle = 'rgba(255, 255, 0, 0.7)';
      ctx.beginPath();
      ctx.arc(iso.x, iso.y - 70, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#000';
      ctx.font = '10px Arial';
      ctx.fillText('!', iso.x, iso.y - 67);
    }
    
    // Speech bubble
    if (agent.speech && agent.speechTimer > 0) {
      drawSpeechBubble(ctx, iso.x, iso.y - 80, agent.speech);
      agent.speechTimer--;
    }
    
    ctx.textAlign = 'left';
  };

  const drawSpeechBubble = (ctx: CanvasRenderingContext2D, x: number, y: number, text: string) => {
    const padding = 10;
    ctx.font = '14px Arial';
    const metrics = ctx.measureText(text);
    const width = metrics.width + padding * 2;
    const height = 30;
    
    // Bubble body
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    
    ctx.beginPath();
    ctx.roundRect(x - width/2, y - height, width, height, 10);
    ctx.fill();
    ctx.stroke();
    
    // Tail
    ctx.beginPath();
    ctx.moveTo(x - 5, y);
    ctx.lineTo(x + 5, y);
    ctx.lineTo(x, y + 10);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    
    // Text
    ctx.fillStyle = '#000';
    ctx.textAlign = 'center';
    ctx.fillText(text, x, y - height/2 + 5);
    ctx.textAlign = 'left';
  };

  const drawSelectedIndicator = (ctx: CanvasRenderingContext2D, agent: Agent) => {
    const iso = toIsometric(agent.x, agent.y);
    
    // Selection ring
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.ellipse(iso.x, iso.y + 5, 30, 15, 0, 0, Math.PI * 2);
    ctx.stroke();
    
    // Info panel
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(10, 10, 200, 80);
    ctx.fillStyle = '#FFF';
    ctx.font = '16px Arial';
    ctx.fillText(`Selected: ${agent.name}`, 20, 30);
    ctx.font = '14px Arial';
    ctx.fillText(`Type: ${agent.type}`, 20, 50);
    ctx.fillText(`Activity: ${agent.activity}`, 20, 70);
  };

  const drawTooltip = (ctx: CanvasRenderingContext2D, obj: any) => {
    const mousePos = { x: 400, y: 300 }; // Would get from mouse events
    
    ctx.fillStyle = 'rgba(0, 0, 0, 0.9)';
    ctx.fillRect(mousePos.x + 10, mousePos.y - 30, 150, 50);
    ctx.fillStyle = '#FFF';
    ctx.font = '12px Arial';
    ctx.fillText(obj.name || obj.type, mousePos.x + 20, mousePos.y - 10);
    ctx.fillText(obj.active ? 'Active' : 'Inactive', mousePos.x + 20, mousePos.y + 5);
  };

  const updateAgent = (agent: Agent) => {
    // Move towards target
    const dx = agent.targetX - agent.x;
    const dy = agent.targetY - agent.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance > 2) {
      agent.x += (dx / distance) * 2;
      agent.y += (dy / distance) * 2;
      agent.activity = 'walking';
    } else {
      agent.activity = 'idle';
      
      // Random movement
      if (Math.random() < 0.01) {
        agent.targetX = Math.random() * 400 + 50;
        agent.targetY = Math.random() * 400 + 50;
      }
      
      // Random interaction with vending machines
      if (Math.random() < 0.005) {
        const nearbyMachine = vendingMachines[Math.floor(Math.random() * vendingMachines.length)];
        agent.targetX = nearbyMachine.x + 50;
        agent.targetY = nearbyMachine.y;
        agent.speech = `Getting ${nearbyMachine.type}!`;
        agent.speechTimer = 120;
        agent.activity = 'buying';
      }
    }
    
    // Random speech
    if (Math.random() < 0.003 && agent.speechTimer <= 0) {
      const speeches = [
        "Hello there!",
        "Nice day!",
        "I need coffee...",
        "Where's the NFT machine?",
        "Crypto time!",
        "Anyone seen Bob?",
        "This place is cool!"
      ];
      agent.speech = speeches[Math.floor(Math.random() * speeches.length)];
      agent.speechTimer = 150;
    }
  };

  const shadeColor = (color: string, percent: number) => {
    const num = parseInt(color.replace("#", ""), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) + amt;
    const G = (num >> 8 & 0x00FF) + amt;
    const B = (num & 0x0000FF) + amt;
    return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
      (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
      (B < 255 ? B < 1 ? 0 : B : 255))
      .toString(16).slice(1);
  };

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Check if clicking on an agent
    agents.forEach(agent => {
      const iso = toIsometric(agent.x, agent.y);
      const dx = x - iso.x;
      const dy = y - (iso.y - 20);
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 30) {
        setSelectedAgent(agent);
        agent.speech = "Hi! I'm selected!";
        agent.speechTimer = 100;
      }
    });
    
    // Check if clicking on a vending machine
    vendingMachines.forEach(machine => {
      const iso = toIsometric(machine.x, machine.y);
      if (x > iso.x - machine.width/2 && x < iso.x + machine.width/2 &&
          y > iso.y - machine.height && y < iso.y) {
        // Make nearest agent go to machine
        if (selectedAgent) {
          selectedAgent.targetX = machine.x + 50;
          selectedAgent.targetY = machine.y;
          selectedAgent.speech = `Going to ${machine.type} machine!`;
          selectedAgent.speechTimer = 100;
        }
      }
    });
  };

  return (
    <div className="sims-world-container">
      <canvas
        ref={canvasRef}
        width={900}
        height={600}
        onClick={handleCanvasClick}
        className="sims-canvas"
      />
      <div className="controls-panel">
        <h3>🏠 EtheriusVerse Room</h3>
        <div className="agents-list">
          <h4>Agents:</h4>
          {agents.map(agent => (
            <div 
              key={agent.id} 
              className={`agent-item ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
              onClick={() => setSelectedAgent(agent)}
            >
              <span>{agent.emoji}</span>
              <span>{agent.name}</span>
              <span className="agent-status">{agent.activity}</span>
            </div>
          ))}
        </div>
        <div className="machines-list">
          <h4>Vending Machines:</h4>
          {vendingMachines.map(machine => (
            <div key={machine.id} className="machine-item">
              <span>{machine.emoji}</span>
              <span>{machine.type}</span>
              <span className={`machine-status ${machine.active ? 'active' : 'inactive'}`}>
                {machine.active ? '●' : '○'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SimsWorld;