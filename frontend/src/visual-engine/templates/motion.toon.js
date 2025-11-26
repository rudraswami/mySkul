/**
 * Motion Concept - TOON Template
 * Interactive visual for teaching Motion (गति)
 */

export const motionTOON = {
  topic: "Motion (गति)",
  scene: "street",
  
  analogy: "Auto जब चलता है, distance बदलता है - यही motion है!",
  
  formula: {
    main: "v = d / t",
    meaning: "Velocity equals Distance divided by Time",
    breakdown: [
      { symbol: "v", name: "Velocity (वेग)", unit: "m/s" },
      { symbol: "d", name: "Distance (दूरी)", unit: "meter (m)" },
      { symbol: "t", name: "Time (समय)", unit: "second (s)" },
    ],
    example: "Auto travels 100m in 10s, v = 100/10 = 10 m/s",
  },

  actors: [
    {
      id: "professor",
      type: "professor",
      position: { x: 0.05, y: 0.55 },
      initialState: "pointing",
      speech: "देखो motion!",
    },
  ],

  props: [
    {
      id: "auto",
      type: "auto_rickshaw",
      position: { x: 0.3, y: 0.65 },
      interactive: true,
    },
    {
      id: "scooter",
      type: "scooter",
      position: { x: 0.6, y: 0.68 },
    },
    {
      id: "motion_badge",
      type: "badge_orange",
      text: "गति (Motion)",
      position: { x: 0.5, y: 0.25 },
    },
  ],

  labels: [
    {
      id: "velocity_label",
      text: "v = 10 m/s",
      style: "formula",
      x: 35,
      y: 50,
      showOn: "step_2",
    },
  ],

  animations: [
    {
      id: "auto_move",
      target: "auto",
      type: "moveTo",
      targetX: 75,
      targetY: 65,
      duration: 2000,
    },
  ],

  steps: [
    {
      id: "step_1",
      title: "Auto at rest",
      description: "Auto is stationary at position A",
      animations: [],
      labels: [],
      duration: 2000,
    },
    {
      id: "step_2",
      title: "Auto starts moving",
      description: "Auto moves from A to B - this is motion!",
      animations: ["auto_move"],
      labels: ["velocity_label"],
      duration: 3000,
    },
    {
      id: "step_3",
      title: "Velocity calculated",
      description: "v = distance / time",
      animations: [],
      labels: [],
      duration: 2000,
    },
  ],

  interactions: [
    {
      target: "auto",
      onTap: "highlight(auto)",
      onLongPress: "showFormula()",
    },
  ],
};

/**
 * Velocity TOON Template
 */
export const velocityTOON = {
  topic: "Velocity (वेग)",
  scene: "street",
  
  analogy: "Bike की speed with direction = Velocity!",
  
  formula: {
    main: "v = Δx / Δt",
    meaning: "Change in position per unit time with direction",
    breakdown: [
      { symbol: "v", name: "Velocity", unit: "m/s" },
      { symbol: "Δx", name: "Displacement", unit: "m" },
      { symbol: "Δt", name: "Time interval", unit: "s" },
    ],
  },

  actors: [
    {
      id: "professor",
      type: "professor",
      position: { x: 0.05, y: 0.55 },
    },
  ],

  props: [
    {
      id: "scooter",
      type: "scooter",
      position: { x: 0.25, y: 0.65 },
    },
    {
      id: "velocity_badge",
      type: "badge_blue",
      text: "वेग (v)",
      position: { x: 0.5, y: 0.3 },
    },
  ],

  steps: [
    {
      id: "step_1",
      title: "Starting position",
      animations: [],
      duration: 2000,
    },
    {
      id: "step_2",
      title: "Moving with velocity",
      animations: [],
      duration: 2500,
    },
  ],
};

/**
 * Acceleration TOON Template
 */
export const accelerationTOON = {
  topic: "Acceleration (त्वरण)",
  scene: "street",
  
  analogy: "Auto जब gear बदलता है, speed बढ़ती है - यही acceleration!",
  
  formula: {
    main: "a = Δv / Δt",
    meaning: "Rate of change of velocity",
    breakdown: [
      { symbol: "a", name: "Acceleration (त्वरण)", unit: "m/s²" },
      { symbol: "Δv", name: "Change in velocity", unit: "m/s" },
      { symbol: "Δt", name: "Time interval", unit: "s" },
    ],
    example: "Speed increases from 0 to 20 m/s in 4s, a = 20/4 = 5 m/s²",
  },

  actors: [
    {
      id: "professor",
      type: "professor",
      position: { x: 0.05, y: 0.55 },
      initialState: "explaining",
    },
  ],

  props: [
    {
      id: "auto",
      type: "auto_rickshaw",
      position: { x: 0.2, y: 0.65 },
    },
    {
      id: "accel_badge",
      type: "badge_green",
      text: "त्वरण (a)",
      position: { x: 0.5, y: 0.3 },
    },
  ],

  steps: [
    {
      id: "step_1",
      title: "Auto starting slow",
      animations: [],
      duration: 2000,
    },
    {
      id: "step_2",
      title: "Accelerating!",
      animations: [],
      duration: 2500,
    },
    {
      id: "step_3",
      title: "Formula: a = Δv/Δt",
      animations: [],
      duration: 2000,
    },
  ],
};

export default motionTOON;
