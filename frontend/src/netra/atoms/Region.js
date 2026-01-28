/**
 * 🔲 REGION ATOM
 * ==============
 * 
 * Bounded area/zone for grouping or highlighting.
 */

import { Atom } from './Atom';

export class Region extends Atom {
  static get type() {
    return 'Region';
  }

  getDefaultParams() {
    return {
      width: 200,
      height: 150,
      fill: 'rgba(59, 130, 246, 0.1)',
      stroke: '#3B82F6',
      strokeWidth: 2,
      strokeStyle: 'dashed',
      cornerRadius: 8,
      label: null,
      labelPosition: 'top'
    };
  }

  static getParamSchema() {
    return {
      width: { type: 'number', min: 50, max: 800, default: 200 },
      height: { type: 'number', min: 50, max: 600, default: 150 },
      fill: { type: 'string' },
      stroke: { type: 'string', default: '#3B82F6' },
      strokeWidth: { type: 'number', min: 0, max: 6, default: 2 },
      strokeStyle: { type: 'string', default: 'dashed' },
      cornerRadius: { type: 'number', min: 0, max: 30, default: 8 }
    };
  }

  onMount(scene) {
    super.onMount(scene);
    this.size = {
      width: this.params.width,
      height: this.params.height
    };
  }

  render(renderer) {
    if (!this.visible) return;

    const pos = this.getComputedPosition();
    const { width, height, fill, stroke, strokeWidth, strokeStyle, cornerRadius, label, labelPosition } = this.params;

    renderer.push();
    renderer.translate(pos.x, pos.y);

    // Set stroke style
    if (strokeStyle === 'dashed') {
      renderer.drawingContext.setLineDash([8, 4]);
    } else if (strokeStyle === 'dotted') {
      renderer.drawingContext.setLineDash([3, 3]);
    }

    // Draw region
    renderer.fill(fill, this.opacity);
    renderer.stroke(stroke, this.opacity);
    renderer.strokeWeight(strokeWidth);
    renderer.rect(-width / 2, -height / 2, width, height, cornerRadius);

    // Reset dash
    renderer.drawingContext.setLineDash([]);

    // Label
    if (label) {
      const ly = labelPosition === 'top' ? -height / 2 - 12 : height / 2 + 12;
      
      renderer.noStroke();
      renderer.fill(stroke, this.opacity);
      renderer.textAlign('center', 'center');
      renderer.textSize(12);
      renderer.text(label, 0, ly);
    }

    renderer.pop();
  }
}

export default Region;
