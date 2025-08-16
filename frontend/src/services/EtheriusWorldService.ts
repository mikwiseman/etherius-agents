/**
 * EtheriusWorldService - Manages the world state and agent interactions
 */

import { IsometricUtils, Point2D } from '../utils/isometric';
import { spriteManager, Particle } from '../assets/sprites';
import MultiAgentService from './MultiAgentService';
import { UserAgent, StrategyDiscussion, ConsensusResponse } from '../types';

export interface WorldAgent {
  id: string;
  name: string;
  personality: string;
  emoji: string;
  color: string;
  gridX: number;
  gridY: number;
  targetX: number;
  targetY: number;
  screenX: number;
  screenY: number;
  z: number;
  activity: 'idle' | 'walking' | 'talking' | 'thinking' | 'analyzing' | 'trading';
  speech: string | null;
  speechTimer: number;
  animationFrame: number;
  animationTimer: number;
  mood: 'happy' | 'neutral' | 'thinking' | 'excited' | 'concerned';
  path: Point2D[] | null;
  pathIndex: number;
  moveSpeed: number;
}

export interface WorldObject {
  id: string;
  type: 'terminal' | 'table' | 'vending' | 'display' | 'chair';
  gridX: number;
  gridY: number;
  width: number;
  height: number;
  interactive: boolean;
  active: boolean;
  owner?: string;
}

export interface Zone {
  id: string;
  name: string;
  type: 'tech' | 'trading' | 'gallery' | 'conference' | 'lounge';
  gridStartX: number;
  gridStartY: number;
  gridEndX: number;
  gridEndY: number;
  color: string;
  ambientLight: string;
}

export class EtheriusWorldService {
  private isometric: IsometricUtils;
  private agents: Map<string, WorldAgent> = new Map();
  private objects: Map<string, WorldObject> = new Map();
  private zones: Zone[] = [];
  private particles: Particle[] = [];
  private multiAgentService: MultiAgentService;
  private worldTime: number = 0;
  private dayNightCycle: number = 0;
  private selectedAgent: WorldAgent | null = null;
  
  // Grid dimensions
  private gridWidth: number = 20;
  private gridHeight: number = 20;
  private tileOccupancy: boolean[][] = [];

  constructor() {
    this.isometric = new IsometricUtils(64, 32, 450, 100);
    this.multiAgentService = new MultiAgentService();
    this.initializeWorld();
  }

  /**
   * Initialize the world
   */
  private initializeWorld(): void {
    // Initialize tile occupancy grid
    this.tileOccupancy = Array(this.gridWidth).fill(null).map(() => 
      Array(this.gridHeight).fill(false)
    );

    // Create zones
    this.createZones();
    
    // Create agents
    this.createAgents();
    
    // Create world objects
    this.createWorldObjects();
    
    // Connect to multi-agent hub
    this.connectToHub();
  }

  /**
   * Create world zones
   */
  private createZones(): void {
    this.zones = [
      {
        id: 'tech-lab',
        name: 'Tech Lab',
        type: 'tech',
        gridStartX: 0,
        gridStartY: 0,
        gridEndX: 6,
        gridEndY: 6,
        color: '#2c3e50',
        ambientLight: '#3498db'
      },
      {
        id: 'trading-floor',
        name: 'Trading Floor',
        type: 'trading',
        gridStartX: 14,
        gridStartY: 0,
        gridEndX: 20,
        gridEndY: 6,
        color: '#27ae60',
        ambientLight: '#2ecc71'
      },
      {
        id: 'nft-gallery',
        name: 'NFT Gallery',
        type: 'gallery',
        gridStartX: 0,
        gridStartY: 14,
        gridEndX: 6,
        gridEndY: 20,
        color: '#8e44ad',
        ambientLight: '#9b59b6'
      },
      {
        id: 'conference-room',
        name: 'Conference Room',
        type: 'conference',
        gridStartX: 14,
        gridStartY: 14,
        gridEndX: 20,
        gridEndY: 20,
        color: '#c0392b',
        ambientLight: '#e74c3c'
      },
      {
        id: 'central-lounge',
        name: 'Central Lounge',
        type: 'lounge',
        gridStartX: 7,
        gridStartY: 7,
        gridEndX: 13,
        gridEndY: 13,
        color: '#34495e',
        ambientLight: '#95a5a6'
      }
    ];
  }

  /**
   * Create agents
   */
  private createAgents(): void {
    const userAgents = this.multiAgentService.getUserAgents();
    
    userAgents.forEach((ua: UserAgent, index: number) => {
      const startPositions = [
        { x: 3, y: 3 },   // Tech lab
        { x: 17, y: 3 },  // Trading floor
        { x: 10, y: 10 }  // Central lounge
      ];
      
      const pos = startPositions[index % startPositions.length];
      const screen = this.isometric.gridToScreen(pos.x, pos.y, 0);
      
      const worldAgent: WorldAgent = {
        id: ua.id,
        name: ua.name,
        personality: ua.personality,
        emoji: ua.emoji,
        color: ua.color,
        gridX: pos.x,
        gridY: pos.y,
        targetX: pos.x,
        targetY: pos.y,
        screenX: screen.x,
        screenY: screen.y,
        z: 0,
        activity: 'idle',
        speech: null,
        speechTimer: 0,
        animationFrame: 0,
        animationTimer: 0,
        mood: 'neutral',
        path: null,
        pathIndex: 0,
        moveSpeed: 2
      };
      
      this.agents.set(ua.id, worldAgent);
      this.tileOccupancy[pos.x][pos.y] = true;
    });
  }

  /**
   * Create world objects
   */
  private createWorldObjects(): void {
    // Trading terminals in trading floor
    this.addObject({
      id: 'terminal-1',
      type: 'terminal',
      gridX: 15,
      gridY: 2,
      width: 2,
      height: 2,
      interactive: true,
      active: true
    });

    this.addObject({
      id: 'terminal-2',
      type: 'terminal',
      gridX: 18,
      gridY: 2,
      width: 2,
      height: 2,
      interactive: true,
      active: true
    });

    // Conference table
    this.addObject({
      id: 'conference-table',
      type: 'table',
      gridX: 16,
      gridY: 16,
      width: 3,
      height: 3,
      interactive: false,
      active: false
    });

    // NFT displays
    this.addObject({
      id: 'nft-display-1',
      type: 'display',
      gridX: 2,
      gridY: 15,
      width: 1,
      height: 2,
      interactive: true,
      active: true
    });

    this.addObject({
      id: 'nft-display-2',
      type: 'display',
      gridX: 2,
      gridY: 18,
      width: 1,
      height: 2,
      interactive: true,
      active: true
    });

    // Vending machines
    this.addObject({
      id: 'crypto-vending',
      type: 'vending',
      gridX: 10,
      gridY: 7,
      width: 1,
      height: 2,
      interactive: true,
      active: true
    });
  }

  /**
   * Add object to world
   */
  private addObject(obj: WorldObject): void {
    this.objects.set(obj.id, obj);
    
    // Mark tiles as occupied
    for (let x = obj.gridX; x < obj.gridX + obj.width; x++) {
      for (let y = obj.gridY; y < obj.gridY + obj.height; y++) {
        if (x < this.gridWidth && y < this.gridHeight) {
          this.tileOccupancy[x][y] = true;
        }
      }
    }
  }

  /**
   * Connect to multi-agent hub
   */
  private connectToHub(): void {
    this.multiAgentService.connect();
    
    // Listen for discussions
    this.multiAgentService.on('discussion', (discussion: StrategyDiscussion) => {
      this.handleDiscussion(discussion);
    });
    
    // Listen for consensus
    this.multiAgentService.on('consensus', (consensus: ConsensusResponse) => {
      this.handleConsensus(consensus);
    });
  }

  /**
   * Handle agent discussion
   */
  private handleDiscussion(discussion: StrategyDiscussion): void {
    const agent = Array.from(this.agents.values()).find(
      a => a.name === discussion.agentName
    );
    
    if (agent) {
      agent.speech = discussion.message;
      agent.speechTimer = 300; // 5 seconds at 60fps
      agent.activity = 'talking';
      agent.mood = this.getMoodFromRiskAssessment(discussion.riskAssessment);
      
      // Move to conference room for discussion
      this.moveAgentToZone(agent, 'conference');
      
      // Create particles based on mood
      this.createMoodParticles(agent);
    }
  }

  /**
   * Handle consensus
   */
  private handleConsensus(consensus: ConsensusResponse): void {
    // Make all agents celebrate or show concern based on consensus
    this.agents.forEach(agent => {
      if (consensus.consensusReached) {
        agent.mood = 'excited';
        agent.speech = "Consensus reached! 🎉";
        this.createCelebrationParticles(agent);
      } else {
        agent.mood = 'concerned';
        agent.speech = "We need more discussion...";
      }
      agent.speechTimer = 180;
    });
  }

  /**
   * Get mood from risk assessment
   */
  private getMoodFromRiskAssessment(risk: string): WorldAgent['mood'] {
    const moods: Record<string, WorldAgent['mood']> = {
      'low': 'happy',
      'medium': 'neutral',
      'calculated': 'thinking',
      'high': 'excited',
      'yolo': 'excited'
    };
    return moods[risk] || 'neutral';
  }

  /**
   * Move agent to zone
   */
  moveAgentToZone(agent: WorldAgent, zoneType: Zone['type']): void {
    const zone = this.zones.find(z => z.type === zoneType);
    if (!zone) return;
    
    // Find random unoccupied tile in zone
    const targetX = zone.gridStartX + Math.floor(
      Math.random() * (zone.gridEndX - zone.gridStartX)
    );
    const targetY = zone.gridStartY + Math.floor(
      Math.random() * (zone.gridEndY - zone.gridStartY)
    );
    
    this.moveAgentTo(agent, targetX, targetY);
  }

  /**
   * Move agent to specific tile
   */
  moveAgentTo(agent: WorldAgent, targetX: number, targetY: number): void {
    if (!this.isTileWalkable(targetX, targetY)) {
      // Find nearest walkable tile
      const nearestWalkable = this.findNearestWalkableTile(targetX, targetY);
      if (nearestWalkable) {
        targetX = nearestWalkable.x;
        targetY = nearestWalkable.y;
      } else {
        return;
      }
    }
    
    // Calculate path
    const path = this.isometric.findPath(
      { x: agent.gridX, y: agent.gridY },
      { x: targetX, y: targetY },
      (x, y) => this.isTileWalkable(x, y)
    );
    
    if (path && path.length > 1) {
      agent.path = path;
      agent.pathIndex = 0;
      agent.targetX = targetX;
      agent.targetY = targetY;
      agent.activity = 'walking';
    }
  }

  /**
   * Check if tile is walkable
   */
  isTileWalkable(x: number, y: number): boolean {
    if (x < 0 || x >= this.gridWidth || y < 0 || y >= this.gridHeight) {
      return false;
    }
    return !this.tileOccupancy[x][y];
  }

  /**
   * Find nearest walkable tile
   */
  private findNearestWalkableTile(x: number, y: number): Point2D | null {
    const maxRadius = 5;
    
    for (let radius = 1; radius <= maxRadius; radius++) {
      for (let dx = -radius; dx <= radius; dx++) {
        for (let dy = -radius; dy <= radius; dy++) {
          const checkX = x + dx;
          const checkY = y + dy;
          
          if (this.isTileWalkable(checkX, checkY)) {
            return { x: checkX, y: checkY };
          }
        }
      }
    }
    
    return null;
  }

  /**
   * Update world state
   */
  update(deltaTime: number): void {
    this.worldTime += deltaTime;
    this.dayNightCycle = (this.worldTime / 60000) % 1; // 1 minute day/night cycle
    
    // Update agents
    this.agents.forEach(agent => {
      this.updateAgent(agent, deltaTime);
    });
    
    // Update particles
    this.particles = this.particles.filter(particle => {
      spriteManager.updateParticle(particle, deltaTime);
      return particle.life > 0;
    });
    
    // Random agent activities
    if (Math.random() < 0.005) {
      this.triggerRandomActivity();
    }
  }

  /**
   * Update agent
   */
  private updateAgent(agent: WorldAgent, deltaTime: number): void {
    // Update animation
    agent.animationTimer += deltaTime;
    if (agent.animationTimer > 150) {
      agent.animationTimer = 0;
      agent.animationFrame = (agent.animationFrame + 1) % 4;
    }
    
    // Update speech timer
    if (agent.speechTimer > 0) {
      agent.speechTimer -= deltaTime / 16.67;
      if (agent.speechTimer <= 0) {
        agent.speech = null;
        agent.activity = 'idle';
      }
    }
    
    // Update movement
    if (agent.path && agent.pathIndex < agent.path.length) {
      const target = agent.path[agent.pathIndex];
      const dx = target.x - agent.gridX;
      const dy = target.y - agent.gridY;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 0.1) {
        // Update tile occupancy
        this.tileOccupancy[agent.gridX][agent.gridY] = false;
        agent.gridX = target.x;
        agent.gridY = target.y;
        this.tileOccupancy[agent.gridX][agent.gridY] = true;
        
        agent.pathIndex++;
        
        if (agent.pathIndex >= agent.path.length) {
          agent.path = null;
          agent.activity = 'idle';
        }
      } else {
        // Move towards target
        const moveDistance = agent.moveSpeed * deltaTime / 1000;
        agent.gridX += (dx / distance) * moveDistance;
        agent.gridY += (dy / distance) * moveDistance;
      }
      
      // Update screen position
      const screen = this.isometric.gridToScreen(agent.gridX, agent.gridY, agent.z);
      agent.screenX = screen.x;
      agent.screenY = screen.y;
    }
  }

  /**
   * Trigger random activity
   */
  private triggerRandomActivity(): void {
    const agents = Array.from(this.agents.values());
    if (agents.length === 0) return;
    
    const agent = agents[Math.floor(Math.random() * agents.length)];
    const activities = [
      () => {
        agent.speech = "Analyzing market data...";
        agent.speechTimer = 120;
        agent.activity = 'analyzing';
        this.moveAgentToZone(agent, 'trading');
      },
      () => {
        agent.speech = "Checking NFT collections...";
        agent.speechTimer = 120;
        agent.activity = 'thinking';
        this.moveAgentToZone(agent, 'gallery');
      },
      () => {
        agent.speech = "Time for a strategy meeting!";
        agent.speechTimer = 120;
        agent.activity = 'talking';
        this.moveAgentToZone(agent, 'conference');
      },
      () => {
        agent.speech = "Building something cool...";
        agent.speechTimer = 120;
        agent.activity = 'thinking';
        this.moveAgentToZone(agent, 'tech');
      }
    ];
    
    const activity = activities[Math.floor(Math.random() * activities.length)];
    activity();
  }

  /**
   * Create mood particles
   */
  private createMoodParticles(agent: WorldAgent): void {
    const types: Record<string, 'heart' | 'sparkle' | 'data' | 'coin'> = {
      'happy': 'heart',
      'excited': 'sparkle',
      'thinking': 'data',
      'neutral': 'sparkle',
      'concerned': 'smoke' as any
    };
    
    const type = types[agent.mood] || 'sparkle';
    const particles = spriteManager.createParticleEffect(
      agent.screenX,
      agent.screenY - 30,
      type,
      5
    );
    
    this.particles.push(...particles);
  }

  /**
   * Create celebration particles
   */
  private createCelebrationParticles(agent: WorldAgent): void {
    const particles = spriteManager.createParticleEffect(
      agent.screenX,
      agent.screenY - 30,
      'sparkle',
      15
    );
    
    this.particles.push(...particles);
  }

  /**
   * Handle click on world
   */
  handleClick(screenX: number, screenY: number): void {
    const gridPos = this.isometric.screenToGrid(screenX, screenY);
    
    // Check if clicking on an agent
    let clickedAgent: WorldAgent | null = null;
    this.agents.forEach(agent => {
      if (Math.floor(agent.gridX) === gridPos.x && 
          Math.floor(agent.gridY) === gridPos.y) {
        clickedAgent = agent;
      }
    });
    
    if (clickedAgent) {
      this.selectAgent(clickedAgent);
    } else if (this.selectedAgent) {
      // Move selected agent to clicked position
      this.moveAgentTo(this.selectedAgent, gridPos.x, gridPos.y);
    }
  }

  /**
   * Select agent
   */
  selectAgent(agent: WorldAgent): void {
    this.selectedAgent = agent;
    agent.speech = `Hi! I'm ${agent.name}!`;
    agent.speechTimer = 120;
    
    // Create selection particles
    const particles = spriteManager.createParticleEffect(
      agent.screenX,
      agent.screenY,
      'sparkle',
      8
    );
    this.particles.push(...particles);
  }

  /**
   * Broadcast query to agents
   */
  async broadcastQuery(query: string): Promise<void> {
    // Move all agents to conference room
    this.agents.forEach(agent => {
      this.moveAgentToZone(agent, 'conference');
      agent.activity = 'thinking';
    });
    
    // Send query to multi-agent service
    await this.multiAgentService.broadcastQuery(query);
  }

  // Getters
  getAgents(): WorldAgent[] {
    return Array.from(this.agents.values());
  }

  getObjects(): WorldObject[] {
    return Array.from(this.objects.values());
  }

  getZones(): Zone[] {
    return this.zones;
  }

  getParticles(): Particle[] {
    return this.particles;
  }

  getSelectedAgent(): WorldAgent | null {
    return this.selectedAgent;
  }

  getDayNightCycle(): number {
    return this.dayNightCycle;
  }

  getIsometric(): IsometricUtils {
    return this.isometric;
  }
}

export default EtheriusWorldService;