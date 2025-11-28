/**
 * 🧠 DRUV AI Natural Explanation Engine
 * 
 * Transforms AI responses into ChatGPT/Gemini-style structured,
 * engaging, human-friendly explanations with:
 * - Bullet points for lists
 * - Section headers with emojis
 * - Bold emphasis for key terms
 * - Conversational hooks
 * - Cognitive scaffolding
 * - Progressive reveal style
 */

import React from 'react';

// ============ SECTION TEMPLATES ============

const SECTION_CONFIGS = {
  definition: {
    emoji: '🧠',
    title: 'What is it?',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    borderColor: 'border-blue-200 dark:border-blue-800',
    textColor: 'text-blue-800 dark:text-blue-200'
  },
  simple: {
    emoji: '👉',
    title: 'In Simple Words',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    borderColor: 'border-green-200 dark:border-green-800',
    textColor: 'text-green-800 dark:text-green-200'
  },
  analogy: {
    emoji: '🍲',
    title: 'Real-Life Analogy',
    bgColor: 'bg-orange-50 dark:bg-orange-900/20',
    borderColor: 'border-orange-200 dark:border-orange-800',
    textColor: 'text-orange-800 dark:text-orange-200'
  },
  example: {
    emoji: '🏏',
    title: 'Example',
    bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    borderColor: 'border-purple-200 dark:border-purple-800',
    textColor: 'text-purple-800 dark:text-purple-200'
  },
  formula: {
    emoji: '⚙️',
    title: 'Formula',
    bgColor: 'bg-indigo-50 dark:bg-indigo-900/20',
    borderColor: 'border-indigo-200 dark:border-indigo-800',
    textColor: 'text-indigo-800 dark:text-indigo-200'
  },
  takeaway: {
    emoji: '🎯',
    title: 'Quick Takeaway',
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
    textColor: 'text-yellow-800 dark:text-yellow-200'
  },
  steps: {
    emoji: '📝',
    title: 'Step by Step',
    bgColor: 'bg-teal-50 dark:bg-teal-900/20',
    borderColor: 'border-teal-200 dark:border-teal-800',
    textColor: 'text-teal-800 dark:text-teal-200'
  },
  warning: {
    emoji: '⚠️',
    title: 'Common Mistake',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    borderColor: 'border-red-200 dark:border-red-800',
    textColor: 'text-red-800 dark:text-red-200'
  },
  tip: {
    emoji: '💡',
    title: 'Pro Tip',
    bgColor: 'bg-cyan-50 dark:bg-cyan-900/20',
    borderColor: 'border-cyan-200 dark:border-cyan-800',
    textColor: 'text-cyan-800 dark:text-cyan-200'
  }
};

// ============ TEXT ANALYSIS ============

/**
 * Detect the type of content for smart formatting
 */
export function detectContentType(text, question = '') {
  const q = (question || '').toLowerCase();
  const t = (text || '').toLowerCase();
  
  // Calculation/solving
  if (q.match(/(solve|calculate|find|evaluate|compute|integrate|differentiate)/)) {
    return 'calculation';
  }
  
  // Comparison
  if (q.match(/(difference|compare|vs|versus|distinguish|contrast)/)) {
    return 'comparison';
  }
  
  // Definition
  if (q.match(/(what is|define|meaning|definition|who is|who was)/)) {
    return 'definition';
  }
  
  // Process/how-it-works
  if (q.match(/(how does|how do|process|mechanism|steps|procedure)/)) {
    return 'process';
  }
  
  // Why/reasoning
  if (q.match(/(why|reason|cause|because)/)) {
    return 'reasoning';
  }
  
  // Example request
  if (q.match(/(example|for instance|show me|demonstrate)/)) {
    return 'example';
  }
  
  // Default explanation
  return 'explanation';
}

/**
 * Extract key terms from text for bolding
 */
export function extractKeyTerms(text, subject = '') {
  const keyTermPatterns = {
    physics: /\b(force|mass|acceleration|velocity|momentum|energy|gravity|friction|newton|joule|watt|pressure|temperature|heat|wave|frequency|amplitude|electric|magnetic|current|voltage|resistance|power)\b/gi,
    chemistry: /\b(atom|molecule|electron|proton|neutron|bond|covalent|ionic|reaction|acid|base|ph|oxidation|reduction|catalyst|compound|element|solution|concentration|mole)\b/gi,
    biology: /\b(cell|dna|rna|protein|enzyme|mitosis|meiosis|photosynthesis|respiration|gene|chromosome|nucleus|membrane|organism|species|evolution|mutation|hormone)\b/gi,
    mathematics: /\b(equation|function|derivative|integral|limit|slope|graph|variable|constant|polynomial|quadratic|linear|exponential|logarithm|sine|cosine|tangent|vector|matrix)\b/gi,
    general: /\b(important|key|critical|essential|fundamental|primary|main|significant|crucial)\b/gi
  };
  
  const patterns = subject && keyTermPatterns[subject.toLowerCase()] 
    ? [keyTermPatterns[subject.toLowerCase()], keyTermPatterns.general]
    : Object.values(keyTermPatterns);
  
  const terms = new Set();
  patterns.forEach(pattern => {
    const matches = text.match(pattern) || [];
    matches.forEach(m => terms.add(m.toLowerCase()));
  });
  
  return Array.from(terms);
}

/**
 * Detect if text contains a formula
 */
export function extractFormulas(text) {
  const formulas = [];
  
  // LaTeX formulas
  const latexMatches = text.match(/\\\[(.*?)\\\]|\\\((.*?)\\\)/g) || [];
  formulas.push(...latexMatches);
  
  // Simple equations like F = ma, E = mc²
  const simpleEquations = text.match(/[A-Z]\s*=\s*[^.]+/g) || [];
  formulas.push(...simpleEquations.filter(eq => eq.length < 50));
  
  return formulas;
}

/**
 * Split text into logical paragraphs/sections
 */
export function splitIntoSections(text) {
  if (!text) return [];
  
  // Split by double newlines or clear section breaks
  const rawSections = text.split(/\n\n+|\n(?=[A-Z•\-\d])/);
  
  return rawSections
    .map(s => s.trim())
    .filter(s => s.length > 10);
}

/**
 * Detect bullet points or list items
 */
export function extractBulletPoints(text) {
  const bullets = [];
  
  // Match various bullet formats
  const bulletPatterns = [
    /^[\-\•\*]\s*(.+)$/gm,           // - bullet or • bullet
    /^\d+[\.\)]\s*(.+)$/gm,          // 1. numbered or 1) numbered
    /^[a-z][\.\)]\s*(.+)$/gm,        // a. lettered
    /^(?:First|Second|Third|Next|Then|Finally)[,:]?\s*(.+)$/gim  // Transition words
  ];
  
  bulletPatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      bullets.push(match[1] || match[0]);
    }
  });
  
  return bullets;
}

/**
 * Detect analogies in text
 */
export function extractAnalogies(text) {
  const analogyPatterns = [
    /(?:like|similar to|just like|think of|imagine|picture|consider)\s+([^.]+)/gi,
    /(?:for example|for instance)[,:]?\s*([^.]+)/gi,
    /(?:it's as if|it's like)\s+([^.]+)/gi
  ];
  
  const analogies = [];
  analogyPatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      analogies.push(match[1].trim());
    }
  });
  
  return analogies;
}

// ============ FORMATTING ENGINE ============

/**
 * Main formatting function - transforms plain text into structured content
 */
export function formatExplanation(text, options = {}) {
  const {
    question = '',
    subject = '',
    includeEmojis = true,
    maxBullets = 6,
    style = 'conversational' // 'conversational', 'academic', 'exam-focused'
  } = options;
  
  if (!text || text.length < 20) return { type: 'simple', content: text };
  
  const contentType = detectContentType(text, question);
  const keyTerms = extractKeyTerms(text, subject);
  const formulas = extractFormulas(text);
  const bullets = extractBulletPoints(text);
  const analogies = extractAnalogies(text);
  const sections = splitIntoSections(text);
  
  return {
    type: contentType,
    originalText: text,
    keyTerms,
    formulas,
    bullets: bullets.slice(0, maxBullets),
    analogies,
    sections,
    formatted: createFormattedStructure(text, {
      contentType,
      keyTerms,
      formulas,
      bullets,
      analogies,
      sections,
      includeEmojis,
      style
    })
  };
}

/**
 * Create the formatted structure for rendering
 */
function createFormattedStructure(text, analysis) {
  const { contentType, keyTerms, formulas, bullets, analogies, sections, includeEmojis, style } = analysis;
  
  const structure = {
    hook: null,
    mainSections: [],
    takeaway: null
  };
  
  // Add conversational hook
  if (style === 'conversational' && sections.length > 0) {
    const hookPhrases = [
      "Let's break this down in a simple, fun way:",
      "Here's the deal:",
      "Okay, so this is pretty interesting!",
      "Let me explain this clearly:",
      "Think of it this way:"
    ];
    structure.hook = hookPhrases[Math.floor(Math.random() * hookPhrases.length)];
  }
  
  // Process sections based on content type
  switch (contentType) {
    case 'definition':
      structure.mainSections = formatDefinitionSections(sections, { keyTerms, analogies, formulas, includeEmojis });
      break;
    
    case 'calculation':
      structure.mainSections = formatCalculationSections(sections, { keyTerms, formulas, bullets, includeEmojis });
      break;
    
    case 'comparison':
      structure.mainSections = formatComparisonSections(sections, { keyTerms, includeEmojis });
      break;
    
    case 'process':
      structure.mainSections = formatProcessSections(sections, { keyTerms, bullets, includeEmojis });
      break;
    
    default:
      structure.mainSections = formatExplanationSections(sections, { keyTerms, analogies, formulas, bullets, includeEmojis });
  }
  
  // Add takeaway if we have enough content
  if (sections.length > 2) {
    structure.takeaway = generateTakeaway(text, keyTerms);
  }
  
  return structure;
}

/**
 * Format sections for definition-type content
 */
function formatDefinitionSections(sections, { keyTerms, analogies, formulas, includeEmojis }) {
  const result = [];
  
  // Definition section
  if (sections[0]) {
    result.push({
      type: 'definition',
      config: SECTION_CONFIGS.definition,
      content: highlightKeyTerms(sections[0], keyTerms),
      emoji: includeEmojis ? '🧠' : null
    });
  }
  
  // Simple explanation
  if (sections[1]) {
    result.push({
      type: 'simple',
      config: SECTION_CONFIGS.simple,
      content: highlightKeyTerms(sections[1], keyTerms),
      emoji: includeEmojis ? '👉' : null
    });
  }
  
  // Analogy if found
  if (analogies.length > 0) {
    result.push({
      type: 'analogy',
      config: SECTION_CONFIGS.analogy,
      content: analogies[0],
      emoji: includeEmojis ? '🍲' : null
    });
  }
  
  // Formula if present
  if (formulas.length > 0) {
    result.push({
      type: 'formula',
      config: SECTION_CONFIGS.formula,
      content: formulas[0],
      emoji: includeEmojis ? '⚙️' : null
    });
  }
  
  // Remaining sections
  sections.slice(2).forEach((section, i) => {
    if (!analogies.some(a => section.includes(a))) {
      result.push({
        type: 'content',
        content: highlightKeyTerms(section, keyTerms)
      });
    }
  });
  
  return result;
}

/**
 * Format sections for calculation-type content
 */
function formatCalculationSections(sections, { keyTerms, formulas, bullets, includeEmojis }) {
  const result = [];
  
  // Formula first
  if (formulas.length > 0) {
    result.push({
      type: 'formula',
      config: SECTION_CONFIGS.formula,
      content: formulas.join('\n'),
      emoji: includeEmojis ? '⚙️' : null
    });
  }
  
  // Steps
  if (bullets.length > 0) {
    result.push({
      type: 'steps',
      config: SECTION_CONFIGS.steps,
      content: bullets,
      isList: true,
      emoji: includeEmojis ? '📝' : null
    });
  }
  
  // Remaining explanation
  sections.forEach(section => {
    if (!formulas.some(f => section.includes(f)) && !bullets.some(b => section.includes(b))) {
      result.push({
        type: 'content',
        content: highlightKeyTerms(section, keyTerms)
      });
    }
  });
  
  return result;
}

/**
 * Format sections for comparison-type content
 */
function formatComparisonSections(sections, { keyTerms, includeEmojis }) {
  const result = [];
  
  sections.forEach((section, i) => {
    result.push({
      type: i === 0 ? 'definition' : 'content',
      config: i === 0 ? SECTION_CONFIGS.definition : null,
      content: highlightKeyTerms(section, keyTerms),
      emoji: i === 0 && includeEmojis ? '🔄' : null
    });
  });
  
  return result;
}

/**
 * Format sections for process-type content
 */
function formatProcessSections(sections, { keyTerms, bullets, includeEmojis }) {
  const result = [];
  
  // Introduction
  if (sections[0]) {
    result.push({
      type: 'definition',
      config: SECTION_CONFIGS.definition,
      content: highlightKeyTerms(sections[0], keyTerms),
      emoji: includeEmojis ? '🧠' : null
    });
  }
  
  // Steps
  if (bullets.length > 0) {
    result.push({
      type: 'steps',
      config: SECTION_CONFIGS.steps,
      content: bullets.map(b => highlightKeyTerms(b, keyTerms)),
      isList: true,
      emoji: includeEmojis ? '📝' : null
    });
  }
  
  // Additional sections
  sections.slice(1).forEach(section => {
    if (!bullets.some(b => section.includes(b))) {
      result.push({
        type: 'content',
        content: highlightKeyTerms(section, keyTerms)
      });
    }
  });
  
  return result;
}

/**
 * Format sections for general explanation content
 */
function formatExplanationSections(sections, { keyTerms, analogies, formulas, bullets, includeEmojis }) {
  const result = [];
  
  // Main explanation
  if (sections[0]) {
    result.push({
      type: 'definition',
      config: SECTION_CONFIGS.definition,
      content: highlightKeyTerms(sections[0], keyTerms),
      emoji: includeEmojis ? '🧠' : null
    });
  }
  
  // Analogy
  if (analogies.length > 0) {
    result.push({
      type: 'analogy',
      config: SECTION_CONFIGS.analogy,
      content: analogies[0],
      emoji: includeEmojis ? '🍲' : null
    });
  }
  
  // Example (second section often contains examples)
  if (sections[1] && sections[1].toLowerCase().includes('example')) {
    result.push({
      type: 'example',
      config: SECTION_CONFIGS.example,
      content: highlightKeyTerms(sections[1], keyTerms),
      emoji: includeEmojis ? '🏏' : null
    });
  }
  
  // Formula
  if (formulas.length > 0) {
    result.push({
      type: 'formula',
      config: SECTION_CONFIGS.formula,
      content: formulas[0],
      emoji: includeEmojis ? '⚙️' : null
    });
  }
  
  // Bullet points if any
  if (bullets.length > 2) {
    result.push({
      type: 'steps',
      config: SECTION_CONFIGS.steps,
      content: bullets.slice(0, 5),
      isList: true,
      emoji: includeEmojis ? '📝' : null
    });
  }
  
  // Remaining content
  const usedContent = new Set([
    ...analogies,
    ...formulas,
    ...bullets
  ]);
  
  sections.slice(1).forEach(section => {
    if (!Array.from(usedContent).some(used => section.includes(used))) {
      result.push({
        type: 'content',
        content: highlightKeyTerms(section, keyTerms)
      });
    }
  });
  
  return result;
}

/**
 * Highlight key terms in text with bold markers
 */
function highlightKeyTerms(text, keyTerms) {
  if (!text || keyTerms.length === 0) return text;
  
  let result = text;
  keyTerms.forEach(term => {
    const regex = new RegExp(`\\b(${term})\\b`, 'gi');
    result = result.replace(regex, '**$1**');
  });
  
  return result;
}

/**
 * Generate a quick takeaway from the content
 */
function generateTakeaway(text, keyTerms) {
  // Extract last sentence or create summary
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 10);
  
  if (sentences.length > 0) {
    const lastSentence = sentences[sentences.length - 1].trim();
    if (lastSentence.length < 150) {
      return highlightKeyTerms(lastSentence, keyTerms);
    }
  }
  
  // Create summary from key terms
  if (keyTerms.length > 0) {
    return `Key concepts: ${keyTerms.slice(0, 4).map(t => `**${t}**`).join(', ')}`;
  }
  
  return null;
}

// ============ REACT COMPONENTS ============

/**
 * Formatted Section Component
 */
export function FormattedSection({ section, index }) {
  const { type, config, content, emoji, isList } = section;
  
  if (!content) return null;
  
  // Plain content without special formatting
  if (!config) {
    return (
      <div className="text-gray-800 dark:text-gray-200 leading-relaxed mb-4">
        <FormattedText text={content} />
      </div>
    );
  }
  
  return (
    <div 
      className={`rounded-xl p-4 border mb-4 ${config.bgColor} ${config.borderColor}`}
      style={{ animationDelay: `${index * 100}ms` }}
    >
      {/* Section Header */}
      <div className="flex items-center space-x-2 mb-3">
        {emoji && <span className="text-xl">{emoji}</span>}
        <h4 className={`font-semibold ${config.textColor}`}>
          {config.title}
        </h4>
      </div>
      
      {/* Content */}
      {isList ? (
        <ul className="space-y-2">
          {(Array.isArray(content) ? content : [content]).map((item, i) => (
            <li key={i} className="flex items-start space-x-2 text-gray-800 dark:text-gray-200">
              <span className={`${config.textColor} font-bold`}>•</span>
              <span><FormattedText text={item} /></span>
            </li>
          ))}
        </ul>
      ) : (
        <div className="text-gray-800 dark:text-gray-200 leading-relaxed">
          <FormattedText text={content} />
        </div>
      )}
    </div>
  );
}

/**
 * Formatted Text Component - handles bold, italic, etc.
 */
export function FormattedText({ text }) {
  if (!text) return null;
  
  // Handle **bold** markers
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return (
            <strong key={i} className="font-bold text-gray-900 dark:text-white">
              {part.slice(2, -2)}
            </strong>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}

/**
 * Main Formatted Explanation Component
 */
export function FormattedExplanation({ text, question, subject, style = 'conversational' }) {
  const formatted = formatExplanation(text, { question, subject, style });
  
  if (formatted.type === 'simple') {
    return (
      <div className="text-gray-800 dark:text-gray-200 leading-relaxed">
        {text}
      </div>
    );
  }
  
  return (
    <div className="space-y-2">
      {/* Conversational Hook */}
      {formatted.formatted.hook && (
        <p className="text-gray-600 dark:text-gray-400 italic mb-4">
          {formatted.formatted.hook}
        </p>
      )}
      
      {/* Main Sections */}
      {formatted.formatted.mainSections.map((section, i) => (
        <FormattedSection key={i} section={section} index={i} />
      ))}
      
      {/* Takeaway */}
      {formatted.formatted.takeaway && (
        <div className="rounded-xl p-4 border bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xl">🎯</span>
            <h4 className="font-semibold text-yellow-800 dark:text-yellow-200">Quick Takeaway</h4>
          </div>
          <div className="text-gray-800 dark:text-gray-200">
            <FormattedText text={formatted.formatted.takeaway} />
          </div>
        </div>
      )}
    </div>
  );
}

export default {
  formatExplanation,
  detectContentType,
  extractKeyTerms,
  FormattedExplanation,
  FormattedSection,
  FormattedText
};

