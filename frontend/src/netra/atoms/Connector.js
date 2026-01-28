/**
 * 🔗 CONNECTOR ATOM
 * =================
 * 
 * Line or arrow connecting two atoms.
 */

import { Atom } from './Atom';

export class Connector extends Atom {
  static get type() {
    return 'Connector';
  }

  getDefaultParams() {
    return {
      fromAtom: null,        // Source atom ID
      toAtom: null,          // Target atom ID
      fromAnchor: 'center',
      toAnchor: 'center',
      style: 'solid',        // solid, dashed, dotted
      color: '#6B7280',
      strokeWidth: 2,
      arrow: 'none',         // none, end, start, both
      arrowSize: 10,
      label: null,
      labelPosition: 0.5,    // 0-1 along line
      curvature: 0           // 0 = straight, positive = curve right
    };
  }

  static getParamSchema() {
    return {
      fromAtom: { type: 'string', required: true },
      toAtom: { type: 'string', required: true },
      style: { type: 'string', default: 'solid' },
      color: { type: 'string', default: '#6B7280' },
      strokeWidth: { type: 'number', min: 1, max: 8, default: 2 },
      arrow: { type: 'string', default: 'none' },
      arrowSize: { type: 'number', min: 5, max: 20, default: 10 },
      curvature: { type: 'number', min: -100, max: 100, default: 0 }
    };
  }

  render(renderer) {
    if (!this.visible || !this.scene) return;

    const fromAtom = this.scene.getAtom(this.params.fromAtom);
    const toAtom = this.scene.getAtom(this.params.toAtom);

    if (!fromAtom || !toAtom) return;

    const fromPos = fromAtom.getComputedPosition();
    const toPos = toAtom.getComputedPosition();

    const fromOffset = this.getAnchorOffset(fromAtom, this.params.fromAnchor);
    const toOffset = this.getAnchorOffset(toAtom, this.params.toAnchor);

    const x1 = fromPos.x + fromOffset.x;
    const y1 = fromPos.y + fromOffset.y;
    const x2 = toPos.x + toOffset.x;
    const y2 = toPos.y + toOffset.y;

    const { style, color, strokeWidth, arrow, arrowSize, label, labelPosition, curvature } = this.params;

    renderer.push();

    // Set stroke style
    renderer.stroke(color, this.opacity);
    renderer.strokeWeight(strokeWidth);
    renderer.noFill();

    if (style === 'dashed') {
      renderer.drawingContext.setLineDash([8, 4]);
    } else if (style === 'dotted') {
      renderer.drawingContext.setLineDash([2, 4]);
    }

    // Draw line
    if (curvature === 0) {
      renderer.line(x1, y1, x2, y2);
    } else {
      // Bezier curve
      const midX = (x1 + x2) / 2;
      const midY = (y1 + y2) / 2;
      const perpX = -(y2 - y1) * curvature / 100;
      const perpY = (x2 - x1) * curvature / 100;
      const cpX = midX + perpX;
      const cpY = midY + perpY;
      
      renderer.beginShape();
      renderer.vertex(x1, y1);
      renderer.quadraticVertex(cpX, cpY, x2, y2);
      renderer.endShape();
    }

    // Reset dash
    renderer.drawingContext.setLineDash([]);

    // Draw arrows
    if (arrow === 'end' || arrow === 'both') {
      this.drawArrowHead(renderer, x2, y2, x1, y1, arrowSize, color);
    }
    if (arrow === 'start' || arrow === 'both') {
      this.drawArrowHead(renderer, x1, y1, x2, y2, arrowSize, color);
    }

    // Draw label
    if (label) {
      const lx = x1 + (x2 - x1) * labelPosition;
      const ly = y1 + (y2 - y1) * labelPosition - 10;
      
      renderer.noStroke();
      renderer.fill(color, this.opacity);
      renderer.textAlign('center', 'center');
      renderer.textSize(12);
      renderer.text(label, lx, ly);
    }

    renderer.pop();
  }

  drawArrowHead(renderer, tipX, tipY, tailX, tailY, size, color) {
    const angle = Math.atan2(tipY - tailY, tipX - tailX);
    
    renderer.push();
    renderer.translate(tipX, tipY);
    renderer.rotate(angle);
    
    renderer.fill(color, this.opacity);
    renderer.noStroke();
    renderer.triangle(
      0, 0,
      -size, -size / 2,
      -size, size / 2
    );
    
    renderer.pop();
  }
}

export default Connector;
