/**
 * ➡️ FORCEVECTOR ATOM
 * ====================
 * 
 * Animated force/velocity vector arrow.
 */

import { Atom } from './Atom';

export class ForceVector extends Atom {
  static get type() {
    return 'ForceVector';
  }

  getDefaultParams() {
    return {
      magnitude: 60,
      direction: 0,          // Angle in degrees (0 = right, 90 = down)
      color: '#E74C3C',
      strokeWidth: 3,
      headSize: 12,
      label: null,
      formula: null,         // e.g., "F = ma"
      showMagnitude: false,
      animated: false,
      pulseSpeed: 1000       // ms for pulse animation
    };
  }

  getInitialState() {
    return {
      animationPhase: 0,
      isVisible: true
    };
  }

  static getParamSchema() {
    return {
      magnitude: { type: 'number', min: 10, max: 200, default: 60 },
      direction: { type: 'number', min: -180, max: 180, default: 0 },
      color: { type: 'string', default: '#E74C3C' },
      strokeWidth: { type: 'number', min: 1, max: 8, default: 3 },
      headSize: { type: 'number', min: 5, max: 25, default: 12 },
      label: { type: 'string' },
      formula: { type: 'string' },
      animated: { type: 'boolean', default: false }
    };
  }

  onMount(scene) {
    super.onMount(scene);
    this.size = { width: this.params.magnitude, height: 20 };
  }

  update(dt) {
    super.update(dt);

    if (this.params.animated) {
      const phase = (this.state.animationPhase + dt / this.params.pulseSpeed) % 1;
      this.state.animationPhase = phase;
    }
  }

  render(renderer) {
    if (!this.visible) return;

    const pos = this.getComputedPosition();
    const { magnitude, direction, color, strokeWidth, headSize, label, formula, showMagnitude, animated } = this.params;

    const rad = (direction * Math.PI) / 180;
    const endX = pos.x + Math.cos(rad) * magnitude;
    const endY = pos.y + Math.sin(rad) * magnitude;

    renderer.push();

    // Pulse effect
    let currentMagnitude = magnitude;
    let currentOpacity = this.opacity;
    if (animated) {
      const pulse = Math.sin(this.state.animationPhase * Math.PI * 2) * 0.1 + 1;
      currentMagnitude = magnitude * pulse;
      currentOpacity = this.opacity * (0.7 + pulse * 0.3);
    }

    const animEndX = pos.x + Math.cos(rad) * currentMagnitude;
    const animEndY = pos.y + Math.sin(rad) * currentMagnitude;

    // Emphasis glow
    if (this.emphasis === 'high') {
      renderer.stroke(color, currentOpacity * 0.3);
      renderer.strokeWeight(strokeWidth + 6);
      renderer.line(pos.x, pos.y, animEndX, animEndY);
    }

    // Arrow line
    renderer.stroke(color, currentOpacity);
    renderer.strokeWeight(strokeWidth);
    renderer.line(pos.x, pos.y, animEndX, animEndY);

    // Arrow head
    renderer.push();
    renderer.translate(animEndX, animEndY);
    renderer.rotate(rad);
    
    renderer.fill(color, currentOpacity);
    renderer.noStroke();
    renderer.triangle(
      0, 0,
      -headSize, -headSize / 2,
      -headSize, headSize / 2
    );
    renderer.pop();

    // Label
    const displayLabel = formula || label;
    if (displayLabel) {
      const labelX = pos.x + Math.cos(rad) * (magnitude / 2);
      const labelY = pos.y + Math.sin(rad) * (magnitude / 2);
      const offsetY = direction > -90 && direction < 90 ? -15 : 15;

      renderer.noStroke();
      
      // Background
      renderer.fill(255, 255, 255, currentOpacity * 0.85);
      const textWidth = displayLabel.length * 8 + 10;
      renderer.rect(labelX - textWidth / 2, labelY + offsetY - 10, textWidth, 18, 4);

      // Text
      renderer.fill(color, currentOpacity);
      renderer.textAlign('center', 'center');
      renderer.textSize(12);
      renderer.textStyle('bold');
      renderer.text(displayLabel, labelX, labelY + offsetY);
    }

    // Magnitude value
    if (showMagnitude) {
      renderer.fill(100, currentOpacity);
      renderer.textSize(10);
      renderer.text(`${magnitude.toFixed(0)} N`, animEndX + 10, animEndY);
    }

    renderer.pop();
  }

  setMagnitude(value) {
    this.params.magnitude = Math.max(10, Math.min(200, value));
    this.emit('magnitude_changed', this.params.magnitude);
  }

  setDirection(angle) {
    this.params.direction = angle;
    this.emit('direction_changed', angle);
  }

  onInteract(type, data) {
    super.onInteract(type, data);

    if (type === 'drag' && this.attachedTo) {
      // Calculate new direction based on drag
      const parentAtom = this.scene?.getAtom(this.attachedTo);
      if (parentAtom) {
        const parentPos = parentAtom.getComputedPosition();
        const dx = data.position.x - parentPos.x;
        const dy = data.position.y - parentPos.y;
        const newAngle = Math.atan2(dy, dx) * 180 / Math.PI;
        const newMagnitude = Math.sqrt(dx * dx + dy * dy);
        
        this.setDirection(newAngle);
        this.setMagnitude(newMagnitude);
      }
    }
  }
}

export default ForceVector;
