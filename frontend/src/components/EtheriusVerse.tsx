import React, { useEffect, useRef, useState, useCallback } from 'react';
import EtheriusWorldService, { WorldAgent } from '../services/EtheriusWorldService';
import { spriteManager } from '../assets/sprites';
import './EtheriusVerse.css';

interface Props {
  onQuerySubmit?: (query: string) => void;
}

const EtheriusVerse: React.FC<Props> = ({ onQuerySubmit }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const worldServiceRef = useRef<EtheriusWorldService | null>(null);
  const animationRef = useRef<number>();
  const lastTimeRef = useRef<number>(0);
  
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<WorldAgent | null>(null);
  const [hoveredObject, setHoveredObject] = useState<any>(null);
  const [query, setQuery] = useState('');
  const [isQueryActive, setIsQueryActive] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [cameraZoom, setCameraZoom] = useState(1);
  const [cameraPan, setCameraPan] = useState({ x: 0, y: 0 });

  // Initialize world
  useEffect(() => {
    const initWorld = async () => {
      // Load sprites
      setIsLoading(true);
      await spriteManager.loadAllSprites();
      
      // Create world service
      worldServiceRef.current = new EtheriusWorldService();
      
      setIsLoading(false);
    };
    
    initWorld();
    
    return () => {
      if (worldServiceRef.current) {
        // Cleanup
      }
    };
  }, []);

  // Animation loop
  useEffect(() => {
    if (isLoading || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const animate = (timestamp: number) => {
      const deltaTime = timestamp - lastTimeRef.current;
      lastTimeRef.current = timestamp;
      
      if (!worldServiceRef.current) return;
      
      // Update world
      worldServiceRef.current.update(deltaTime);
      
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Apply camera transforms
      ctx.save();
      ctx.translate(cameraPan.x, cameraPan.y);
      ctx.scale(cameraZoom, cameraZoom);
      
      // Render world
      renderWorld(ctx);
      
      ctx.restore();
      
      // Render UI overlay
      renderUI(ctx);
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animationRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isLoading, cameraZoom, cameraPan]);

  // Render world
  const renderWorld = (ctx: CanvasRenderingContext2D) => {
    if (!worldServiceRef.current) return;
    
    const worldService = worldServiceRef.current;
    const isometric = worldService.getIsometric();
    const dayNight = worldService.getDayNightCycle();
    
    // Draw background with day/night cycle
    drawBackground(ctx, dayNight);
    
    // Draw floor tiles for each zone
    const zones = worldService.getZones();
    zones.forEach(zone => {
      for (let x = zone.gridStartX; x < zone.gridEndX; x++) {
        for (let y = zone.gridStartY; y < zone.gridEndY; y++) {
          const tileColor = interpolateColor(zone.color, zone.ambientLight, 
            Math.sin((x + y) * 0.5) * 0.1 + 0.5);
          isometric.drawTile(ctx, x, y, tileColor);
        }
      }
    });
    
    // Draw zone labels
    zones.forEach(zone => {
      const centerX = (zone.gridStartX + zone.gridEndX) / 2;
      const centerY = (zone.gridStartY + zone.gridEndY) / 2;
      const pos = isometric.gridToScreen(centerX, centerY);
      
      ctx.font = 'bold 14px "Courier New", monospace';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
      ctx.textAlign = 'center';
      ctx.fillText(zone.name, pos.x, pos.y);
    });
    
    // Get all renderable objects sorted by depth
    const agents = worldService.getAgents();
    const objects = worldService.getObjects();
    
    const renderables = [
      ...objects.map(obj => ({ ...obj, type: 'object' as const })),
      ...agents.map(agent => ({ ...agent, type: 'agent' as const }))
    ].sort((a, b) => {
      const depthA = isometric.calculateDepth(a.gridX, a.gridY, 
        a.type === 'agent' ? (a as any).z : 0);
      const depthB = isometric.calculateDepth(b.gridX, b.gridY,
        b.type === 'agent' ? (b as any).z : 0);
      return depthA - depthB;
    });
    
    // Render all objects and agents
    renderables.forEach(item => {
      if (item.type === 'object') {
        renderWorldObject(ctx, item as any);
      } else {
        renderAgent(ctx, item as WorldAgent);
      }
    });
    
    // Draw particles
    const particles = worldService.getParticles();
    particles.forEach(particle => {
      spriteManager.drawParticle(ctx, particle);
    });
    
    // Draw selection indicator
    const selected = worldService.getSelectedAgent();
    if (selected) {
      drawSelectionIndicator(ctx, selected);
    }
  };

  // Draw background
  const drawBackground = (ctx: CanvasRenderingContext2D, dayNight: number) => {
    // Sky gradient based on time of day
    const gradient = ctx.createLinearGradient(0, 0, 0, 600);
    
    if (dayNight < 0.25) {
      // Night
      gradient.addColorStop(0, '#0a0a1e');
      gradient.addColorStop(1, '#1a1a3e');
    } else if (dayNight < 0.5) {
      // Dawn
      gradient.addColorStop(0, '#2e3e5e');
      gradient.addColorStop(0.5, '#5a6e8e');
      gradient.addColorStop(1, '#8a9eae');
    } else if (dayNight < 0.75) {
      // Day
      gradient.addColorStop(0, '#87ceeb');
      gradient.addColorStop(1, '#98d8e8');
    } else {
      // Dusk
      gradient.addColorStop(0, '#ff6b6b');
      gradient.addColorStop(0.5, '#feca57');
      gradient.addColorStop(1, '#48dbfb');
    }
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 1200, 800);
    
    // Draw digital rain effect
    drawDigitalRain(ctx);
    
    // Draw grid overlay
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < 1200; x += 50) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 800);
      ctx.stroke();
    }
    for (let y = 0; y < 800; y += 50) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(1200, y);
      ctx.stroke();
    }
  };

  // Draw digital rain
  const drawDigitalRain = (ctx: CanvasRenderingContext2D) => {
    ctx.font = '10px monospace';
    ctx.fillStyle = 'rgba(0, 255, 0, 0.1)';
    
    for (let i = 0; i < 20; i++) {
      const x = Math.random() * 1200;
      const y = (Date.now() / 20 + i * 100) % 800;
      const chars = '01101010011';
      const char = chars[Math.floor(Math.random() * chars.length)];
      ctx.fillText(char, x, y);
    }
  };

  // Render world object
  const renderWorldObject = (ctx: CanvasRenderingContext2D, obj: any) => {
    const isometric = worldServiceRef.current?.getIsometric();
    if (!isometric) return;
    
    const pos = isometric.gridToScreen(obj.gridX, obj.gridY);
    
    // Draw based on object type
    switch (obj.type) {
      case 'terminal':
        drawTerminal(ctx, pos.x, pos.y, obj.active);
        break;
      case 'table':
        drawTable(ctx, pos.x, pos.y);
        break;
      case 'vending':
        drawVendingMachine(ctx, pos.x, pos.y, obj.active);
        break;
      case 'display':
        drawNFTDisplay(ctx, pos.x, pos.y, obj.active);
        break;
      default:
        drawGenericObject(ctx, pos.x, pos.y);
    }
  };

  // Draw terminal
  const drawTerminal = (ctx: CanvasRenderingContext2D, x: number, y: number, active: boolean) => {
    // Base
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(x - 40, y - 60, 80, 60);
    
    // Screen
    ctx.fillStyle = active ? '#00ff00' : '#111';
    ctx.fillRect(x - 35, y - 55, 70, 40);
    
    // Screen content
    if (active) {
      ctx.font = '8px monospace';
      ctx.fillStyle = '#000';
      for (let i = 0; i < 5; i++) {
        ctx.fillText('> data_stream...', x - 30, y - 45 + i * 8);
      }
    }
    
    // Keyboard
    ctx.fillStyle = '#34495e';
    ctx.fillRect(x - 30, y - 10, 60, 10);
  };

  // Draw table
  const drawTable = (ctx: CanvasRenderingContext2D, x: number, y: number) => {
    // Table top
    ctx.fillStyle = '#8b4513';
    ctx.beginPath();
    ctx.moveTo(x - 60, y - 20);
    ctx.lineTo(x + 60, y - 20);
    ctx.lineTo(x + 50, y);
    ctx.lineTo(x - 50, y);
    ctx.closePath();
    ctx.fill();
    
    // Hologram projector
    ctx.fillStyle = '#00ffff';
    ctx.beginPath();
    ctx.arc(x, y - 10, 15, 0, Math.PI * 2);
    ctx.fill();
    
    // Hologram
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.5)';
    ctx.lineWidth = 2;
    for (let i = 0; i < 3; i++) {
      ctx.beginPath();
      ctx.arc(x, y - 30 - i * 10, 20 - i * 5, 0, Math.PI * 2);
      ctx.stroke();
    }
  };

  // Draw vending machine
  const drawVendingMachine = (ctx: CanvasRenderingContext2D, x: number, y: number, active: boolean) => {
    // Body
    ctx.fillStyle = '#ff6b6b';
    ctx.fillRect(x - 30, y - 80, 60, 80);
    
    // Screen
    ctx.fillStyle = active ? '#00ff00' : '#333';
    ctx.fillRect(x - 25, y - 75, 50, 30);
    
    // Display text
    if (active) {
      ctx.font = '10px monospace';
      ctx.fillStyle = '#000';
      ctx.fillText('CRYPTO', x - 20, y - 60);
      ctx.fillText('VENDING', x - 20, y - 50);
    }
    
    // Slot
    ctx.fillStyle = '#000';
    ctx.fillRect(x - 20, y - 20, 40, 10);
    
    // Glow effect
    if (active) {
      ctx.shadowBlur = 20;
      ctx.shadowColor = '#00ff00';
      ctx.strokeStyle = '#00ff00';
      ctx.strokeRect(x - 30, y - 80, 60, 80);
      ctx.shadowBlur = 0;
    }
  };

  // Draw NFT display
  const drawNFTDisplay = (ctx: CanvasRenderingContext2D, x: number, y: number, active: boolean) => {
    // Frame
    ctx.strokeStyle = '#9b59b6';
    ctx.lineWidth = 3;
    ctx.strokeRect(x - 40, y - 60, 80, 60);
    
    // Display
    if (active) {
      // Animated NFT art
      const time = Date.now() / 1000;
      const gradient = ctx.createLinearGradient(x - 35, y - 55, x + 35, y - 5);
      gradient.addColorStop(0, `hsl(${(time * 50) % 360}, 100%, 50%)`);
      gradient.addColorStop(1, `hsl(${(time * 50 + 180) % 360}, 100%, 50%)`);
      ctx.fillStyle = gradient;
      ctx.fillRect(x - 35, y - 55, 70, 50);
    } else {
      ctx.fillStyle = '#222';
      ctx.fillRect(x - 35, y - 55, 70, 50);
    }
    
    // Label
    ctx.font = '10px monospace';
    ctx.fillStyle = '#fff';
    ctx.fillText('NFT #' + Math.floor(Math.random() * 9999), x - 25, y - 65);
  };

  // Draw generic object
  const drawGenericObject = (ctx: CanvasRenderingContext2D, x: number, y: number) => {
    ctx.fillStyle = '#666';
    ctx.fillRect(x - 20, y - 40, 40, 40);
  };

  // Render agent
  const renderAgent = (ctx: CanvasRenderingContext2D, agent: WorldAgent) => {
    // Draw shadow
    ctx.beginPath();
    ctx.ellipse(agent.screenX, agent.screenY + 10, 20, 10, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fill();
    
    // Draw agent sprite or emoji fallback
    const hasSprite = spriteManager.getSprite(agent.id.toLowerCase());
    
    if (hasSprite && hasSprite.loaded) {
      spriteManager.drawSprite(
        ctx,
        agent.id.toLowerCase(),
        agent.screenX,
        agent.screenY,
        agent.animationFrame
      );
    } else {
      // Fallback to emoji rendering
      ctx.font = '40px Arial';
      ctx.fillText(agent.emoji, agent.screenX - 20, agent.screenY - 10);
    }
    
    // Draw name tag
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(agent.screenX - 30, agent.screenY + 15, 60, 20);
    ctx.font = 'bold 12px "Courier New", monospace';
    ctx.fillStyle = agent.color;
    ctx.textAlign = 'center';
    ctx.fillText(agent.name, agent.screenX, agent.screenY + 28);
    
    // Draw activity indicator
    if (agent.activity !== 'idle') {
      const activityIcons: Record<string, string> = {
        'walking': '🚶',
        'talking': '💬',
        'thinking': '🤔',
        'analyzing': '📊',
        'trading': '💹'
      };
      
      ctx.font = '20px Arial';
      ctx.fillText(activityIcons[agent.activity] || '❓', agent.screenX + 25, agent.screenY - 20);
    }
    
    // Draw mood indicator
    const moodColors: Record<string, string> = {
      'happy': '#2ecc71',
      'neutral': '#95a5a6',
      'thinking': '#3498db',
      'excited': '#f39c12',
      'concerned': '#e74c3c'
    };
    
    ctx.beginPath();
    ctx.arc(agent.screenX - 25, agent.screenY - 25, 5, 0, Math.PI * 2);
    ctx.fillStyle = moodColors[agent.mood] || '#95a5a6';
    ctx.fill();
    
    // Draw speech bubble
    if (agent.speech && agent.speechTimer > 0) {
      drawSpeechBubble(ctx, agent.screenX, agent.screenY - 60, agent.speech);
    }
  };

  // Draw speech bubble
  const drawSpeechBubble = (ctx: CanvasRenderingContext2D, x: number, y: number, text: string) => {
    const maxWidth = 200;
    const padding = 10;
    const lineHeight = 16;
    
    // Measure text
    ctx.font = '14px "Courier New", monospace';
    const words = text.split(' ');
    const lines: string[] = [];
    let currentLine = '';
    
    words.forEach(word => {
      const testLine = currentLine + (currentLine ? ' ' : '') + word;
      const metrics = ctx.measureText(testLine);
      
      if (metrics.width > maxWidth - padding * 2) {
        if (currentLine) lines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = testLine;
      }
    });
    if (currentLine) lines.push(currentLine);
    
    const width = Math.min(
      maxWidth,
      Math.max(...lines.map(line => ctx.measureText(line).width)) + padding * 2
    );
    const height = lines.length * lineHeight + padding * 2;
    
    // Draw bubble background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    
    ctx.beginPath();
    ctx.roundRect(x - width / 2, y - height, width, height, 10);
    ctx.fill();
    ctx.stroke();
    
    // Draw tail
    ctx.beginPath();
    ctx.moveTo(x - 10, y);
    ctx.lineTo(x + 10, y);
    ctx.lineTo(x, y + 15);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    
    // Draw text
    ctx.fillStyle = '#000';
    ctx.textAlign = 'center';
    lines.forEach((line, index) => {
      ctx.fillText(line, x, y - height + padding + (index + 1) * lineHeight);
    });
    
    ctx.textAlign = 'left';
  };

  // Draw selection indicator
  const drawSelectionIndicator = (ctx: CanvasRenderingContext2D, agent: WorldAgent) => {
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 3;
    ctx.setLineDash([5, 5]);
    
    ctx.beginPath();
    ctx.ellipse(agent.screenX, agent.screenY + 10, 30, 15, 0, 0, Math.PI * 2);
    ctx.stroke();
    
    ctx.setLineDash([]);
  };

  // Render UI overlay
  const renderUI = (ctx: CanvasRenderingContext2D) => {
    // Selected agent info
    const selected = worldServiceRef.current?.getSelectedAgent();
    if (selected) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
      ctx.fillRect(10, 10, 250, 100);
      
      ctx.fillStyle = selected.color;
      ctx.font = 'bold 16px "Courier New", monospace';
      ctx.fillText(selected.name, 20, 35);
      
      ctx.fillStyle = '#fff';
      ctx.font = '14px "Courier New", monospace';
      ctx.fillText(`Personality: ${selected.personality}`, 20, 55);
      ctx.fillText(`Activity: ${selected.activity}`, 20, 75);
      ctx.fillText(`Mood: ${selected.mood}`, 20, 95);
    }
    
    // FPS counter
    ctx.fillStyle = 'rgba(0, 255, 0, 0.8)';
    ctx.font = '12px monospace';
    ctx.fillText(`FPS: ${Math.round(1000 / (16.67))}`, 10, 790);
  };

  // Handle canvas click
  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || !worldServiceRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (event.clientX - rect.left - cameraPan.x) / cameraZoom;
    const y = (event.clientY - rect.top - cameraPan.y) / cameraZoom;
    
    worldServiceRef.current.handleClick(x, y);
    setSelectedAgent(worldServiceRef.current.getSelectedAgent());
  };

  // Handle canvas mouse move
  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (event.clientX - rect.left - cameraPan.x) / cameraZoom;
    const y = (event.clientY - rect.top - cameraPan.y) / cameraZoom;
    
    // Update cursor based on hover
    canvasRef.current.style.cursor = 'default';
  };

  // Handle query submit
  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !worldServiceRef.current) return;
    
    setIsQueryActive(true);
    await worldServiceRef.current.broadcastQuery(query);
    
    if (onQuerySubmit) {
      onQuerySubmit(query);
    }
    
    setTimeout(() => {
      setIsQueryActive(false);
    }, 10000);
  };

  // Handle zoom
  const handleZoom = (delta: number) => {
    setCameraZoom(prev => Math.max(0.5, Math.min(2, prev + delta)));
  };

  // Handle pan
  const handlePan = (dx: number, dy: number) => {
    setCameraPan(prev => ({
      x: Math.max(-400, Math.min(400, prev.x + dx)),
      y: Math.max(-300, Math.min(300, prev.y + dy))
    }));
  };

  // Interpolate color
  const interpolateColor = (color1: string, color2: string, factor: number): string => {
    const c1 = parseInt(color1.slice(1), 16);
    const c2 = parseInt(color2.slice(1), 16);
    
    const r1 = (c1 >> 16) & 255;
    const g1 = (c1 >> 8) & 255;
    const b1 = c1 & 255;
    
    const r2 = (c2 >> 16) & 255;
    const g2 = (c2 >> 8) & 255;
    const b2 = c2 & 255;
    
    const r = Math.round(r1 + (r2 - r1) * factor);
    const g = Math.round(g1 + (g2 - g1) * factor);
    const b = Math.round(b1 + (b2 - b1) * factor);
    
    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="etherius-verse-loading">
        <div className="loading-spinner"></div>
        <h2>Loading EtheriusVerse...</h2>
        <p>Initializing agents and world assets...</p>
      </div>
    );
  }

  return (
    <div className="etherius-verse">
      <canvas
        ref={canvasRef}
        width={1200}
        height={800}
        onClick={handleCanvasClick}
        onMouseMove={handleCanvasMouseMove}
        className="world-canvas"
      />
      
      {showControls && (
        <div className="controls-panel">
          <h3>🌍 EtheriusVerse</h3>
          
          <div className="camera-controls">
            <h4>Camera</h4>
            <div className="zoom-controls">
              <button onClick={() => handleZoom(-0.1)}>-</button>
              <span>Zoom: {(cameraZoom * 100).toFixed(0)}%</span>
              <button onClick={() => handleZoom(0.1)}>+</button>
            </div>
            <div className="pan-controls">
              <button onClick={() => handlePan(0, -50)}>↑</button>
              <div>
                <button onClick={() => handlePan(-50, 0)}>←</button>
                <button onClick={() => handlePan(50, 0)}>→</button>
              </div>
              <button onClick={() => handlePan(0, 50)}>↓</button>
            </div>
          </div>
          
          {selectedAgent && (
            <div className="selected-agent-info">
              <h4>Selected Agent</h4>
              <div className="agent-card">
                <span className="agent-emoji">{selectedAgent.emoji}</span>
                <div className="agent-details">
                  <strong>{selectedAgent.name}</strong>
                  <small>{selectedAgent.personality}</small>
                  <div className="agent-status">
                    <span className={`mood mood-${selectedAgent.mood}`}>
                      {selectedAgent.mood}
                    </span>
                    <span className="activity">
                      {selectedAgent.activity}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div className="instructions">
            <h4>Controls</h4>
            <ul>
              <li>Click agents to select</li>
              <li>Click ground to move selected agent</li>
              <li>Use camera controls to explore</li>
              <li>Submit queries to start discussions</li>
            </ul>
          </div>
        </div>
      )}
      
      <button 
        className="toggle-controls"
        onClick={() => setShowControls(!showControls)}
      >
        {showControls ? '◀' : '▶'}
      </button>
      
      <form onSubmit={handleQuerySubmit} className="query-panel">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask agents about NFT strategies..."
          disabled={isQueryActive}
          className="query-input"
        />
        <button 
          type="submit"
          disabled={isQueryActive || !query.trim()}
          className="query-submit"
        >
          {isQueryActive ? (
            <>🔄 Processing...</>
          ) : (
            <>📡 Broadcast</>
          )}
        </button>
      </form>
    </div>
  );
};

export default EtheriusVerse;