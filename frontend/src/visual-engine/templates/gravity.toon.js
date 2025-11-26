/**
 * Gravity Concept - TOON Template
 * Interactive visual for teaching Gravity (गुरुत्वाकर्षण)
 */

export const gravityTOON = {
  topic: "Gravity (गुरुत्वाकर्षण)",
  scene: "village",
  
  analogy: "आम पेड़ से क्यों गिरता है? Gravity खींचती है!",
  
  formula: {
    main: "F = G(m₁m₂)/r²",
    meaning: "Force of attraction between masses",
    breakdown: [
      { symbol: "F", name: "Gravitational Force", unit: "Newton (N)" },
      { symbol: "G", name: "Gravitational Constant", unit: "6.67×10⁻¹¹" },
      { symbol: "m₁, m₂", name: "Masses", unit: "kg" },
      { symbol: "r", name: "Distance", unit: "m" },
    ],
    example: "Earth pulls apple with F = mg = 0.1 × 10 = 1 N",
  },

  actors: [
    {
      id: "professor",
      type: "professor",
      position: { x: 0.08, y: 0.65 },
      initialState: "pointing",
      speech: "Newton का सेब!",
    },
  ],

  props: [
    {
      id: "tree",
      type: "tree",
      position: { x: 0.7, y: 0.5 },
    },
    {
      id: "mango",
      type: "mango",
      position: { x: 0.68, y: 0.25 },
      interactive: true,
    },
    {
      id: "gravity_badge",
      type: "badge_orange",
      text: "गुरुत्व (g)",
      position: { x: 0.4, y: 0.2 },
    },
    {
      id: "earth_label",
      type: "card",
      text: "g = 9.8 m/s²",
      position: { x: 0.4, y: 0.85 },
    },
  ],

  labels: [
    {
      id: "falling_label",
      text: "↓ Falling due to gravity",
      style: "badge",
      x: 60,
      y: 40,
      showOn: "step_2",
    },
  ],

  animations: [
    {
      id: "mango_fall",
      target: "mango",
      type: "projectile",
      force: "low",
      angle: 90,
      duration: 1500,
    },
    {
      id: "gravity_arrow",
      target: "gravity_vector",
      type: "vector_grow",
      direction: "down",
      magnitude: 60,
      duration: 800,
    },
  ],

  steps: [
    {
      id: "step_1",
      title: "Mango on tree",
      description: "Mango hangs on the tree branch",
      animations: [],
      labels: [],
      duration: 2000,
    },
    {
      id: "step_2",
      title: "Gravity pulls it down",
      description: "Earth's gravity attracts the mango",
      animations: ["gravity_arrow"],
      labels: ["falling_label"],
      duration: 2500,
    },
    {
      id: "step_3",
      title: "Mango falls!",
      description: "Acceleration due to gravity = 9.8 m/s²",
      animations: ["mango_fall"],
      labels: [],
      duration: 2000,
    },
  ],

  interactions: [
    {
      target: "mango",
      onTap: "highlight(gravity_arrow)",
      onLongPress: "showFormula()",
    },
    {
      target: "tree",
      onTap: "pulse(tree)",
    },
  ],
};

/**
 * Free Fall TOON Template
 */
export const freeFallTOON = {
  topic: "Free Fall (मुक्त पतन)",
  scene: "lab",
  
  analogy: "बिना हवा resistance के गिरना - सब साथ गिरते हैं!",
  
  formula: {
    main: "h = ½gt²",
    meaning: "Height fallen in time t",
    breakdown: [
      { symbol: "h", name: "Height", unit: "m" },
      { symbol: "g", name: "Acceleration (9.8)", unit: "m/s²" },
      { symbol: "t", name: "Time", unit: "s" },
    ],
  },

  actors: [
    {
      id: "professor",
      type: "professor",
      position: { x: 0.1, y: 0.6 },
    },
  ],

  props: [
    {
      id: "ball",
      type: "cricket_ball",
      position: { x: 0.4, y: 0.2 },
    },
  ],

  steps: [
    {
      id: "step_1",
      title: "Ball held up",
      animations: [],
      duration: 2000,
    },
    {
      id: "step_2",
      title: "Released!",
      animations: [],
      duration: 2500,
    },
  ],
};

export default gravityTOON;
