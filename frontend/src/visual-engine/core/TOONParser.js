/**
 * TOON Parser
 * Converts TOON (Teaching Object Oriented Notation) to Scene Configuration
 * 
 * TOON is our custom DSL for defining visual teaching scenes
 */

export class TOONParser {
  constructor() {
    this.defaultConfig = {
      viewport: { width: 640, height: 360 },
      background: 'classroom',
      language: 'hinglish',
      animationSpeed: 1,
    };
  }

  /**
   * Parse TOON object into scene configuration
   * @param {Object} toon - TOON instruction object
   * @returns {Object} Scene configuration
   */
  parse(toon) {
    const config = {
      ...this.defaultConfig,
      id: toon.topic?.toLowerCase().replace(/\s+/g, '_') || 'scene',
      topic: toon.topic || 'Concept',
      
      // Scene setup
      scene: this.parseScene(toon.scene),
      
      // Actors (professor, students, etc.)
      actors: this.parseActors(toon.actors || []),
      
      // Props (objects in the scene)
      props: this.parseProps(toon.props || []),
      
      // Animations timeline
      animations: this.parseAnimations(toon.animations || []),
      
      // Labels and formulas
      labels: this.parseLabels(toon.labels || []),
      
      // Interaction zones
      interactions: this.parseInteractions(toon.interactions || []),
      
      // Cultural analogy
      analogy: toon.analogy || null,
      
      // Steps for progressive reveal
      steps: this.parseSteps(toon.steps || []),
    };

    return this.validate(config);
  }

  parseScene(sceneName) {
    const scenes = {
      'cricket_pitch': {
        background: 'cricket',
        gradient: ['#87CEEB', '#90EE90'],
        groundLevel: 0.75,
        props: ['pitch', 'boundary'],
      },
      'classroom': {
        background: 'classroom',
        gradient: ['#FFF8E1', '#FFECB3'],
        groundLevel: 0.85,
        props: ['blackboard', 'desk'],
      },
      'lab': {
        background: 'lab',
        gradient: ['#E3F2FD', '#BBDEFB'],
        groundLevel: 0.80,
        props: ['table', 'equipment'],
      },
      'street': {
        background: 'street',
        gradient: ['#81D4FA', '#E1F5FE'],
        groundLevel: 0.70,
        props: ['road', 'traffic_signal'],
      },
      'village': {
        background: 'village',
        gradient: ['#64B5F6', '#E3F2FD'],
        groundLevel: 0.75,
        props: ['tree', 'grass'],
      },
      'space': {
        background: 'space',
        gradient: ['#1A237E', '#000051'],
        groundLevel: null,
        props: ['stars', 'earth'],
      },
    };

    return scenes[sceneName] || scenes['classroom'];
  }

  parseActors(actors) {
    return actors.map((actor, index) => ({
      id: actor.id || `actor_${index}`,
      type: actor.type || 'professor',
      role: actor.role || 'demonstrator',
      position: actor.position || { x: 0.15, y: 0.5 },
      scale: actor.scale || 1,
      initialState: actor.initialState || 'standing',
      actions: actor.actions || [],
      speech: actor.speech || null,
    }));
  }

  parseProps(props) {
    return props.map((prop, index) => ({
      id: prop.id || `prop_${index}`,
      type: prop.type,
      position: prop.position || { x: 0.5, y: 0.5 },
      size: prop.size || 'medium',
      rotation: prop.rotation || 0,
      physics: {
        mass: prop.mass || '1kg',
        velocity: prop.velocity || { x: 0, y: 0 },
        acceleration: prop.acceleration || { x: 0, y: 0 },
      },
      style: prop.style || {},
      interactive: prop.interactive !== false,
    }));
  }

  parseAnimations(animations) {
    return animations.map((anim, index) => ({
      id: anim.id || `anim_${index}`,
      target: anim.target,
      type: anim.type,
      trigger: anim.trigger || 'auto', // 'auto', 'tap', 'step'
      delay: anim.delay || 0,
      duration: anim.duration || 1000,
      easing: anim.easing || 'easeInOut',
      params: this.parseAnimationParams(anim),
      loop: anim.loop || false,
    }));
  }

  parseAnimationParams(anim) {
    const typeParams = {
      'throw': { force: anim.force || 'medium', angle: anim.angle || -30 },
      'push': { direction: anim.direction || 'right', force: anim.force || 'medium' },
      'pull': { direction: anim.direction || 'left', force: anim.force || 'medium' },
      'fall': { acceleration: 9.8, bounce: anim.bounce || 0 },
      'rotate': { angle: anim.angle || 360, origin: anim.origin || 'center' },
      'scale': { from: anim.from || 1, to: anim.to || 1.5 },
      'move': { to: anim.to || { x: 0, y: 0 }, path: anim.path || 'linear' },
      'vector_grow': { direction: anim.direction, magnitude: anim.magnitude || 100 },
      'gesture': { gesture: anim.gesture || 'point', target: anim.gestureTarget },
    };

    return typeParams[anim.type] || {};
  }

  parseLabels(labels) {
    return labels.map((label, index) => ({
      id: label.id || `label_${index}`,
      target: label.target,
      text: label.text,
      textHi: label.textHi || null, // Hindi translation
      position: label.position || 'above', // 'above', 'below', 'left', 'right'
      style: label.style || 'default', // 'default', 'formula', 'highlight', 'speech'
      showOn: label.showOn || 'always', // 'always', 'tap', 'step:2'
      animation: label.animation || 'fadeIn',
    }));
  }

  parseInteractions(interactions) {
    return interactions.map((interaction, index) => ({
      id: interaction.id || `interaction_${index}`,
      target: interaction.target,
      type: interaction.type || 'tap', // 'tap', 'longPress', 'swipe', 'drag'
      action: interaction.action, // 'animate', 'showFormula', 'nextStep', 'explain'
      params: interaction.params || {},
    }));
  }

  parseSteps(steps) {
    return steps.map((step, index) => ({
      id: step.id || `step_${index}`,
      order: index + 1,
      title: step.title,
      description: step.description,
      animations: step.animations || [],
      labels: step.labels || [],
      duration: step.duration || 2000,
      autoAdvance: step.autoAdvance !== false,
    }));
  }

  validate(config) {
    // Ensure required fields
    if (!config.topic) {
      console.warn('TOON: Missing topic');
    }
    
    // Validate animation targets exist
    config.animations.forEach(anim => {
      const targetExists = 
        config.props.some(p => p.id === anim.target) ||
        config.actors.some(a => a.id === anim.target) ||
        anim.target === 'vector';
      
      if (!targetExists && anim.target) {
        console.warn(`TOON: Animation target "${anim.target}" not found`);
      }
    });

    return config;
  }
}

export default new TOONParser();









