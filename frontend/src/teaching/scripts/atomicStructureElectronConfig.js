/**
 * Atomic Structure & Electron Configuration teaching script
 * Visualizes nucleus, shells (K, L, M), and electron filling with a slider.
 */

function polar(cx, cy, r, theta) {
  return [cx + r * Math.cos(theta), cy + r * Math.sin(theta)];
}

function buildScene() {
  const cx = 280; const cy = 150;
  const rK = 40, rL = 70, rM = 100, rN = 125;

  // Precompute ring guides and positions for up to 8 electrons
  const electronAnglesK = [0, Math.PI]; // 2
  const electronAnglesL = [0, Math.PI/2, Math.PI, 3*Math.PI/2, Math.PI/4, 3*Math.PI/4, 5*Math.PI/4, 7*Math.PI/4]; // up to 8
  const electronAnglesM = electronAnglesL; // reuse

  const positionsK = electronAnglesK.map(a => { const [x,y]=polar(cx,cy,rK,a); return {cx:x,cy:y}; });
  const positionsL = electronAnglesL.map(a => { const [x,y]=polar(cx,cy,rL,a); return {cx:x,cy:y}; });
  const positionsM = electronAnglesM.map(a => { const [x,y]=polar(cx,cy,rM,a); return {cx:x,cy:y}; });

  // Build electrons up to Z=20 with visibility tied to slider Z
  const electrons = [];
  const placeOnRing = (ring, indexInRing, ringCapacity) => {
    const rings = { K: rK, L: rL, M: rM, N: rN };
    const r = rings[ring] || rK;
    const angle = (2 * Math.PI * indexInRing) / ringCapacity;
    const [ex, ey] = polar(cx, cy, r, angle);
    return { cx: ex, cy: ey };
  };
  // Up to Ca (20): K 2, L 8, M 8, N 2 (4s)
  const capacities = { K: 2, L: 8, M: 8, N: 2 };
  const sequence = [];
  for (let i = 1; i <= capacities.K; i++) sequence.push({ ring: 'K', idx: i - 1, cap: capacities.K });
  for (let i = 1; i <= capacities.L; i++) sequence.push({ ring: 'L', idx: i - 1, cap: capacities.L });
  for (let i = 1; i <= capacities.M; i++) sequence.push({ ring: 'M', idx: i - 1, cap: capacities.M });
  for (let i = 1; i <= capacities.N; i++) sequence.push({ ring: 'N', idx: i - 1, cap: capacities.N });
  for (let i = 1; i <= 20; i++) {
    const s = sequence[i - 1];
    const pos = s ? placeOnRing(s.ring, s.idx, s.cap) : { cx: -999, cy: -999 };
    electrons.push({ id: `e${i}`, type: 'circle', r: 4, fill: '#0ea5e9', stroke: '#0369a1', cx: pos.cx, cy: pos.cy, visibleIf: { sliderId: 'Z', op: '>=', value: i } });
  }

  return {
    canvas: { width: 560, height: 300, background: '#ffffff' },
    elements: [
      // Nucleus
      { id: 'nucleus', type: 'circle', cx, cy, r: 18, fill: '#ffe0b2', stroke: '#fb8c00' },
      { id: 'label_nucleus', type: 'label', x: cx - 16, y: cy + 6, text: 'Nucleus' },
      // Shell rings
      { id: 'ring_K', type: 'circle', cx, cy, r: rK, fill: 'none', stroke: '#90caf9' },
      { id: 'ring_L', type: 'circle', cx, cy, r: rL, fill: 'none', stroke: '#a5d6a7' },
      { id: 'ring_M', type: 'circle', cx, cy, r: rM, fill: 'none', stroke: '#ffe082' },
      { id: 'ring_N', type: 'circle', cx, cy, r: rN, fill: 'none', stroke: '#f8bbd0' },
      { id: 'label_K', type: 'label', x: cx + rK + 8, y: cy, text: 'Shell 1 (K)' },
      { id: 'label_L', type: 'label', x: cx + rL + 8, y: cy, text: 'Shell 2 (L)' },
      { id: 'label_M', type: 'label', x: cx + rM + 8, y: cy, text: 'Shell 3 (M)' },
      { id: 'label_N', type: 'label', x: cx + rN + 8, y: cy, text: 'Shell 4 (N)' },
      // Legend
      { id: 'legend', type: 'rect', x: 410, y: 20, w: 130, h: 96, fill: '#ffffff', stroke: '#e5e7eb' },
      { id: 'legend_t', type: 'label', x: 418, y: 36, text: 'Electron filling' },
      { id: 'legend_k', type: 'label', x: 418, y: 52, text: 'K <= 2, inner' },
      { id: 'legend_l', type: 'label', x: 418, y: 66, text: 'L <= 8, next' },
      { id: 'legend_m', type: 'label', x: 418, y: 80, text: 'M <= 8' },
      { id: 'legend_n', type: 'label', x: 418, y: 94, text: 'N <= 2 (19–20)' },
      // Slider for principal quantum number and filling
      { id: 'n', type: 'slider', min: 1, max: 3, step: 1, value: 1, label: 'Energy Level n', x: 40, y: 262, w: 240, ui: false },
      // Slider for atomic number (Z)
      { id: 'Z', type: 'slider', min: 1, max: 20, step: 1, value: 10, label: 'Atomic Number Z', x: 300, y: 262, w: 240, ui: false },
      // Caption
      { id: 'caption_energy', type: 'label', x: 24, y: 24, text: 'Use Element/Z to fill electrons; n shows shell energy' },
      // Element selector bound to Z
      { id: 'el_select', type: 'select', x: 24, y: 218, w: 200, label: 'Element', targetSliderId: 'Z', ui: false, options: [
        { value: 1, label: 'H (1)' }, { value: 2, label: 'He (2)' }, { value: 3, label: 'Li (3)' }, { value: 4, label: 'Be (4)' }, { value: 5, label: 'B (5)' },
        { value: 6, label: 'C (6)' }, { value: 7, label: 'N (7)' }, { value: 8, label: 'O (8)' }, { value: 9, label: 'F (9)' }, { value: 10, label: 'Ne (10)' },
        { value: 11, label: 'Na (11)' }, { value: 12, label: 'Mg (12)' }, { value: 13, label: 'Al (13)' }, { value: 14, label: 'Si (14)' }, { value: 15, label: 'P (15)' },
        { value: 16, label: 'S (16)' }, { value: 17, label: 'Cl (17)' }, { value: 18, label: 'Ar (18)' }, { value: 19, label: 'K (19)' }, { value: 20, label: 'Ca (20)' },
      ]},
      // Info panel
      { id: 'info', type: 'rect', x: 410, y: 130, w: 130, h: 120, fill: '#ffffff', stroke: '#e5e7eb' },
      { id: 'info_t', type: 'label', x: 418, y: 146, text: 'Element Info' },
      // Symbol/Config labels per Z (visibleIf)
      ...[
        ['H', 'Hydrogen', '1s1'], ['He','Helium','1s2'], ['Li','Lithium','1s2 2s1'], ['Be','Beryllium','1s2 2s2'], ['B','Boron','1s2 2s2 2p1'],
        ['C','Carbon','1s2 2s2 2p2'], ['N','Nitrogen','1s2 2s2 2p3'], ['O','Oxygen','1s2 2s2 2p4'], ['F','Fluorine','1s2 2s2 2p5'], ['Ne','Neon','1s2 2s2 2p6'],
        ['Na','Sodium','[Ne] 3s1'], ['Mg','Magnesium','[Ne] 3s2'], ['Al','Aluminium','[Ne] 3s2 3p1'], ['Si','Silicon','[Ne] 3s2 3p2'], ['P','Phosphorus','[Ne] 3s2 3p3'],
        ['S','Sulfur','[Ne] 3s2 3p4'], ['Cl','Chlorine','[Ne] 3s2 3p5'], ['Ar','Argon','[Ne] 3s2 3p6'], ['K','Potassium','[Ar] 4s1'], ['Ca','Calcium','[Ar] 4s2']
      ].map((row, i) => ({ id: `sym_${i+1}`, type: 'label', x: 418, y: 164, text: `${row[0]} (${i+1}) — ${row[1]}`, visibleIf: { sliderId: 'Z', op: '==', value: i+1 } })),
      ...[
        ['H', 'Hydrogen', '1s1'], ['He','Helium','1s2'], ['Li','Lithium','1s2 2s1'], ['Be','Beryllium','1s2 2s2'], ['B','Boron','1s2 2s2 2p1'],
        ['C','Carbon','1s2 2s2 2p2'], ['N','Nitrogen','1s2 2s2 2p3'], ['O','Oxygen','1s2 2s2 2p4'], ['F','Fluorine','1s2 2s2 2p5'], ['Ne','Neon','1s2 2s2 2p6'],
        ['Na','Sodium','[Ne] 3s1'], ['Mg','Magnesium','[Ne] 3s2'], ['Al','Aluminium','[Ne] 3s2 3p1'], ['Si','Silicon','[Ne] 3s2 3p2'], ['P','Phosphorus','[Ne] 3s2 3p3'],
        ['S','Sulfur','[Ne] 3s2 3p4'], ['Cl','Chlorine','[Ne] 3s2 3p5'], ['Ar','Argon','[Ne] 3s2 3p6'], ['K','Potassium','[Ar] 4s1'], ['Ca','Calcium','[Ar] 4s2']
      ].map((row, i) => ({ id: `cfg_${i+1}`, type: 'label', x: 418, y: 182, text: row[2], visibleIf: { sliderId: 'Z', op: '==', value: i+1 } })),
      // Z display
      { id: 'z_lbl', type: 'label', x: 418, y: 200, text: 'Z =' },
      ...Array.from({length:20}, (_,i)=>({ id:`zval_${i+1}`, type:'label', x: 442, y: 200, text: String(i+1), visibleIf:{ sliderId:'Z', op:'==', value:i+1 } })),
      // Electrons (visibility driven by Z)
      ...electrons,
    ],
  };
}

export default function atomicStructure({ complexity = 'simple' } = {}) {
  const scene_json = buildScene();
  const interaction_flow = [
    { id: 'intro', highlight: ['nucleus', 'ring_K'], caption: 'Start with nucleus and first shell (K)' },
    { id: 'fill_k', highlight: ['e1', 'e2'], caption: 'Electrons fill K-shell (max 2)' },
    { id: 'fill_l', highlight: ['ring_L', 'e3', 'e4'], caption: 'Next, electrons enter L-shell (up to 8)' },
  ];

  const steps = [
    { id: 's1', title: "Let's start with the main idea", narration: 'Electrons occupy shells around the nucleus. Lower energy shells fill first.', flowId: 'intro' },
    { id: 's2', title: 'Notice the filling order', narration: 'K-shell fills up to 2 electrons; then L up to 8 (2n² rule).', flowId: 'fill_k' },
    { id: 's3', title: 'What it means', narration: 'As n increases, average distance grows — atoms get larger down groups.', flowId: 'fill_l', microCheck: { id: 'kmax', prompt: 'Max electrons in K shell?', options: [{id:'2',label:'2'},{id:'8',label:'8'}], correct: '2' } },
  ];

  const visualData = {
    type: 'story_scene',
    scene_json,
    interaction_flow,
    caption_text: 'Atomic Structure: Electrons fill inner shells first',
    generated: true,
    interactivity: { sliders: [{ id: 'n', min: 1, max: 3, step: 1 }], drop_accepts: [] },
  };

  return { steps, scene: visualData, meta: { topic: 'Atomic Structure & Electron Configuration', subject: 'Chemistry', complexity } };
}

