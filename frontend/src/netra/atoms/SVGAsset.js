/**
 * 🎨 SVG ASSET ATOM
 * =================
 * 
 * Renders pre-built SVG assets for rich visual scenes.
 * Unlike Entity (basic shapes), this renders complex illustrations.
 * 
 * This is the key to NanoBanana-quality visuals with programmatic control.
 */

import { Atom } from './Atom';
import { getAssetById } from '../assets/SceneAssets';

export class SVGAsset extends Atom {
  static get type() {
    return 'SVGAsset';
  }

  getDefaultParams() {
    return {
      assetId: null,         // ID from SceneAssets library
      scale: 1.0,            // Scale factor
      rotation: 0,           // Rotation in degrees
      flipX: false,          // Horizontal flip
      flipY: false,          // Vertical flip
      tint: null,            // Optional color tint
      glow: false,           // Glow effect
      glowColor: '#FFD700',  // Glow color
      glowIntensity: 0.5,    // Glow strength
      shadow: true,          // Drop shadow
      label: null,           // Optional label below asset
      labelColor: '#374151',
      labelSize: 14,
    };
  }

  getInitialState() {
    return {
      highlighted: false,
      animating: false,
    };
  }

  static getParamSchema() {
    return {
      assetId: { type: 'string', required: true },
      scale: { type: 'number', min: 0.1, max: 5, default: 1.0 },
      rotation: { type: 'number', min: -360, max: 360, default: 0 },
      glow: { type: 'boolean', default: false },
    };
  }

  onMount(scene) {
    super.onMount(scene);
    
    // Load asset data
    this.asset = getAssetById(this.params.assetId);
    
    if (!this.asset) {
      console.warn(`[SVGAsset] Unknown asset: ${this.params.assetId}`);
      this.asset = this._getFallbackAsset();
    }
    
    // Calculate size based on asset dimensions and scale
    const scale = this.params.scale || 1;
    this.size = {
      width: this.asset.width * scale,
      height: this.asset.height * scale,
    };
    
    // Parse SVG for rendering
    this._parsedSVG = this._parseSVG(this.asset.svg);
  }

  _getFallbackAsset() {
    return {
      id: 'fallback',
      name: 'Fallback',
      width: 100,
      height: 100,
      svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="10" width="80" height="80" fill="#E5E7EB" stroke="#9CA3AF" stroke-width="2" rx="8"/>
        <text x="50" y="55" text-anchor="middle" font-size="12" fill="#6B7280">Asset</text>
      </svg>`,
    };
  }

  _parseSVG(svgString) {
    // Create a data URL from the SVG for canvas rendering
    const encoded = encodeURIComponent(svgString);
    const dataUrl = `data:image/svg+xml,${encoded}`;
    
    // Create image element
    const img = new Image();
    img.src = dataUrl;
    
    return {
      dataUrl,
      img,
      loaded: false,
    };
  }

  update(dt) {
    super.update(dt);
    
    // Check if image is loaded
    if (this._parsedSVG && !this._parsedSVG.loaded && this._parsedSVG.img.complete) {
      this._parsedSVG.loaded = true;
    }
  }

  render(renderer) {
    if (!this.visible || !this._parsedSVG) return;

    const pos = this.getComputedPosition();
    const { scale, rotation, flipX, flipY, glow, glowColor, glowIntensity, shadow, label, labelColor, labelSize } = this.params;
    const { highlighted } = this.state;

    const width = this.asset.width * scale;
    const height = this.asset.height * scale;

    renderer.push();
    renderer.translate(pos.x, pos.y);

    // Apply rotation
    if (rotation) {
      renderer.rotate(rotation * Math.PI / 180);
    }

    // Apply flip
    if (flipX || flipY) {
      const sx = flipX ? -1 : 1;
      const sy = flipY ? -1 : 1;
      renderer.scale(sx, sy);
    }

    // Glow effect
    if (glow || highlighted || this.emphasis === 'high') {
      const color = glowColor || '#FFD700';
      const intensity = glowIntensity || 0.5;
      
      // Draw glow layers
      for (let i = 3; i >= 1; i--) {
        const glowSize = i * 6;
        const alpha = intensity * (1 - i * 0.25) * this.opacity;
        renderer.noStroke();
        renderer.fill(color, alpha);
        renderer.ellipse(0, 0, width + glowSize * 2, height + glowSize * 2);
      }
    }

    // Shadow
    if (shadow) {
      renderer.noStroke();
      renderer.fill(0, 0, 0, 20 * this.opacity);
      renderer.ellipse(4, 4, width * 0.9, height * 0.3);
    }

    // Draw the SVG image
    if (this._parsedSVG.loaded && renderer.drawingContext) {
      const ctx = renderer.drawingContext;
      ctx.globalAlpha = this.opacity;
      ctx.drawImage(
        this._parsedSVG.img,
        -width / 2,
        -height / 2,
        width,
        height
      );
      ctx.globalAlpha = 1;
    } else {
      // Fallback: draw placeholder while loading
      renderer.fill('#E5E7EB', this.opacity);
      renderer.stroke('#9CA3AF');
      renderer.strokeWeight(2);
      renderer.rect(-width / 2, -height / 2, width, height, 8);
      
      // Loading indicator
      renderer.noStroke();
      renderer.fill('#6B7280', this.opacity);
      renderer.textAlign('center', 'center');
      renderer.textSize(12);
      renderer.text('Loading...', 0, 0);
    }

    // Highlight border
    if (highlighted || this.emphasis === 'high') {
      renderer.noFill();
      renderer.stroke('#F59E0B', this.opacity * 0.8);
      renderer.strokeWeight(3);
      renderer.rect(-width / 2 - 4, -height / 2 - 4, width + 8, height + 8, 8);
    }

    // Label
    if (label) {
      renderer.noStroke();
      renderer.fill(labelColor, this.opacity);
      renderer.textAlign('center', 'top');
      renderer.textSize(labelSize);
      renderer.text(label, 0, height / 2 + 8);
    }

    renderer.pop();
  }

  // Get anchor position for connecting flows
  getAnchorPosition(anchorName) {
    if (!this.asset || !this.asset.anchors || !this.asset.anchors[anchorName]) {
      return this.getComputedPosition();
    }

    const anchor = this.asset.anchors[anchorName];
    const pos = this.getComputedPosition();
    const scale = this.params.scale || 1;

    return {
      x: pos.x + (anchor.x - 0.5) * this.asset.width * scale,
      y: pos.y + (anchor.y - 0.5) * this.asset.height * scale,
    };
  }

  onInteract(type, data) {
    super.onInteract(type, data);
    
    if (type === 'tap' || type === 'click') {
      this.setState({ highlighted: !this.state.highlighted });
      this.emit('asset_clicked', { assetId: this.params.assetId });
    }
    if (type === 'hover_enter') {
      this.setState({ highlighted: true });
    }
    if (type === 'hover_leave') {
      this.setState({ highlighted: false });
    }
  }
}

export default SVGAsset;
