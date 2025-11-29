/**
 * Indian Context Utilities
 * Cultural adaptations for Indian students
 */

/**
 * Region-specific props mapping
 * Different Indian regions have different common objects
 */
export const REGIONAL_PROPS = {
  north: {
    vehicle: 'auto_rickshaw',
    fruit: 'mango',
    drink: 'chai',
    food: 'paratha',
    sport: 'cricket',
    container: 'matka',
  },
  south: {
    vehicle: 'auto_rickshaw', // Or 'cycle_rickshaw' in some areas
    fruit: 'coconut',
    drink: 'filter_coffee',
    food: 'dosa',
    sport: 'cricket',
    container: 'brass_vessel',
  },
  east: {
    vehicle: 'auto_rickshaw',
    fruit: 'mango',
    drink: 'chai',
    food: 'rasgulla',
    sport: 'football',
    container: 'terracotta_pot',
  },
  west: {
    vehicle: 'auto_rickshaw',
    fruit: 'chikoo',
    drink: 'chai',
    food: 'dhokla',
    sport: 'cricket',
    container: 'brass_lota',
  },
};

/**
 * Hinglish phrases for common physics concepts
 */
export const HINGLISH_PHRASES = {
  // Force
  'force': 'बल (Force)',
  'push': 'धक्का (Push)',
  'pull': 'खींचना (Pull)',
  'more force': 'ज़्यादा बल',
  'less force': 'कम बल',
  'applied force': 'लगाया गया बल',
  
  // Motion
  'motion': 'गति (Motion)',
  'velocity': 'वेग (Velocity)',
  'speed': 'गति/रफ़्तार',
  'acceleration': 'त्वरण (Acceleration)',
  'at rest': 'रुका हुआ',
  'moving': 'चल रहा है',
  'fast': 'तेज़',
  'slow': 'धीरे',
  
  // Gravity
  'gravity': 'गुरुत्वाकर्षण',
  'falling': 'गिर रहा है',
  'weight': 'भार (Weight)',
  'mass': 'द्रव्यमान (Mass)',
  'earth': 'पृथ्वी',
  'moon': 'चाँद',
  
  // General
  'formula': 'सूत्र (Formula)',
  'remember': 'याद रखो',
  'example': 'उदाहरण',
  'key insight': 'महत्वपूर्ण बात',
  'next': 'अगला',
  'previous': 'पिछला',
  'tap to continue': 'आगे बढ़ने के लिए टैप करें',
};

/**
 * Indian analogies for physics concepts
 */
export const INDIAN_ANALOGIES = {
  force: [
    {
      scenario: 'cricket',
      text: 'Bowler जितना ज़ोर से फेंकता है, ball उतनी तेज़ जाती है!',
      props: ['bowler', 'cricket_ball', 'stumps'],
    },
    {
      scenario: 'auto',
      text: 'Auto का accelerator दबाओ, speed बढ़ती है - यही Force है!',
      props: ['auto_rickshaw', 'road'],
    },
    {
      scenario: 'kite',
      text: 'पतंग को हवा का Force ऊपर उठाता है, धागे का Force नीचे खींचता है',
      props: ['kite', 'string', 'wind'],
    },
  ],
  
  motion: [
    {
      scenario: 'traffic',
      text: 'Signal हरा होने पर गाड़ियाँ धीरे-धीरे तेज़ होती हैं - Acceleration!',
      props: ['auto_rickshaw', 'traffic_signal', 'road'],
    },
    {
      scenario: 'train',
      text: 'Train जब station छोड़ती है, पहले धीरे फिर तेज़ - v बढ़ता है!',
      props: ['train', 'platform'],
    },
  ],
  
  gravity: [
    {
      scenario: 'mango',
      text: 'पेड़ से आम टपकता है - धरती खींचती है! यही Gravity है!',
      props: ['tree', 'mango', 'ground'],
    },
    {
      scenario: 'ball',
      text: 'ऊपर फेंकी ball वापस आती है - Gravity नीचे खींचती है',
      props: ['ball', 'person'],
    },
  ],
  
  friction: [
    {
      scenario: 'carrom',
      text: 'Carrom board पर powder डालते हो - Friction कम होता है, striker तेज़ जाता है!',
      props: ['carrom_board', 'striker', 'powder'],
    },
    {
      scenario: 'slippers',
      text: 'गीले फ़र्श पर फिसल जाते हो - Friction कम है!',
      props: ['floor', 'water', 'person'],
    },
  ],
};

/**
 * Get regional context
 */
export function getIndianContext(region = 'north') {
  return {
    props: REGIONAL_PROPS[region] || REGIONAL_PROPS['north'],
    hinglish: HINGLISH_PHRASES,
    analogies: INDIAN_ANALOGIES,
    region,
  };
}

/**
 * Get appropriate analogy for concept
 */
export function getAnalogy(concept, preferredScenario = null) {
  const analogies = INDIAN_ANALOGIES[concept.toLowerCase()] || [];
  
  if (preferredScenario) {
    const preferred = analogies.find(a => a.scenario === preferredScenario);
    if (preferred) return preferred;
  }
  
  // Return random analogy
  return analogies[Math.floor(Math.random() * analogies.length)] || null;
}

/**
 * Translate text to Hinglish
 */
export function toHinglish(text) {
  let result = text;
  
  Object.entries(HINGLISH_PHRASES).forEach(([english, hinglish]) => {
    const regex = new RegExp(`\\b${english}\\b`, 'gi');
    result = result.replace(regex, hinglish);
  });
  
  return result;
}

/**
 * Get professor speech for concept
 */
export function getProfessorSpeech(concept, step = 0) {
  const speeches = {
    force: [
      'Force matlab dhakka ya kheenchna!',
      'Dekho jab force lagta hai...',
      'F = m × a - yaad rakho!',
    ],
    motion: [
      'Motion matlab jagah badalna!',
      'Speed aur velocity alag hain...',
      'v = u + at - yehi formula hai!',
    ],
    gravity: [
      'Gravity kya hai? Dekho...',
      'Sab cheezein neeche kyun girti hain?',
      'g = 9.8 m/s² - yaad rakho!',
    ],
  };
  
  const conceptSpeeches = speeches[concept.toLowerCase()] || ['Let me explain...'];
  return conceptSpeeches[step % conceptSpeeches.length];
}

export default {
  getIndianContext,
  getAnalogy,
  toHinglish,
  getProfessorSpeech,
  REGIONAL_PROPS,
  HINGLISH_PHRASES,
  INDIAN_ANALOGIES,
};









