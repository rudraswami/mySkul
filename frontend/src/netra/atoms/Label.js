/**
 * 📝 LABEL ATOM
 * =============
 * 
 * Text annotation with optional formula/equation support.
 */

import { Atom } from './Atom';

export class Label extends Atom {
  static get type() {
    return 'Label';
  }

  getDefaultParams() {
    return {
      text: '',
      formula: null,         // LaTeX formula (for future MathJax)
      fontSize: 16,
      fontFamily: 'system-ui, sans-serif',
      fontWeight: 'normal',
      color: '#1F2937',
      backgroundColor: null,
      padding: 8,
      cornerRadius: 4,
      maxWidth: 200
    };
  }

  getInitialState() {
    return {
      visible: true
    };
  }

  static getParamSchema() {
    return {
      text: { type: 'string', required: true },
      formula: { type: 'string' },
      fontSize: { type: 'number', min: 8, max: 48, default: 16 },
      color: { type: 'string', default: '#1F2937' },
      backgroundColor: { type: 'string' },
      padding: { type: 'number', min: 0, max: 32, default: 8 }
    };
  }

  onMount(scene) {
    super.onMount(scene);
    // Estimate size based on text
    const charWidth = this.params.fontSize * 0.6;
    const estimatedWidth = Math.min(this.params.text.length * charWidth, this.params.maxWidth);
    this.size = {
      width: estimatedWidth + this.params.padding * 2,
      height: this.params.fontSize + this.params.padding * 2
    };
  }

  render(renderer) {
    if (!this.visible) return;

    const pos = this.getComputedPosition();
    const { text, formula, fontSize, fontFamily, fontWeight, color, backgroundColor, padding, cornerRadius } = this.params;

    const displayText = formula || text;

    renderer.push();
    renderer.translate(pos.x, pos.y);

    // Background
    if (backgroundColor) {
      renderer.fill(backgroundColor, this.opacity * 0.9);
      renderer.noStroke();
      renderer.rect(
        -this.size.width / 2,
        -this.size.height / 2,
        this.size.width,
        this.size.height,
        cornerRadius
      );
    }

    // Text
    renderer.noStroke();
    renderer.fill(color, this.opacity);
    renderer.textAlign('center', 'center');
    renderer.textSize(fontSize);
    renderer.textFont(fontFamily);
    renderer.textStyle(fontWeight === 'bold' ? 'bold' : 'normal');
    renderer.text(displayText, 0, 0);

    renderer.pop();
  }
}

export default Label;
