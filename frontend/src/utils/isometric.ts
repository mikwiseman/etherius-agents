/**
 * Isometric utilities for EtheriusVerse
 * Handles coordinate conversion, depth sorting, and grid management
 */

export interface Point2D {
  x: number;
  y: number;
}

export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export interface IsometricTile {
  gridX: number;
  gridY: number;
  screenX: number;
  screenY: number;
  depth: number;
  occupied: boolean;
  zoneType?: 'tech' | 'trading' | 'gallery' | 'conference' | 'lounge';
}

export class IsometricUtils {
  private tileWidth: number;
  private tileHeight: number;
  private originX: number;
  private originY: number;

  constructor(
    tileWidth: number = 64,
    tileHeight: number = 32,
    originX: number = 450,
    originY: number = 100
  ) {
    this.tileWidth = tileWidth;
    this.tileHeight = tileHeight;
    this.originX = originX;
    this.originY = originY;
  }

  /**
   * Convert grid coordinates to screen coordinates
   */
  gridToScreen(gridX: number, gridY: number, z: number = 0): Point2D {
    const screenX = this.originX + (gridX - gridY) * (this.tileWidth / 2);
    const screenY = this.originY + (gridX + gridY) * (this.tileHeight / 2) - z;
    return { x: screenX, y: screenY };
  }

  /**
   * Convert screen coordinates to grid coordinates
   */
  screenToGrid(screenX: number, screenY: number): Point2D {
    const adjustedX = screenX - this.originX;
    const adjustedY = screenY - this.originY;
    
    const gridX = (adjustedX / (this.tileWidth / 2) + adjustedY / (this.tileHeight / 2)) / 2;
    const gridY = (adjustedY / (this.tileHeight / 2) - adjustedX / (this.tileWidth / 2)) / 2;
    
    return {
      x: Math.floor(gridX),
      y: Math.floor(gridY)
    };
  }

  /**
   * Calculate depth for proper rendering order
   */
  calculateDepth(gridX: number, gridY: number, z: number = 0): number {
    return (gridX + gridY) * 1000 + z;
  }

  /**
   * Check if a point is within a tile
   */
  isPointInTile(point: Point2D, tileGridPos: Point2D): boolean {
    const tileScreen = this.gridToScreen(tileGridPos.x, tileGridPos.y);
    
    // Create diamond shape points
    const points = [
      { x: tileScreen.x, y: tileScreen.y },
      { x: tileScreen.x + this.tileWidth / 2, y: tileScreen.y + this.tileHeight / 2 },
      { x: tileScreen.x, y: tileScreen.y + this.tileHeight },
      { x: tileScreen.x - this.tileWidth / 2, y: tileScreen.y + this.tileHeight / 2 }
    ];
    
    return this.pointInPolygon(point, points);
  }

  /**
   * Check if point is inside polygon
   */
  private pointInPolygon(point: Point2D, polygon: Point2D[]): boolean {
    let inside = false;
    
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const xi = polygon[i].x;
      const yi = polygon[i].y;
      const xj = polygon[j].x;
      const yj = polygon[j].y;
      
      const intersect = ((yi > point.y) !== (yj > point.y))
        && (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi);
      
      if (intersect) inside = !inside;
    }
    
    return inside;
  }

  /**
   * Get neighboring tiles
   */
  getNeighbors(gridX: number, gridY: number): Point2D[] {
    return [
      { x: gridX - 1, y: gridY },     // Left
      { x: gridX + 1, y: gridY },     // Right
      { x: gridX, y: gridY - 1 },     // Up
      { x: gridX, y: gridY + 1 },     // Down
      { x: gridX - 1, y: gridY - 1 }, // Up-Left
      { x: gridX + 1, y: gridY - 1 }, // Up-Right
      { x: gridX - 1, y: gridY + 1 }, // Down-Left
      { x: gridX + 1, y: gridY + 1 }  // Down-Right
    ];
  }

  /**
   * Calculate distance between two grid points
   */
  gridDistance(p1: Point2D, p2: Point2D): number {
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * A* pathfinding algorithm
   */
  findPath(
    start: Point2D,
    end: Point2D,
    isWalkable: (x: number, y: number) => boolean,
    maxDistance: number = 50
  ): Point2D[] | null {
    const openSet: Set<string> = new Set([`${start.x},${start.y}`]);
    const cameFrom: Map<string, string> = new Map();
    const gScore: Map<string, number> = new Map();
    const fScore: Map<string, number> = new Map();
    
    const key = (p: Point2D) => `${p.x},${p.y}`;
    const parseKey = (k: string): Point2D => {
      const [x, y] = k.split(',').map(Number);
      return { x, y };
    };
    
    gScore.set(key(start), 0);
    fScore.set(key(start), this.gridDistance(start, end));
    
    while (openSet.size > 0) {
      // Find node with lowest fScore
      let current: string = '';
      let lowestF = Infinity;
      
      openSet.forEach(node => {
        const f = fScore.get(node) || Infinity;
        if (f < lowestF) {
          lowestF = f;
          current = node;
        }
      });
      
      if (!current) break;
      
      const currentPoint = parseKey(current);
      
      // Check if we reached the goal
      if (currentPoint.x === end.x && currentPoint.y === end.y) {
        // Reconstruct path
        const path: Point2D[] = [];
        let curr = current;
        
        while (curr) {
          path.unshift(parseKey(curr));
          curr = cameFrom.get(curr) || '';
          if (curr === '') break;
        }
        
        return path;
      }
      
      openSet.delete(current);
      
      // Check neighbors
      const neighbors = this.getNeighbors(currentPoint.x, currentPoint.y);
      
      for (const neighbor of neighbors) {
        if (!isWalkable(neighbor.x, neighbor.y)) continue;
        
        const neighborKey = key(neighbor);
        const tentativeGScore = (gScore.get(current) || 0) + 
          this.gridDistance(currentPoint, neighbor);
        
        if (tentativeGScore < (gScore.get(neighborKey) || Infinity)) {
          cameFrom.set(neighborKey, current);
          gScore.set(neighborKey, tentativeGScore);
          fScore.set(neighborKey, tentativeGScore + this.gridDistance(neighbor, end));
          openSet.add(neighborKey);
        }
      }
      
      // Limit search distance
      if ((gScore.get(current) || 0) > maxDistance) {
        break;
      }
    }
    
    return null; // No path found
  }

  /**
   * Draw isometric tile
   */
  drawTile(
    ctx: CanvasRenderingContext2D,
    gridX: number,
    gridY: number,
    color: string,
    strokeColor: string = 'rgba(255, 255, 255, 0.1)'
  ): void {
    const screen = this.gridToScreen(gridX, gridY);
    
    ctx.beginPath();
    ctx.moveTo(screen.x, screen.y);
    ctx.lineTo(screen.x + this.tileWidth / 2, screen.y + this.tileHeight / 2);
    ctx.lineTo(screen.x, screen.y + this.tileHeight);
    ctx.lineTo(screen.x - this.tileWidth / 2, screen.y + this.tileHeight / 2);
    ctx.closePath();
    
    ctx.fillStyle = color;
    ctx.fill();
    
    if (strokeColor) {
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  }

  /**
   * Draw isometric cube/box
   */
  drawCube(
    ctx: CanvasRenderingContext2D,
    gridX: number,
    gridY: number,
    width: number,
    height: number,
    depth: number,
    colors: { top: string; left: string; right: string }
  ): void {
    const base = this.gridToScreen(gridX, gridY, 0);
    
    // Top face
    ctx.fillStyle = colors.top;
    ctx.beginPath();
    ctx.moveTo(base.x, base.y - depth);
    ctx.lineTo(base.x + width / 2, base.y - depth + height / 2);
    ctx.lineTo(base.x, base.y - depth + height);
    ctx.lineTo(base.x - width / 2, base.y - depth + height / 2);
    ctx.closePath();
    ctx.fill();
    
    // Left face
    ctx.fillStyle = colors.left;
    ctx.beginPath();
    ctx.moveTo(base.x - width / 2, base.y - depth + height / 2);
    ctx.lineTo(base.x - width / 2, base.y + height / 2);
    ctx.lineTo(base.x, base.y + height);
    ctx.lineTo(base.x, base.y - depth + height);
    ctx.closePath();
    ctx.fill();
    
    // Right face
    ctx.fillStyle = colors.right;
    ctx.beginPath();
    ctx.moveTo(base.x, base.y - depth + height);
    ctx.lineTo(base.x, base.y + height);
    ctx.lineTo(base.x + width / 2, base.y + height / 2);
    ctx.lineTo(base.x + width / 2, base.y - depth + height / 2);
    ctx.closePath();
    ctx.fill();
  }

  /**
   * Sort objects by depth for proper rendering order
   */
  sortByDepth<T extends { gridX: number; gridY: number; z?: number }>(
    objects: T[]
  ): T[] {
    return objects.sort((a, b) => {
      const depthA = this.calculateDepth(a.gridX, a.gridY, a.z || 0);
      const depthB = this.calculateDepth(b.gridX, b.gridY, b.z || 0);
      return depthA - depthB;
    });
  }

  /**
   * Create room zones
   */
  createRoomZones(gridWidth: number, gridHeight: number): IsometricTile[][] {
    const tiles: IsometricTile[][] = [];
    
    for (let x = 0; x < gridWidth; x++) {
      tiles[x] = [];
      for (let y = 0; y < gridHeight; y++) {
        const screen = this.gridToScreen(x, y);
        
        // Determine zone type based on position
        let zoneType: IsometricTile['zoneType'] = 'lounge';
        
        if (x < gridWidth / 3 && y < gridHeight / 3) {
          zoneType = 'tech';
        } else if (x >= gridWidth * 2/3 && y < gridHeight / 3) {
          zoneType = 'trading';
        } else if (x < gridWidth / 3 && y >= gridHeight * 2/3) {
          zoneType = 'gallery';
        } else if (x >= gridWidth * 2/3 && y >= gridHeight * 2/3) {
          zoneType = 'conference';
        }
        
        tiles[x][y] = {
          gridX: x,
          gridY: y,
          screenX: screen.x,
          screenY: screen.y,
          depth: this.calculateDepth(x, y),
          occupied: false,
          zoneType
        };
      }
    }
    
    return tiles;
  }

  /**
   * Get zone color based on type
   */
  getZoneColor(zoneType: IsometricTile['zoneType']): string {
    const colors = {
      tech: '#2c3e50',      // Dark blue-gray
      trading: '#27ae60',   // Green
      gallery: '#8e44ad',   // Purple
      conference: '#c0392b', // Red
      lounge: '#34495e'     // Default gray
    };
    
    return colors[zoneType || 'lounge'];
  }

  /**
   * Smooth movement interpolation
   */
  lerp(start: number, end: number, t: number): number {
    return start + (end - start) * t;
  }

  /**
   * Easing function for smooth animations
   */
  easeInOutQuad(t: number): number {
    return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
  }
}

export default IsometricUtils;