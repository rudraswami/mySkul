/**
 * Force Concept - TOON Template
 * Complete interactive visual for teaching Force (बल)
 */

export const forceTOON = {
  topic: "Force (बल)",
  scene: "cricket_pitch",
  
  // Main analogy for connection
  analogy: "Bowler जितना ज़ोर से फेंकता है (Force), ball उतनी तेज़ जाती है (Acceleration)!",
  
  // Formula card data
  formula: {
    main: "F = m × a",
    meaning: "Force equals Mass times Acceleration",
    breakdown: [
      { symbol: "F", name: "Force (बल)", unit: "Newton (N)" },
      { symbol: "m", name: "Mass (द्रव्यमान)", unit: "Kilogram (kg)" },
      { symbol: "a", name: "Acceleration (त्वरण)", unit: "m/s²" },
    ],
    example: "Ball mass = 0.15 kg, If acceleration = 10 m/s², then F = 0.15 × 10 = 1.5 N",
  },

  // Actors in the scene
  actors: [
    {
      id: "professor",
      type: "professor",
      role: "demonstrator",
      position: { x: 0.08, y: 0.6 },
      initialState: "pointing",
      speech: "देखो!",
    },
  ],

  // Props in the scene
  props: [
    {
      id: "ball",
      type: "cricket_ball",
      position: { x: 0.25, y: 0.5 },
      mass: "0.15 kg",
      interactive: true,
    },
    {
      id: "stumps",
      type: "stumps",
      position: { x: 0.85, y: 0.7 },
    },
    {
      id: "bat",
      type: "bat",
      position: { x: 0.65, y: 0.6 },
    },
    {
      id: "force_badge",
      type: "badge_orange",
      text: "बल (F)",
      position: { x: 0.5, y: 0.35 },
    },
    {
      id: "mass_label",
      type: "card",
      text: "m = 0.15 kg",
      position: { x: 0.28, y: 0.4 },
    },
  ],

  // Labels that appear on steps
  labels: [
    {
      id: "step1_label",
      text: "Step 1: Professor applies force",
      style: "step",
      x: 50,
      y: 8,
      showOn: "step_1",
    },
    {
      id: "step2_label",
      text: "Step 2: Ball accelerates forward",
      style: "step",
      x: 50,
      y: 8,
      showOn: "step_2",
    },
    {
      id: "step3_label",
      text: "Step 3: F = m × a explains it!",
      style: "step",
      x: 50,
      y: 8,
      showOn: "step_3",
    },
  ],

  // Animation definitions
  animations: [
    {
      id: "professor_throw",
      target: "professor",
      type: "gesture",
      params: { gesture: "pointing" },
      duration: 0.5,
    },
    {
      id: "ball_motion",
      target: "ball",
      type: "projectile",
      force: "high",
      angle: -10,
      duration: 1.5,
    },
    {
      id: "force_arrow",
      target: "force_vector",
      type: "vector_grow",
      direction: "right",
      magnitude: 100,
      duration: 0.8,
    },
  ],

  // Step definitions for timeline
  steps: [
    {
      id: "step_1",
      title: "Professor demonstrates force",
      description: "Watch as the bowler prepares to throw",
      animations: ["professor_throw"],
      labels: ["step1_label"],
      duration: 2000,
      autoAdvance: true,
    },
    {
      id: "step_2",
      title: "Ball accelerates",
      description: "Force causes the ball to speed up",
      animations: ["ball_motion", "force_arrow"],
      labels: ["step2_label"],
      duration: 3000,
      autoAdvance: true,
    },
    {
      id: "step_3",
      title: "Formula revealed",
      description: "F = m × a explains the relationship",
      animations: [],
      labels: ["step3_label"],
      duration: 2000,
      autoAdvance: false,
    },
  ],

  // Interaction definitions
  interactions: [
    {
      target: "ball",
      onTap: "highlight(force_arrow)",
      onLongPress: "showFormula()",
    },
    {
      target: "force_badge",
      onTap: "pulse(force_badge)",
    },
    {
      onSwipe: "next_step",
    },
  ],
};

/**
 * Friction TOON Template
 */
export const frictionTOON = {
  topic: "Friction (घर्षण)",
  scene: "street",
  
  analogy: "Auto जब brake लगाता है, friction ही उसे रोकता है!",
  
  formula: {
    main: "f = μN",
    meaning: "Friction equals coefficient times Normal force",
    breakdown: [
      { symbol: "f", name: "Friction (घर्षण)", unit: "Newton (N)" },
      { symbol: "μ", name: "Coefficient (गुणांक)", unit: "no unit" },
      { symbol: "N", name: "Normal Force", unit: "Newton (N)" },
    ],
    example: "If μ = 0.5 and N = 100 N, then f = 0.5 × 100 = 50 N",
  },

  actors: [
    {
      id: "professor",
      type: "professor",
      position: { x: 0.08, y: 0.6 },
      initialState: "explaining",
    },
  ],

  props: [
    {
      id: "auto",
      type: "auto_rickshaw",
      position: { x: 0.5, y: 0.65 },
    },
    {
      id: "friction_badge",
      type: "badge_orange",
      text: "घर्षण (f)",
      position: { x: 0.5, y: 0.35 },
    },
  ],

  steps: [
    {
      id: "step_1",
      title: "Auto moving on road",
      animations: [],
      labels: [],
      duration: 2000,
    },
    {
      id: "step_2",
      title: "Brakes applied",
      animations: [],
      labels: [],
      duration: 2000,
    },
    {
      id: "step_3",
      title: "Friction stops auto",
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

export default forceTOON;
