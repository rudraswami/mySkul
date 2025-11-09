/**
 * Covalent Bonding teaching script
 * Professor-style sequence with motion-aligned narration and cause-effect cues.
 * Produces a light-weight story_scene flow driven by DynamicSceneComposer.
 */

function buildBaseScene() {
  // Minimal canvas with two atoms, electrons, and an energy arrow that can drop
  return {
    canvas: { width: 560, height: 300, background: '#ffffff' },
    palette: { saffron: '#FF9933', green: '#138808', gold: '#FFD700' },
    elements: [
      { id: 'atom_left', type: 'circle', cx: 180, cy: 160, r: 34, fill: '#e3f2fd', stroke: '#1976d2' },
      { id: 'atom_right', type: 'circle', cx: 380, cy: 160, r: 34, fill: '#e8f5e9', stroke: '#2e7d32' },
      // valence electrons
      { id: 'e_l1', type: 'circle', cx: 160, cy: 130, r: 5, fill: '#1976d2' },
      { id: 'e_l2', type: 'circle', cx: 200, cy: 130, r: 5, fill: '#1976d2' },
      { id: 'e_r1', type: 'circle', cx: 360, cy: 130, r: 5, fill: '#2e7d32' },
      { id: 'e_r2', type: 'circle', cx: 400, cy: 130, r: 5, fill: '#2e7d32' },
      // energy arrow (bind width to slider for effect)
      { id: 'energy_axis', type: 'rect', x: 30, y: 40, w: 6, h: 200, fill: '#eee', stroke: '#bbb' },
      { id: 'energy_arrow', type: 'arrow', from: [34, 60], to: [34, 220], color: '#ef6c00' },
      { id: 'energy_label', type: 'label', x: 20, y: 35, text: 'Energy' },
      // shared electron pair placeholder
      { id: 'bond_e_pair', type: 'rect', x: 278, y: 150, w: 4, h: 20, fill: '#90caf9', stroke: '#90caf9' },
      // cultural pattern (subtle background motif)
      { id: 'rangoli', type: 'pattern', x: 460, y: 200, w: 80, h: 80, style: 'rangoli' },
    ],
  };
}

export default function covalentBonding({ complexity = 'simple' } = {}) {
  const scene_json = buildBaseScene();

  // interaction_flow frames: which elements to highlight and in what order
  const interaction_flow = [
    {
      id: 'intro_atoms',
      highlight: ['atom_left', 'atom_right'],
      caption: 'Two atoms approach each other',
    },
    {
      id: 'valence_focus',
      highlight: ['e_l1', 'e_l2', 'e_r1', 'e_r2'],
      caption: 'Focus on valence electrons',
    },
    {
      id: 'share_pair',
      highlight: ['bond_e_pair'],
      caption: 'They share electrons → covalent bond',
    },
    {
      id: 'energy_drop',
      highlight: ['energy_arrow', 'energy_label'],
      caption: 'Energy drops → stability increases',
    },
  ];

  const steps = [
    {
      id: 'step1',
      title: "Let's start with the main idea",
      narration:
        'Covalent bonding happens when atoms share electron pairs to become more stable.',
      flowId: 'intro_atoms',
    },
    {
      id: 'step2',
      title: 'Notice the cause and effect',
      narration:
        'As atoms approach, valence electrons are positioned to pair and reduce potential energy.',
      flowId: 'valence_focus',
    },
    {
      id: 'step3',
      title: 'Motion aligned with meaning',
      narration: 'Sharing electrons forms a bond. Think of it like a handshake of stability.',
      flowId: 'share_pair',
    },
    {
      id: 'step4',
      title: 'Real-life anchor',
      narration:
        'When energy drops, stability rises. Like teamwork during a festival—shared effort lowers strain.',
      flowId: 'energy_drop',
      microCheck: {
        id: 'bond_stability_check',
        prompt: 'What happens to stability when bond energy drops?',
        options: [
          { id: 'up', label: 'It decreases' },
          { id: 'down', label: 'It increases' },
        ],
        correct: 'down',
      },
    },
  ];

  // Complexity scaling: advanced adds 2 micro-layers (interaction and reflection)
  if (complexity === 'advanced') {
    steps.splice(2, 0, {
      id: 'step2b',
      title: 'Advanced: repulsion vs attraction',
      narration:
        'Balance electrostatic repulsion and attraction. Net effect favors sharing at optimal distance.',
      flowId: 'valence_focus',
    });
    steps.push({
      id: 'reflect',
      title: 'Reflect',
      narration: 'Why does shared electron density hold atoms together?',
      flowId: 'share_pair',
    });
  }

  const visualData = {
    type: 'story_scene',
    scene_json,
    interaction_flow,
    caption_text: 'Covalent Bonding: Energy ↓ → Stability ↑',
    generated: true,
    interactivity: {
      sliders: [{ id: 'energy', from: 0, to: 1 }],
      drop_accepts: [],
    },
  };

  return { steps, scene: visualData, meta: { topic: 'Covalent Bonding', subject: 'Chemistry', complexity } };
}

