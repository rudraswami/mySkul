/**
 * professorDialogues.js
 * Phase 2.2: Professor dialogue system with Hinglish tips
 * 
 * Categories:
 * - Concept explanations
 * - Value change reactions
 * - Encouragement messages
 * - Exam tips
 * - Common mistakes warnings
 */

export const PROFESSOR_DIALOGUES = {
  // ============ PHYSICS ============
  force: {
    introduction: [
      "Dekho beta, Force = Push ya Pull! 💪",
      "Aaj Force seekhte hain - bahut important hai!",
      "Cricket mein bowling? Woh bhi Force hai!",
    ],
    
    valueReactions: {
      force: {
        high: [
          "Wah! Bahut strong force! 🔥",
          "Itna force? Ball udh jayegi!",
          "Powerful! Isse kehte hain force!",
        ],
        low: [
          "Thoda aur force lagao beta",
          "Kam force = Slow movement",
          "Force badhao, acceleration badhega!",
        ],
        increase: [
          "Dekho, force badha toh acceleration bhi badha!",
          "Yahi toh F=ma ka magic hai!",
          "More force → More speed! Simple!",
        ],
        decrease: [
          "Force kam kiya? Acceleration bhi gira!",
          "Dekho kaise slow ho gaya",
          "Less force = Less acceleration",
        ],
      },
      mass: {
        high: [
          "Heavy mass! Ab zyada force lagega",
          "Mass badha? Acceleration kam hoga",
          "Heavy object = Mushkil hilana!",
        ],
        low: [
          "Light object! Aasani se hilega",
          "Kam mass = Zyada acceleration",
          "Cricket ball light hai, isliye fast jaati hai!",
        ],
        increase: [
          "Mass badha toh acceleration gira - dekho!",
          "Heavy ho gaya, slow ho gaya!",
          "Yahi toh inertia hai beta!",
        ],
        decrease: [
          "Mass kam kiya? Ab fast hoga!",
          "Light object = Easy to accelerate",
          "Dekho kitna fast ho gaya!",
        ],
      },
      acceleration: {
        high: [
          "Bahut fast acceleration! 🚀",
          "Rocket jaisa speed-up!",
          "Itna acceleration? Impressive!",
        ],
        low: [
          "Slow acceleration - mass zyada hai kya?",
          "Thoda force badhao",
          "Acceleration kam hai, check karo values",
        ],
      },
    },
    
    examTips: [
      "JEE mein FBD zaroor banao! ✍️",
      "F=ma yaad rakho - har jagah kaam aayega",
      "Units check karo - Newton mein answer do",
      "Vector hai Force - direction bhi likho!",
    ],
    
    commonMistakes: [
      "⚠️ Mass aur Weight same nahi hai!",
      "⚠️ Force ka direction bhoolna mat!",
      "⚠️ g = 9.8 m/s², 10 nahi!",
    ],
    
    encouragement: [
      "Bahut accha! Keep it up! 🌟",
      "Samajh aa raha hai? Great!",
      "Tum kar sakte ho! 💪",
      "Physics easy hai, bas practice karo!",
    ],
  },
  
  motion: {
    introduction: [
      "Motion = Movement! Simple hai!",
      "Gadi chalti hai? Motion hai!",
      "Aaj equations of motion seekhenge!",
    ],
    
    valueReactions: {
      velocity: {
        high: [
          "Fast! Bahut speed hai! 💨",
          "Itni velocity? Rocket jaisa!",
          "Speed limit cross ho gayi! 😄",
        ],
        low: [
          "Slow motion chal raha hai",
          "Thoda speed badhao",
          "Turtle speed! 🐢",
        ],
      },
      distance: {
        high: [
          "Bahut door gaya! Long distance!",
          "Itna distance? Marathon hai kya?",
        ],
        low: [
          "Thoda hi gaya abhi",
          "Short distance - time kam tha",
        ],
      },
      time: {
        high: [
          "Bahut time laga!",
          "Slow journey thi",
        ],
        low: [
          "Jaldi pahunch gaya!",
          "Fast travel! ⚡",
        ],
      },
    },
    
    examTips: [
      "3 equations yaad rakho: v=u+at, s=ut+½at², v²=u²+2as",
      "Sign convention dhyan se - direction matters!",
      "Graph questions mein slope dekho!",
    ],
    
    commonMistakes: [
      "⚠️ Speed scalar hai, Velocity vector!",
      "⚠️ Distance aur Displacement alag hain!",
      "⚠️ Deceleration = Negative acceleration",
    ],
    
    encouragement: [
      "Motion master ban rahe ho! 🎯",
      "Equations yaad ho gaye? Superb!",
      "Practice karte raho! 📚",
    ],
  },
  
  gravity: {
    introduction: [
      "Newton ne apple gira dekha - Gravity discover kiya!",
      "Gravity = Earth ka pull! 🌍",
      "Sab kuch neeche kyun girta hai? Gravity!",
    ],
    
    valueReactions: {
      height: {
        high: [
          "Itni height se? Careful! 😱",
          "Bahut upar se gira!",
          "High drop = High impact!",
        ],
        low: [
          "Thodi height se gira",
          "Short fall - kam speed",
        ],
      },
      mass: {
        high: [
          "Heavy object! Same speed se girega",
          "Mass zyada, weight bhi zyada!",
        ],
        low: [
          "Light object - same acceleration!",
          "Mass kam, but g same rahega!",
        ],
      },
    },
    
    examTips: [
      "g = 9.8 m/s² (Earth surface pe)",
      "Free fall mein air resistance ignore karo",
      "Weight = mg, Mass ≠ Weight!",
    ],
    
    commonMistakes: [
      "⚠️ Vacuum mein feather aur ball same speed se girte hain!",
      "⚠️ g changes with altitude!",
      "⚠️ Weight Moon pe kam hoga, mass same!",
    ],
    
    encouragement: [
      "Gravity samajh aa gayi? Excellent! 🍎",
      "Newton proud hota tumse! 😊",
    ],
  },
  
  momentum: {
    introduction: [
      "Momentum = Mass × Velocity! 🎱",
      "Cricket ball fast hai, momentum zyada!",
      "Truck rokna mushkil - momentum zyada hai!",
    ],
    
    valueReactions: {
      momentum: {
        high: [
          "High momentum! Hard to stop! 🚛",
          "Bahut momentum hai!",
        ],
        low: [
          "Kam momentum - easy to stop",
          "Light aur slow = Low momentum",
        ],
      },
    },
    
    examTips: [
      "Conservation of momentum - collisions mein use karo!",
      "Impulse = Change in momentum = F×t",
      "Elastic vs Inelastic collision difference yaad rakho!",
    ],
    
    commonMistakes: [
      "⚠️ Momentum is a vector!",
      "⚠️ KE conserve nahi hoti inelastic collision mein!",
    ],
    
    encouragement: [
      "Momentum master! 🎯",
      "Collisions ab easy lagenge!",
    ],
  },
  
  energy: {
    introduction: [
      "Energy = Kaam karne ki capacity! ⚡",
      "KE + PE = Total Energy!",
      "Energy kabhi khatam nahi hoti, bas form badal jaati hai!",
    ],
    
    valueReactions: {
      kinetic: {
        high: [
          "High KE! Fast moving! 🏃",
          "Bahut kinetic energy!",
        ],
        low: [
          "Slow = Low KE",
          "KE kam hai",
        ],
      },
      potential: {
        high: [
          "High PE! Upar hai! 🏔️",
          "Potential energy stored hai!",
        ],
        low: [
          "Ground pe hai - PE kam",
          "Low height = Low PE",
        ],
      },
    },
    
    examTips: [
      "KE = ½mv², PE = mgh - formulas pakka yaad karo!",
      "Work-Energy theorem use karo!",
      "Conservative vs Non-conservative forces samjho!",
    ],
    
    commonMistakes: [
      "⚠️ Energy scalar hai, direction nahi!",
      "⚠️ Negative work bhi hota hai!",
    ],
    
    encouragement: [
      "Energy concepts clear! 💪",
      "Physics mein energy ho toh sab easy! ⚡",
    ],
  },
  
  // ============ CHEMISTRY ============
  atom: {
    introduction: [
      "Atom = Smallest particle! ⚛️",
      "Proton, Neutron, Electron - 3 particles!",
      "Nucleus mein proton aur neutron hain!",
    ],
    
    valueReactions: {
      electrons: {
        increase: [
          "Electron add hua - negative ion banega!",
          "More electrons = More negative!",
        ],
        decrease: [
          "Electron gaya - positive ion!",
          "Less electrons = Positive charge!",
        ],
      },
    },
    
    examTips: [
      "Atomic number = Protons = Electrons (neutral atom mein)",
      "Mass number = Protons + Neutrons",
      "Isotopes same protons, different neutrons!",
    ],
    
    commonMistakes: [
      "⚠️ Electron mass negligible hai!",
      "⚠️ Nucleus bahut chhota hai atom se!",
    ],
    
    encouragement: [
      "Atomic structure clear! ⚛️",
      "Chemistry ka base strong ho gaya!",
    ],
  },
  
  photosynthesis: {
    introduction: [
      "Plants ka khana banana = Photosynthesis! 🌱",
      "Sunlight + CO₂ + H₂O → Glucose + O₂",
      "Isliye plants green hain - Chlorophyll!",
    ],
    
    valueReactions: {
      light: {
        high: [
          "Bright light! Fast photosynthesis! ☀️",
          "Zyada light = Zyada food!",
        ],
        low: [
          "Kam light - slow process",
          "Plants ko sunlight chahiye!",
        ],
      },
    },
    
    examTips: [
      "Light reaction thylakoid mein, Dark reaction stroma mein!",
      "Equation: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂",
      "Chlorophyll absorbs red and blue light!",
    ],
    
    commonMistakes: [
      "⚠️ Dark reaction ko light bhi chahiye indirectly!",
      "⚠️ O₂ water se aata hai, CO₂ se nahi!",
    ],
    
    encouragement: [
      "Biology mein photosynthesis important hai! 🌿",
      "Plants ki respect karo! 😊",
    ],
  },
  
  cell: {
    introduction: [
      "Cell = Life ki basic unit! 🔬",
      "Plant cell mein cell wall, Animal mein nahi!",
      "Mitochondria = Powerhouse of cell!",
    ],
    
    examTips: [
      "Plant vs Animal cell difference yaad karo!",
      "Organelles aur unke functions important hain!",
      "Cell theory ke 3 points yaad rakho!",
    ],
    
    commonMistakes: [
      "⚠️ Prokaryotes mein nucleus nahi hota!",
      "⚠️ Vacuole plant cell mein bada hota hai!",
    ],
    
    encouragement: [
      "Cell biology clear! 🧬",
      "Microscope mein dekho toh aur maza aayega!",
    ],
  },
  
  // ============ MATHEMATICS ============
  quadratic: {
    introduction: [
      "Quadratic = x² wala equation! 📈",
      "ax² + bx + c = 0 - standard form!",
      "Graph parabola hota hai!",
    ],
    
    valueReactions: {
      discriminant: {
        positive: [
          "D > 0: Two real roots! ✅",
          "Parabola x-axis ko 2 jagah kategi!",
        ],
        zero: [
          "D = 0: One repeated root!",
          "Parabola x-axis ko touch karegi!",
        ],
        negative: [
          "D < 0: No real roots! ❌",
          "Parabola x-axis ko nahi kategi!",
        ],
      },
    },
    
    examTips: [
      "Discriminant = b² - 4ac - nature of roots!",
      "Sum of roots = -b/a, Product = c/a",
      "Quadratic formula: x = (-b ± √D)/2a",
    ],
    
    commonMistakes: [
      "⚠️ ± dono roots check karo!",
      "⚠️ a ≠ 0 hona chahiye quadratic ke liye!",
    ],
    
    encouragement: [
      "Quadratic equations easy hain! 📊",
      "Practice karo, JEE mein zaroor aayega!",
    ],
  },
  
  pythagoras: {
    introduction: [
      "a² + b² = c² - Pythagoras theorem! 📐",
      "Right angle triangle mein kaam aata hai!",
      "c = Hypotenuse (sabse lambi side)!",
    ],
    
    examTips: [
      "Sirf RIGHT ANGLE triangle mein valid!",
      "Common triplets: 3-4-5, 5-12-13, 8-15-17",
      "Converse bhi true hai - check karne ke liye!",
    ],
    
    commonMistakes: [
      "⚠️ Hypotenuse identify karna mat bhoolo!",
      "⚠️ Any triangle mein use mat karo!",
    ],
    
    encouragement: [
      "Geometry ka base strong! 📏",
      "Construction problems mein help karega!",
    ],
  },
  
  integral: {
    introduction: [
      "Integration = Reverse of differentiation! ∫",
      "Area under curve nikalta hai!",
      "∫xⁿdx = xⁿ⁺¹/(n+1) + C",
    ],
    
    examTips: [
      "Substitution method practice karo!",
      "By parts: ∫udv = uv - ∫vdu",
      "Definite integral mein limits lagao!",
    ],
    
    commonMistakes: [
      "⚠️ +C mat bhoolo indefinite mein!",
      "⚠️ Limits sahi order mein rakho!",
    ],
    
    encouragement: [
      "Calculus master ban rahe ho! 📈",
      "Integration se physics bhi easy hogi!",
    ],
  },
};

// Generic dialogues for any concept
export const GENERIC_DIALOGUES = {
  introduction: [
    "Aaj kuch naya seekhte hain! 📚",
    "Interesting topic hai yeh!",
    "Dhyan se dekho aur samjho!",
  ],
  
  encouragement: [
    "Bahut accha! Keep going! 🌟",
    "Samajh aa raha hai? Great job!",
    "Tum kar sakte ho! Believe in yourself! 💪",
    "Practice makes perfect! 📖",
    "Ek aur try karo!",
    "Almost there! Thoda aur!",
  ],
  
  examTips: [
    "Concepts clear karo, formulas yaad honge!",
    "Previous year papers solve karo!",
    "Time management important hai exam mein!",
  ],
  
  commonMistakes: [
    "⚠️ Question dhyan se padho!",
    "⚠️ Units check karo!",
    "⚠️ Sign conventions yaad rakho!",
  ],
  
  celebration: [
    "🎉 Excellent! You got it!",
    "🌟 Superb understanding!",
    "🏆 Champion! Well done!",
    "💯 Perfect! Keep it up!",
  ],
};

// Helper function to get random dialogue
export const getRandomDialogue = (dialogues) => {
  if (!dialogues || dialogues.length === 0) return null;
  return dialogues[Math.floor(Math.random() * dialogues.length)];
};

// Helper function to get dialogue for concept and situation
export const getDialogue = (concept, situation, subSituation = null) => {
  const conceptDialogues = PROFESSOR_DIALOGUES[concept?.toLowerCase()];
  
  if (!conceptDialogues) {
    // Fall back to generic
    const generic = GENERIC_DIALOGUES[situation];
    return getRandomDialogue(generic);
  }
  
  if (situation === 'valueReactions' && subSituation) {
    const [variable, reaction] = subSituation.split('.');
    const reactions = conceptDialogues.valueReactions?.[variable]?.[reaction];
    return getRandomDialogue(reactions);
  }
  
  const dialogues = conceptDialogues[situation];
  return getRandomDialogue(dialogues);
};

export default PROFESSOR_DIALOGUES;



