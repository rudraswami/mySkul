/**
 * 🎱 RIGIDBODY ATOM
 * =================
 * 
 * Physics-enabled body with mass, velocity, forces.
 * Integrates with Matter.js physics engine.
 */

import { Atom } from './Atom';

export class RigidBody extends Atom {
  static get type() {
    return 'RigidBody';
  }

  getDefaultParams() {
    return {
      shape: 'rect',         // rect, circle
      width: 80,
      height: 50,
      radius: 25,            // For circle
      mass: 1,
      restitution: 0.3,      // Bounciness
      friction: 0.5,
      fill: '#E74C3C',
      stroke: '#C0392B',
      strokeWidth: 2,
      cornerRadius: 6,
      label: null,
      labelColor: '#FFFFFF',
      shadow: true,
      isStatic: false
    };
  }

  getInitialState() {
    return {
      velocity: { x: 0, y: 0 },
      angularVelocity: 0,
      isMoving: false,
      isSleeping: false
    };
  }

  static getParamSchema() {
    return {
      shape: { type: 'string', default: 'rect' },
      width: { type: 'number', min: 10, max: 300, default: 80 },
      height: { type: 'number', min: 10, max: 300, default: 50 },
      radius: { type: 'number', min: 5, max: 150, default: 25 },
      mass: { type: 'number', min: 0.1, max: 100, default: 1 },
      restitution: { type: 'number', min: 0, max: 1, default: 0.3 },
      friction: { type: 'number', min: 0, max: 1, default: 0.5 },
      fill: { type: 'string', default: '#E74C3C' },
      isStatic: { type: 'boolean', default: false }
    };
  }

  onMount(scene) {
    super.onMount(scene);
    
    const { shape, width, height, radius } = this.params;
    
    if (shape === 'circle') {
      this.size = { width: radius * 2, height: radius * 2 };
    } else {
      this.size = { width, height };
    }

    // Create physics body if physics engine available
    if (scene.physicsWorld) {
      this.createPhysicsBody(scene.physicsWorld);
    }
  }

  createPhysicsBody(world) {
    // Dynamically import Matter.js to avoid SSR issues
    if (typeof window === 'undefined') return;
    
    const Matter = window.Matter;
    if (!Matter) return;

    const { shape, width, height, radius, mass, restitution, friction, isStatic } = this.params;
    const pos = this.getComputedPosition();

    const options = {
      mass: isStatic ? Infinity : mass,
      restitution,
      friction,
      isStatic,
      label: this.id
    };

    if (shape === 'circle') {
      this.body = Matter.Bodies.circle(pos.x, pos.y, radius, options);
    } else {
      this.body = Matter.Bodies.rectangle(pos.x, pos.y, width, height, options);
    }

    Matter.World.add(world, this.body);
  }

  update(dt) {
    super.update(dt);

    if (this.body) {
      const velocity = this.body.velocity;
      const speed = Math.sqrt(velocity.x ** 2 + velocity.y ** 2);
      const wasMoving = this.state.isMoving;
      const isMoving = speed > 0.1;

      this.setState({
        velocity: { x: velocity.x, y: velocity.y },
        angularVelocity: this.body.angularVelocity,
        isMoving,
        isSleeping: this.body.isSleeping
      });

      // Emit movement events
      if (!wasMoving && isMoving) {
        this.emit('started_moving');
      }
      if (wasMoving && !isMoving) {
        this.emit('stopped');
      }
    }
  }

  syncToPhysicsBody() {
    if (this.body && typeof window !== 'undefined' && window.Matter) {
      const Matter = window.Matter;
      Matter.Body.setPosition(this.body, this.position);
    }
  }

  applyForce(force) {
    if (this.body && typeof window !== 'undefined' && window.Matter) {
      const Matter = window.Matter;
      Matter.Body.applyForce(this.body, this.body.position, force);
      this.emit('force_applied', force);
    }
  }

  setVelocity(velocity) {
    if (this.body && typeof window !== 'undefined' && window.Matter) {
      const Matter = window.Matter;
      Matter.Body.setVelocity(this.body, velocity);
    }
  }

  render(renderer) {
    if (!this.visible) return;

    const pos = this.body ? { x: this.body.position.x, y: this.body.position.y } : this.getComputedPosition();
    const angle = this.body ? this.body.angle : 0;
    const { shape, width, height, radius, fill, stroke, strokeWidth, cornerRadius, label, labelColor, shadow } = this.params;

    renderer.push();
    renderer.translate(pos.x, pos.y);
    renderer.rotate(angle);

    // Shadow
    if (shadow) {
      renderer.noStroke();
      renderer.fill(0, 0, 0, 25 * this.opacity);
      if (shape === 'circle') {
        renderer.ellipse(3, 3, radius * 2, radius * 2);
      } else {
        renderer.rect(-width / 2 + 3, -height / 2 + 3, width, height, cornerRadius);
      }
    }

    // Main body
    renderer.fill(fill, this.opacity);
    renderer.stroke(stroke);
    renderer.strokeWeight(strokeWidth);

    if (shape === 'circle') {
      renderer.ellipse(0, 0, radius * 2, radius * 2);
      // Direction indicator
      renderer.stroke(stroke);
      renderer.line(0, 0, radius * 0.7, 0);
    } else {
      renderer.rect(-width / 2, -height / 2, width, height, cornerRadius);
    }

    // Emphasis glow
    if (this.emphasis === 'high') {
      renderer.noFill();
      renderer.stroke('#F39C12', this.opacity * 0.5);
      renderer.strokeWeight(4);
      if (shape === 'circle') {
        renderer.ellipse(0, 0, radius * 2 + 8, radius * 2 + 8);
      } else {
        renderer.rect(-width / 2 - 4, -height / 2 - 4, width + 8, height + 8, cornerRadius + 2);
      }
    }

    // Label
    if (label) {
      renderer.noStroke();
      renderer.fill(labelColor, this.opacity);
      renderer.textAlign('center', 'center');
      renderer.textSize(14);
      renderer.text(label, 0, 0);
    }

    renderer.pop();
  }

  onInteract(type, data) {
    super.onInteract(type, data);

    if (type === 'drag') {
      if (this.body && typeof window !== 'undefined' && window.Matter) {
        const Matter = window.Matter;
        Matter.Body.setPosition(this.body, data.position);
        Matter.Body.setVelocity(this.body, { x: 0, y: 0 });
      } else {
        this.setPosition(data.position.x, data.position.y);
      }
    }

    if (type === 'push') {
      this.applyForce(data.force);
    }
  }

  onUnmount() {
    // Remove from physics world
    if (this.body && this.scene?.physicsWorld && typeof window !== 'undefined' && window.Matter) {
      const Matter = window.Matter;
      Matter.World.remove(this.scene.physicsWorld, this.body);
    }
    super.onUnmount();
  }
}

export default RigidBody;
