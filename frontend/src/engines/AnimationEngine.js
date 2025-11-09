/**
 * Animation Engine for Visual Teaching System
 * Handles all animation primitives and orchestration
 */

import * as d3 from 'd3';

export default class AnimationEngine {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.options = {
      width: 800,
      height: 450,
      fps: 60,
      renderer: 'svg',
      responsive: true,
      ...options
    };

    this.svg = null;
    this.animations = [];
    this.currentStage = 0;
    this.isPlaying = false;
    this.isPaused = false;
    this.speed = 1;
    this.elements = new Map();
    this.listeners = new Map();

    this.initialize();
  }

  initialize() {
    // Create SVG container
    this.svg = d3.select(this.canvas.parentElement)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', `0 0 ${this.options.width} ${this.options.height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .style('position', 'absolute')
      .style('top', 0)
      .style('left', 0);

    // Create main groups
    this.backgroundGroup = this.svg.append('g').attr('class', 'background');
    this.mainGroup = this.svg.append('g').attr('class', 'main-content');
    this.foregroundGroup = this.svg.append('g').attr('class', 'foreground');
    this.interactionGroup = this.svg.append('g').attr('class', 'interactions');

    // Hide canvas if using SVG renderer
    if (this.options.renderer === 'svg') {
      this.canvas.style.display = 'none';
    }
  }

  // ============================================================================
  // CORE API
  // ============================================================================

  loadVisual(visualData) {
    this.visualData = visualData;
    this.stages = visualData.stages;
    this.currentStage = 0;

    // Preload all assets and prepare animations
    this.preloadAssets();

    // Load first stage
    if (this.stages && this.stages.length > 0) {
      this.loadStage(0);
    }
  }

  play() {
    this.isPlaying = true;
    this.isPaused = false;
    this.executeStageAnimations();
  }

  pause() {
    this.isPlaying = false;
    this.isPaused = true;
    // Pause all running animations
    this.svg.selectAll('*').interrupt();
  }

  restart() {
    this.currentStage = 0;
    this.clearAll();
    this.loadStage(0);
  }

  skipToStage(stageIndex) {
    if (stageIndex >= 0 && stageIndex < this.stages.length) {
      this.currentStage = stageIndex;
      this.clearAll();
      this.loadStage(stageIndex);
    }
  }

  setSpeed(speed) {
    this.speed = speed;
  }

  destroy() {
    this.clearAll();
    if (this.svg) {
      this.svg.remove();
    }
    this.listeners.clear();
  }

  // ============================================================================
  // STAGE MANAGEMENT
  // ============================================================================

  loadStage(stageIndex) {
    const stage = this.stages[stageIndex];
    if (!stage) return;

    // Clear previous stage if needed
    if (stage.clearPrevious) {
      this.clearAll();
    }

    // Execute stage animations
    stage.animations.forEach(animation => {
      this.executeAnimation(animation);
    });
  }

  executeStageAnimations() {
    const stage = this.stages[this.currentStage];
    if (!stage) return;

    let animationQueue = Promise.resolve();

    stage.animations.forEach((animation, index) => {
      animationQueue = animationQueue.then(() => {
        if (!this.isPlaying) return;
        return this.executeAnimation(animation);
      });
    });

    // When all animations complete, trigger stage complete
    animationQueue.then(() => {
      if (this.isPlaying) {
        this.emit('stageComplete', this.currentStage);
      }
    });
  }

  executeAnimation(animation) {
    return new Promise((resolve) => {
      const duration = (animation.duration || 1000) / this.speed;

      switch (animation.type) {
        case 'split_screen_create':
          this.createSplitScreen(animation, duration).then(resolve);
          break;

        case 'create_element':
          this.createElement(animation, duration).then(resolve);
          break;

        case 'create_sentence':
          this.createSentence(animation, duration).then(resolve);
          break;

        case 'morph':
          this.morphElement(animation, duration).then(resolve);
          break;

        case 'arrow':
          this.drawArrow(animation, duration).then(resolve);
          break;

        case 'highlight':
          this.highlightElement(animation, duration).then(resolve);
          break;

        case 'rotate_scene':
          this.rotateScene(animation, duration).then(resolve);
          break;

        case 'rearrange_blocks':
          this.rearrangeBlocks(animation, duration).then(resolve);
          break;

        case 'add_points':
          this.addPoints(animation, duration).then(resolve);
          break;

        case 'emphasis':
          this.addEmphasis(animation, duration).then(resolve);
          break;

        default:
          resolve();
      }
    });
  }

  // ============================================================================
  // ANIMATION PRIMITIVES
  // ============================================================================

  createSplitScreen(config, duration) {
    return new Promise(resolve => {
      const width = this.options.width;
      const height = this.options.height;
      const midX = width / 2;

      // Create left panel
      const leftPanel = this.mainGroup.append('g')
        .attr('class', 'left-panel')
        .attr('transform', `translate(-${width}, 0)`);

      leftPanel.append('rect')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', midX - 10)
        .attr('height', height)
        .attr('fill', '#f3f4f6')
        .attr('stroke', '#d1d5db')
        .attr('stroke-width', 2)
        .attr('rx', 10);

      leftPanel.append('text')
        .attr('x', midX / 2)
        .attr('y', 40)
        .attr('text-anchor', 'middle')
        .attr('font-size', '20px')
        .attr('font-weight', 'bold')
        .attr('fill', '#1f2937')
        .text(config.left_label);

      // Create right panel
      const rightPanel = this.mainGroup.append('g')
        .attr('class', 'right-panel')
        .attr('transform', `translate(${width}, 0)`);

      rightPanel.append('rect')
        .attr('x', midX + 10)
        .attr('y', 0)
        .attr('width', midX - 10)
        .attr('height', height)
        .attr('fill', '#f3f4f6')
        .attr('stroke', '#d1d5db')
        .attr('stroke-width', 2)
        .attr('rx', 10);

      rightPanel.append('text')
        .attr('x', midX + (midX / 2))
        .attr('y', 40)
        .attr('text-anchor', 'middle')
        .attr('font-size', '20px')
        .attr('font-weight', 'bold')
        .attr('fill', '#1f2937')
        .text(config.right_label);

      // Animate panels sliding in
      leftPanel.transition()
        .duration(duration)
        .ease(d3.easeBackOut)
        .attr('transform', 'translate(0, 0)');

      rightPanel.transition()
        .duration(duration)
        .ease(d3.easeBackOut)
        .attr('transform', 'translate(0, 0)')
        .on('end', resolve);

      // Store references
      this.elements.set('left_panel', leftPanel);
      this.elements.set('right_panel', rightPanel);
    });
  }

  createSentence(config, duration) {
    return new Promise(resolve => {
      const centerX = this.options.width / 2;
      const centerY = this.options.height / 2;
      const blockWidth = 120;
      const blockHeight = 60;
      const spacing = 20;

      const sentenceGroup = this.mainGroup.append('g')
        .attr('class', 'sentence-blocks');

      const totalWidth = (config.structure.length * blockWidth) + ((config.structure.length - 1) * spacing);
      const startX = centerX - (totalWidth / 2);

      config.structure.forEach((word, index) => {
        const blockGroup = sentenceGroup.append('g')
          .attr('class', `word-block-${index}`)
          .attr('transform', `translate(${startX + (index * (blockWidth + spacing))}, ${centerY})`)
          .style('opacity', 0);

        // Block background
        blockGroup.append('rect')
          .attr('width', blockWidth)
          .attr('height', blockHeight)
          .attr('rx', 8)
          .attr('fill', this.getBlockColor(config.labels[index]))
          .attr('stroke', '#9ca3af')
          .attr('stroke-width', 2);

        // Word text
        blockGroup.append('text')
          .attr('x', blockWidth / 2)
          .attr('y', blockHeight / 2 - 5)
          .attr('text-anchor', 'middle')
          .attr('font-size', '16px')
          .attr('font-weight', 'bold')
          .attr('fill', '#1f2937')
          .text(word);

        // Label text
        blockGroup.append('text')
          .attr('x', blockWidth / 2)
          .attr('y', blockHeight / 2 + 15)
          .attr('text-anchor', 'middle')
          .attr('font-size', '12px')
          .attr('fill', '#6b7280')
          .text(config.labels[index]);

        // Animate appearance
        blockGroup.transition()
          .duration(duration / config.structure.length)
          .delay(index * (duration / config.structure.length))
          .style('opacity', 1)
          .attr('transform', `translate(${startX + (index * (blockWidth + spacing))}, ${centerY - blockHeight / 2})`);

        this.elements.set(`word_${index}`, blockGroup);
      });

      setTimeout(() => resolve(), duration);
    });
  }

  drawArrow(config, duration) {
    return new Promise(resolve => {
      const fromElement = this.elements.get(config.from) || this.svg.select(`.${config.from}`);
      const toElement = this.elements.get(config.to) || this.svg.select(`.${config.to}`);

      if (!fromElement.empty() && !toElement.empty()) {
        // Get positions
        const fromBox = fromElement.node().getBBox();
        const toBox = toElement.node().getBBox();

        const fromX = fromBox.x + fromBox.width / 2;
        const fromY = fromBox.y + fromBox.height / 2;
        const toX = toBox.x + toBox.width / 2;
        const toY = toBox.y + toBox.height / 2;

        // Create curved arrow path
        const midX = (fromX + toX) / 2;
        const midY = (fromY + toY) / 2 - 50; // Curve upward

        const path = `M ${fromX} ${fromY} Q ${midX} ${midY} ${toX} ${toY}`;

        // Draw arrow
        const arrow = this.foregroundGroup.append('path')
          .attr('d', path)
          .attr('fill', 'none')
          .attr('stroke', config.color || '#10b981')
          .attr('stroke-width', 3)
          .attr('marker-end', 'url(#arrowhead)')
          .style('opacity', 0);

        // Add arrow marker
        this.svg.append('defs').append('marker')
          .attr('id', 'arrowhead')
          .attr('markerWidth', 10)
          .attr('markerHeight', 7)
          .attr('refX', 9)
          .attr('refY', 3.5)
          .attr('orient', 'auto')
          .append('polygon')
          .attr('points', '0 0, 10 3.5, 0 7')
          .attr('fill', config.color || '#10b981');

        // Add label if provided
        if (config.label) {
          this.foregroundGroup.append('text')
            .attr('x', midX)
            .attr('y', midY - 10)
            .attr('text-anchor', 'middle')
            .attr('font-size', '14px')
            .attr('fill', config.color || '#10b981')
            .text(config.label)
            .style('opacity', 0)
            .transition()
            .duration(duration)
            .style('opacity', 1);
        }

        // Animate arrow drawing
        const totalLength = arrow.node().getTotalLength();
        arrow
          .attr('stroke-dasharray', totalLength)
          .attr('stroke-dashoffset', totalLength)
          .style('opacity', 1)
          .transition()
          .duration(duration)
          .ease(d3.easeLinear)
          .attr('stroke-dashoffset', 0)
          .on('end', resolve);
      } else {
        resolve();
      }
    });
  }

  highlightElement(config, duration) {
    return new Promise(resolve => {
      const element = this.elements.get(config.target) || this.svg.select(`.${config.target}`);

      if (!element.empty()) {
        // Create glow effect
        const bbox = element.node().getBBox();

        const glowRect = this.foregroundGroup.append('rect')
          .attr('x', bbox.x - 10)
          .attr('y', bbox.y - 10)
          .attr('width', bbox.width + 20)
          .attr('height', bbox.height + 20)
          .attr('rx', 10)
          .attr('fill', 'none')
          .attr('stroke', '#fbbf24')
          .attr('stroke-width', 3)
          .style('opacity', 0);

        // Animate glow
        glowRect.transition()
          .duration(duration / 4)
          .style('opacity', 1)
          .transition()
          .duration(duration / 2)
          .attr('stroke-width', 5)
          .transition()
          .duration(duration / 4)
          .style('opacity', 0)
          .on('end', () => {
            glowRect.remove();
            resolve();
          });
      } else {
        resolve();
      }
    });
  }

  morphElement(config, duration) {
    return new Promise(resolve => {
      const element = this.elements.get(config.from) || this.svg.select(`.${config.from}`);

      if (!element.empty()) {
        // Morph animation - simplified for now
        element.transition()
          .duration(duration)
          .ease(d3.easeCubicInOut)
          .style('opacity', 0.5)
          .transition()
          .duration(duration)
          .style('opacity', 1)
          .on('end', resolve);
      } else {
        resolve();
      }
    });
  }

  rotateScene(config, duration) {
    return new Promise(resolve => {
      const centerX = this.options.width / 2;
      const centerY = this.options.height / 2;

      this.mainGroup.transition()
        .duration(duration)
        .ease(d3.easeCubicInOut)
        .attr('transform', `rotate(${config.degrees}, ${centerX}, ${centerY})`)
        .on('end', resolve);
    });
  }

  rearrangeBlocks(config, duration) {
    return new Promise(resolve => {
      // Rearrange word blocks
      const blockWidth = 120;
      const spacing = 20;
      const centerX = this.options.width / 2;
      const centerY = this.options.height / 2;

      const totalWidth = (config.new_order.length * blockWidth) + ((config.new_order.length - 1) * spacing);
      const startX = centerX - (totalWidth / 2);

      config.new_order.forEach((word, index) => {
        const block = this.elements.get(`word_${index}`);
        if (block) {
          block.transition()
            .duration(duration)
            .ease(d3.easeBackOut)
            .attr('transform', `translate(${startX + (index * (blockWidth + spacing))}, ${centerY - 30})`);

          // Update text
          block.select('text').text(word);
          block.selectAll('text').nodes()[1].textContent = config.new_labels[index];
        }
      });

      setTimeout(resolve, duration);
    });
  }

  addPoints(config, duration) {
    return new Promise(resolve => {
      const panel = this.elements.get(`${config.panel}_panel`);
      if (!panel.empty()) {
        const pointsGroup = panel.append('g')
          .attr('class', 'points');

        config.points.forEach((point, index) => {
          const pointText = pointsGroup.append('text')
            .attr('x', config.panel === 'left' ? 20 : this.options.width / 2 + 20)
            .attr('y', 80 + (index * 30))
            .attr('font-size', '14px')
            .attr('fill', '#4b5563')
            .style('opacity', 0)
            .text(`• ${point}`);

          pointText.transition()
            .duration(duration / config.points.length)
            .delay(index * (duration / config.points.length))
            .style('opacity', 1);
        });
      }
      setTimeout(resolve, duration);
    });
  }

  addEmphasis(config, duration) {
    return new Promise(resolve => {
      // Create pulsing emphasis effect
      const emphasisCircle = this.foregroundGroup.append('circle')
        .attr('cx', this.options.width / 2)
        .attr('cy', this.options.height / 2)
        .attr('r', 0)
        .attr('fill', 'none')
        .attr('stroke', config.color || '#fbbf24')
        .attr('stroke-width', 3);

      emphasisCircle.transition()
        .duration(duration)
        .ease(d3.easeElastic)
        .attr('r', 100)
        .style('opacity', 0)
        .on('end', () => {
          emphasisCircle.remove();
          resolve();
        });
    });
  }

  // ============================================================================
  // HELPER METHODS
  // ============================================================================

  getBlockColor(label) {
    const colors = {
      'Subject': '#dbeafe',
      'Verb': '#fce7f3',
      'Object': '#e0e7ff',
      'Agent': '#fed7aa',
      'default': '#f3f4f6'
    };
    return colors[label] || colors.default;
  }

  clearAll() {
    this.mainGroup.selectAll('*').remove();
    this.foregroundGroup.selectAll('*').remove();
    this.interactionGroup.selectAll('*').remove();
    this.elements.clear();
  }

  preloadAssets() {
    // Preload any images or assets needed
  }

  // ============================================================================
  // EVENT SYSTEM
  // ============================================================================

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        callback(data);
      });
    }
  }

  // ============================================================================
  // INTERACTION HANDLING
  // ============================================================================

  continueFromInteraction(response) {
    // Process interaction response and continue
    this.currentStage++;
    if (this.currentStage < this.stages.length) {
      this.loadStage(this.currentStage);
      this.play();
    } else {
      this.emit('animationComplete');
    }
  }
}