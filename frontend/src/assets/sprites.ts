/**
 * Sprite management system for EtheriusVerse
 * Handles loading, caching, and animation of sprites
 */

export interface Sprite {
  id: string;
  src: string;
  width: number;
  height: number;
  frames?: number;
  frameWidth?: number;
  frameHeight?: number;
  loaded: boolean;
  image?: HTMLImageElement;
}

export interface AnimationFrame {
  x: number;
  y: number;
  width: number;
  height: number;
  duration: number;
}

export interface Animation {
  id: string;
  spriteId: string;
  frames: AnimationFrame[];
  loop: boolean;
  currentFrame: number;
  elapsedTime: number;
}

export class SpriteManager {
  private sprites: Map<string, Sprite> = new Map();
  private animations: Map<string, Animation> = new Map();
  private loadingPromises: Map<string, Promise<void>> = new Map();

  constructor() {
    this.initializeSprites();
  }

  /**
   * Initialize sprite definitions
   */
  private initializeSprites(): void {
    // Agent sprites
    this.registerSprite({
      id: 'kartik',
      src: '/assets/sprites/characters/kartik_sprite.png',
      width: 256,
      height: 64,
      frames: 4,
      frameWidth: 64,
      frameHeight: 64,
      loaded: false
    });

    this.registerSprite({
      id: 'vitalik',
      src: '/assets/sprites/characters/vitalik_sprite.png',
      width: 256,
      height: 64,
      frames: 4,
      frameWidth: 64,
      frameHeight: 64,
      loaded: false
    });

    this.registerSprite({
      id: 'mik',
      src: '/assets/sprites/characters/mik_sprite.png',
      width: 256,
      height: 64,
      frames: 4,
      frameWidth: 64,
      frameHeight: 64,
      loaded: false
    });

    // Environment sprites
    this.registerSprite({
      id: 'trading_terminal',
      src: '/assets/sprites/environment/trading_terminal.png',
      width: 128,
      height: 96,
      loaded: false
    });

    this.registerSprite({
      id: 'nft_gallery',
      src: '/assets/sprites/environment/nft_gallery.png',
      width: 192,
      height: 128,
      loaded: false
    });

    this.registerSprite({
      id: 'conference_table',
      src: '/assets/sprites/environment/conference_table.png',
      width: 160,
      height: 120,
      loaded: false
    });

    this.registerSprite({
      id: 'crypto_vending',
      src: '/assets/sprites/environment/crypto_vending.png',
      width: 96,
      height: 128,
      loaded: false
    });

    // Effect sprites
    this.registerSprite({
      id: 'particles',
      src: '/assets/sprites/effects/particles.png',
      width: 256,
      height: 256,
      frames: 64,
      frameWidth: 32,
      frameHeight: 32,
      loaded: false
    });

    this.registerSprite({
      id: 'speech_bubbles',
      src: '/assets/sprites/ui/speech_bubbles.png',
      width: 256,
      height: 128,
      loaded: false
    });

    // UI sprites
    this.registerSprite({
      id: 'ui_panels',
      src: '/assets/sprites/ui/panels.png',
      width: 512,
      height: 512,
      loaded: false
    });

    this.registerSprite({
      id: 'floor_tiles',
      src: '/assets/sprites/environment/floor_tiles.png',
      width: 256,
      height: 256,
      loaded: false
    });
  }

  /**
   * Register a sprite
   */
  registerSprite(sprite: Sprite): void {
    this.sprites.set(sprite.id, sprite);
  }

  /**
   * Load a sprite
   */
  async loadSprite(id: string): Promise<void> {
    const sprite = this.sprites.get(id);
    if (!sprite) {
      throw new Error(`Sprite ${id} not found`);
    }

    if (sprite.loaded) {
      return;
    }

    // Check if already loading
    if (this.loadingPromises.has(id)) {
      return this.loadingPromises.get(id);
    }

    const loadPromise = new Promise<void>((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        sprite.image = img;
        sprite.loaded = true;
        this.loadingPromises.delete(id);
        resolve();
      };
      img.onerror = () => {
        console.error(`Failed to load sprite: ${id}`);
        this.loadingPromises.delete(id);
        // Use placeholder image
        sprite.image = this.createPlaceholderImage(sprite.width, sprite.height);
        sprite.loaded = true;
        resolve();
      };
      img.src = sprite.src;
    });

    this.loadingPromises.set(id, loadPromise);
    return loadPromise;
  }

  /**
   * Create placeholder image for missing sprites
   */
  private createPlaceholderImage(width: number, height: number): HTMLImageElement {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      // Draw checkerboard pattern
      const squareSize = 8;
      for (let x = 0; x < width; x += squareSize) {
        for (let y = 0; y < height; y += squareSize) {
          ctx.fillStyle = ((x + y) / squareSize) % 2 === 0 ? '#ff00ff' : '#00ffff';
          ctx.fillRect(x, y, squareSize, squareSize);
        }
      }
      
      // Add "PLACEHOLDER" text
      ctx.fillStyle = '#000';
      ctx.font = '12px monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('PLACEHOLDER', width / 2, height / 2);
    }
    
    const img = new Image();
    img.src = canvas.toDataURL();
    return img;
  }

  /**
   * Load all sprites
   */
  async loadAllSprites(): Promise<void> {
    const loadPromises = Array.from(this.sprites.keys()).map(id => 
      this.loadSprite(id)
    );
    await Promise.all(loadPromises);
  }

  /**
   * Get sprite
   */
  getSprite(id: string): Sprite | undefined {
    return this.sprites.get(id);
  }

  /**
   * Draw sprite
   */
  drawSprite(
    ctx: CanvasRenderingContext2D,
    spriteId: string,
    x: number,
    y: number,
    frame: number = 0,
    scale: number = 1
  ): void {
    const sprite = this.sprites.get(spriteId);
    if (!sprite || !sprite.loaded || !sprite.image) {
      return;
    }

    if (sprite.frames && sprite.frameWidth && sprite.frameHeight) {
      // Draw animated sprite frame
      const frameX = (frame % (sprite.width / sprite.frameWidth)) * sprite.frameWidth;
      const frameY = Math.floor(frame / (sprite.width / sprite.frameWidth)) * sprite.frameHeight;
      
      ctx.drawImage(
        sprite.image,
        frameX, frameY,
        sprite.frameWidth, sprite.frameHeight,
        x - (sprite.frameWidth * scale) / 2,
        y - (sprite.frameHeight * scale),
        sprite.frameWidth * scale,
        sprite.frameHeight * scale
      );
    } else {
      // Draw static sprite
      ctx.drawImage(
        sprite.image,
        x - (sprite.width * scale) / 2,
        y - (sprite.height * scale),
        sprite.width * scale,
        sprite.height * scale
      );
    }
  }

  /**
   * Create animation
   */
  createAnimation(
    id: string,
    spriteId: string,
    frameIndices: number[],
    frameDuration: number = 100,
    loop: boolean = true
  ): Animation {
    const sprite = this.sprites.get(spriteId);
    if (!sprite || !sprite.frameWidth || !sprite.frameHeight) {
      throw new Error(`Cannot create animation from sprite ${spriteId}`);
    }

    const frames: AnimationFrame[] = frameIndices.map(index => ({
      x: (index % (sprite.width / sprite.frameWidth!)) * sprite.frameWidth!,
      y: Math.floor(index / (sprite.width / sprite.frameWidth!)) * sprite.frameHeight!,
      width: sprite.frameWidth!,
      height: sprite.frameHeight!,
      duration: frameDuration
    }));

    const animation: Animation = {
      id,
      spriteId,
      frames,
      loop,
      currentFrame: 0,
      elapsedTime: 0
    };

    this.animations.set(id, animation);
    return animation;
  }

  /**
   * Update animation
   */
  updateAnimation(animationId: string, deltaTime: number): void {
    const animation = this.animations.get(animationId);
    if (!animation) return;

    animation.elapsedTime += deltaTime;
    const currentFrameDuration = animation.frames[animation.currentFrame].duration;

    if (animation.elapsedTime >= currentFrameDuration) {
      animation.elapsedTime = 0;
      animation.currentFrame++;

      if (animation.currentFrame >= animation.frames.length) {
        if (animation.loop) {
          animation.currentFrame = 0;
        } else {
          animation.currentFrame = animation.frames.length - 1;
        }
      }
    }
  }

  /**
   * Draw animation
   */
  drawAnimation(
    ctx: CanvasRenderingContext2D,
    animationId: string,
    x: number,
    y: number,
    scale: number = 1
  ): void {
    const animation = this.animations.get(animationId);
    if (!animation) return;

    const sprite = this.sprites.get(animation.spriteId);
    if (!sprite || !sprite.loaded || !sprite.image) return;

    const frame = animation.frames[animation.currentFrame];
    
    ctx.drawImage(
      sprite.image,
      frame.x, frame.y,
      frame.width, frame.height,
      x - (frame.width * scale) / 2,
      y - (frame.height * scale),
      frame.width * scale,
      frame.height * scale
    );
  }

  /**
   * Create particle effect
   */
  createParticleEffect(
    x: number,
    y: number,
    type: 'sparkle' | 'coin' | 'data' | 'smoke' | 'heart',
    count: number = 10
  ): Particle[] {
    const particles: Particle[] = [];
    const typeConfig = this.getParticleConfig(type);

    for (let i = 0; i < count; i++) {
      particles.push({
        x,
        y,
        vx: (Math.random() - 0.5) * typeConfig.speed,
        vy: -Math.random() * typeConfig.speed - 1,
        life: 1,
        decay: typeConfig.decay,
        size: typeConfig.size,
        color: typeConfig.color,
        type
      });
    }

    return particles;
  }

  /**
   * Get particle configuration
   */
  private getParticleConfig(type: string): any {
    const configs: any = {
      sparkle: { speed: 4, decay: 0.02, size: 4, color: '#ffff00' },
      coin: { speed: 3, decay: 0.015, size: 8, color: '#ffd700' },
      data: { speed: 2, decay: 0.01, size: 3, color: '#00ff00' },
      smoke: { speed: 1, decay: 0.02, size: 6, color: '#888888' },
      heart: { speed: 2, decay: 0.015, size: 10, color: '#ff69b4' }
    };
    return configs[type] || configs.sparkle;
  }

  /**
   * Update particle
   */
  updateParticle(particle: Particle, deltaTime: number): void {
    particle.x += particle.vx * deltaTime / 16;
    particle.y += particle.vy * deltaTime / 16;
    particle.vy += 0.2; // Gravity
    particle.life -= particle.decay;
  }

  /**
   * Draw particle
   */
  drawParticle(ctx: CanvasRenderingContext2D, particle: Particle): void {
    if (particle.life <= 0) return;

    ctx.save();
    ctx.globalAlpha = particle.life;
    ctx.fillStyle = particle.color;
    
    if (particle.type === 'heart') {
      // Draw heart shape
      const size = particle.size * particle.life;
      ctx.beginPath();
      ctx.moveTo(particle.x, particle.y + size / 4);
      ctx.quadraticCurveTo(particle.x - size / 2, particle.y - size / 2, particle.x, particle.y);
      ctx.quadraticCurveTo(particle.x + size / 2, particle.y - size / 2, particle.x, particle.y + size / 4);
      ctx.fill();
    } else {
      // Draw circle
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.size * particle.life, 0, Math.PI * 2);
      ctx.fill();
    }
    
    ctx.restore();
  }
}

export interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  decay: number;
  size: number;
  color: string;
  type: string;
}

// Create singleton instance
export const spriteManager = new SpriteManager();
export default spriteManager;