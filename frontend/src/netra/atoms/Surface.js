/**
 * 🏔️ SURFACE ATOM
 * ================
 * 
 * Ground/boundary surface with friction and texture.
 */

import { Atom } from './Atom';

export class Surface extends Atom {
  static get type() {
    return 'Surface';
  }

  getDefaultParams() {
    return {
      width: 800,
      height: 100,
      friction: 0.5,
      texture: 'rough',      // rough, smooth, ice, carpet
      fill: '#8B7355',
      stroke: '#6B5344',
      strokeWidth: 2,
      showFrictionIndicator: false,
      label: null
    };
  }

  getInitialState() {
    return {
      objectsOnSurface: []
    };
  }

  static getParamSchema() {
    return {
      width: { type: 'number', min: 100, max: 1200, default: 800 },
      height: { type: 'number', min: 20, max: 300, default: 100 },
      friction: { type: 'number', min: 0, max: 1, default: 0.5 },
      texture: { type: 'string', default: 'rough' },
      fill: { type: 'string', default: '#8B7355' }
    };
  }

  onMount(scene) {
    super.onMount(scene);
    this.size = {
      width: this.params.width,
      height: this.params.height
    };

    // Create static physics body
    if (scene.physicsWorld) {
      this.createPhysicsBody(scene.physicsWorld);
    }
  }

  createPhysicsBody(world) {
    if (typeof window === 'undefined') return;
    
    const Matter = window.Matter;
    if (!Matter) return;

    const { width, height, friction } = this.params;
    const pos = this.getComputedPosition();

    this.body = Matter.Bodies.rectangle(
      pos.x,
      pos.y + height / 2,
      width,
      height,
      {
        isStatic: true,
        friction,
        label: this.id
      }
    );

    Matter.World.add(world, this.body);
  }

  render(renderer) {
    if (!this.visible) return;

    const pos = this.getComputedPosition();
    const { width, height, fill, stroke, strokeWidth, texture, friction, showFrictionIndicator, label } = this.params;

    renderer.push();
    renderer.translate(pos.x, pos.y);

    // Draw surface base
    renderer.fill(fill, this.opacity);
    renderer.stroke(stroke);
    renderer.strokeWeight(strokeWidth);
    renderer.rect(-width / 2, 0, width, height);

    // Draw texture
    this.drawTexture(renderer, width, height, texture);

    // Friction indicator
    if (showFrictionIndicator) {
      this.drawFrictionIndicator(renderer, width, friction);
    }

    // Label
    if (label) {
      renderer.noStroke();
      renderer.fill('#FFFFFF', this.opacity * 0.9);
      renderer.textAlign('center', 'center');
      renderer.textSize(12);
      renderer.text(label, 0, height / 2);
    }

    renderer.pop();
  }

  drawTexture(renderer, width, height, texture) {
    renderer.noStroke();

    switch (texture) {
      case 'rough':
        // Draw bumps
        renderer.fill(0, 0, 0, 20 * this.opacity);
        for (let x = -width / 2 + 10; x < width / 2; x += 20) {
          const bumpHeight = 3 + Math.random() * 4;
          renderer.ellipse(x, -bumpHeight / 2, 8, bumpHeight);
        }
        break;

      case 'smooth':
        // Gradient highlight
        renderer.fill(255, 255, 255, 15 * this.opacity);
        renderer.rect(-width / 2, 0, width, 3);
        break;

      case 'ice':
        // Ice shine
        renderer.fill(200, 230, 255, 30 * this.opacity);
        renderer.rect(-width / 2, 0, width, height);
        renderer.fill(255, 255, 255, 40 * this.opacity);
        for (let x = -width / 2 + 30; x < width / 2; x += 60) {
          renderer.ellipse(x, height / 3, 20, 5);
        }
        break;

      case 'carpet':
        // Carpet fibers
        renderer.stroke(0, 0, 0, 30 * this.opacity);
        renderer.strokeWeight(1);
        for (let x = -width / 2 + 5; x < width / 2; x += 8) {
          renderer.line(x, 0, x + 2, -4);
        }
        renderer.noStroke();
        break;
    }
  }

  drawFrictionIndicator(renderer, width, friction) {
    const barWidth = 60;
    const barHeight = 8;
    const x = width / 2 - barWidth - 10;
    const y = -15;

    // Background
    renderer.fill(200, 200, 200, this.opacity);
    renderer.noStroke();
    renderer.rect(x, y, barWidth, barHeight, 4);

    // Fill based on friction
    const fillColor = friction < 0.3 ? '#3498DB' : friction < 0.7 ? '#F39C12' : '#E74C3C';
    renderer.fill(fillColor, this.opacity);
    renderer.rect(x, y, barWidth * friction, barHeight, 4);

    // Label
    renderer.fill('#333', this.opacity);
    renderer.textSize(10);
    renderer.textAlign('left', 'center');
    renderer.text(`μ=${friction.toFixed(2)}`, x, y - 10);
  }

  setFriction(value) {
    this.params.friction = Math.max(0, Math.min(1, value));
    
    if (this.body && typeof window !== 'undefined' && window.Matter) {
      this.body.friction = this.params.friction;
    }
    
    this.emit('friction_changed', this.params.friction);
  }

  onUnmount() {
    if (this.body && this.scene?.physicsWorld && typeof window !== 'undefined' && window.Matter) {
      const Matter = window.Matter;
      Matter.World.remove(this.scene.physicsWorld, this.body);
    }
    super.onUnmount();
  }
}

export default Surface;
