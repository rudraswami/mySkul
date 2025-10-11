/**
 * Sentiment Analysis Utility
 * Lightweight JavaScript sentiment detection for emotion-aware AI Tutor
 */

// Simple sentiment keywords dictionary
const sentimentData = {
  positive: [
    'confident', 'easy', 'understand', 'got it', 'clear', 'makes sense',
    'helpful', 'good', 'great', 'awesome', 'perfect', 'excellent',
    'love', 'like', 'amazing', 'fantastic', 'wonderful', 'brilliant'
  ],
  negative: [
    'confused', 'difficult', 'hard', 'stuck', 'lost', 'frustrated',
    'don\'t understand', 'unclear', 'complicated', 'impossible',
    'hate', 'awful', 'terrible', 'worried', 'stressed', 'anxious'
  ],
  neutral: [
    'question', 'help', 'explain', 'what', 'how', 'why', 'when',
    'define', 'example', 'show', 'tell', 'describe'
  ],
  confusion: [
    'confused', 'don\'t get', 'unclear', 'lost', 'stuck', 'what does',
    'how does', 'why does', 'i don\'t understand', 'can you explain',
    'what is', 'help me'
  ],
  motivation: [
    'give up', 'quit', 'can\'t do', 'too hard', 'impossible',
    'never', 'always wrong', 'stupid', 'dumb', 'fail'
  ]
};

/**
 * Analyze sentiment from user input text
 * @param {string} text - User input text to analyze
 * @returns {Object} - Sentiment analysis result
 */
export function analyzeSentiment(text) {
  if (!text || typeof text !== 'string') {
    return {
      emotion: 'neutral',
      confidence: 0.5,
      needsMotivation: false,
      persona: 'hybrid'
    };
  }

  const lowerText = text.toLowerCase();
  const words = lowerText.split(/\s+/);
  
  let positiveScore = 0;
  let negativeScore = 0;
  let confusionScore = 0;
  let motivationNeeded = 0;
  
  // Count sentiment indicators
  words.forEach(word => {
    if (sentimentData.positive.some(pos => lowerText.includes(pos))) {
      positiveScore += 1;
    }
    if (sentimentData.negative.some(neg => lowerText.includes(neg))) {
      negativeScore += 1;
    }
    if (sentimentData.confusion.some(conf => lowerText.includes(conf))) {
      confusionScore += 1;
    }
    if (sentimentData.motivation.some(mot => lowerText.includes(mot))) {
      motivationNeeded += 1;
    }
  });

  // Determine primary emotion
  let emotion = 'neutral';
  let confidence = 0.5;
  let persona = 'hybrid';

  if (confusionScore > 0) {
    emotion = 'confused';
    confidence = Math.min(confusionScore / 3, 1);
    persona = 'professor'; // More explanation needed
  } else if (motivationNeeded > 0) {
    emotion = 'discouraged';
    confidence = Math.min(motivationNeeded / 2, 1);
    persona = 'mentor'; // More encouragement needed
  } else if (positiveScore > negativeScore) {
    emotion = 'positive';
    confidence = Math.min(positiveScore / 2, 1);
    persona = 'professor'; // Student is ready for deeper concepts
  } else if (negativeScore > positiveScore) {
    emotion = 'frustrated';
    confidence = Math.min(negativeScore / 2, 1);
    persona = 'mentor'; // Student needs support
  }

  return {
    emotion,
    confidence: Math.max(confidence, 0.3), // Minimum confidence
    needsMotivation: motivationNeeded > 0 || emotion === 'discouraged',
    persona,
    scores: {
      positive: positiveScore,
      negative: negativeScore,
      confusion: confusionScore,
      motivation: motivationNeeded
    }
  };
}

/**
 * Get persona configuration based on sentiment
 * @param {Object} sentiment - Sentiment analysis result
 * @returns {Object} - Persona configuration
 */
export function getPersonaConfig(sentiment) {
  const { persona, emotion, needsMotivation } = sentiment;
  
  const configs = {
    professor: {
      tone: 'academic',
      colorScheme: 'blue',
      greeting: 'Let\'s explore this concept together.',
      encouragement: 'You\'re asking the right questions!',
      gradient: 'from-blue-500 to-blue-600'
    },
    mentor: {
      tone: 'supportive',
      colorScheme: 'green',
      greeting: 'I\'m here to help you succeed!',
      encouragement: 'You\'ve got this! Let\'s break it down step by step.',
      gradient: 'from-green-500 to-green-600'
    },
    hybrid: {
      tone: 'balanced',
      colorScheme: 'purple',
      greeting: 'Let\'s learn this together!',
      encouragement: 'Every expert was once a beginner.',
      gradient: 'from-purple-500 to-purple-600'
    }
  };

  const config = configs[persona] || configs.hybrid;
  
  // Add emotion-specific modifications
  if (needsMotivation) {
    config.supportMessage = 'Remember: progress over perfection! 🌟';
  }
  
  if (emotion === 'confused') {
    config.approachMessage = 'Let me explain this in a different way...';
  }

  return config;
}

/**
 * Generate motivational micro-copy based on sentiment
 * @param {Object} sentiment - Sentiment analysis result
 * @returns {string} - Motivational message
 */
export function getMotivationalMessage(sentiment) {
  const { emotion, needsMotivation } = sentiment;
  
  const messages = {
    positive: [
      "You're on the right track! 🎯",
      "Great thinking! Let's dive deeper.",
      "You're making excellent progress!"
    ],
    confused: [
      "No worries, let's clarify this together! 💡",
      "Great question! Let me break this down.",
      "Confusion means you're learning - let's solve this!"
    ],
    frustrated: [
      "I understand this is challenging. Let's take it step by step. 🤝",
      "Every expert struggled with this once. You're not alone! 💪",
      "Let's approach this differently - you've got this!"
    ],
    discouraged: [
      "Hey, you're braver than you believe! Let's conquer this together. 🌟",
      "Small steps lead to big victories. Let's start simple. ✨",
      "Your effort matters more than perfection. Keep going! 🚀"
    ],
    neutral: [
      "Let's explore this concept together! 📚",
      "Ready to learn something new? 🎓",
      "I'm here to guide you through this! 🗺️"
    ]
  };

  const emotionMessages = messages[emotion] || messages.neutral;
  const randomIndex = Math.floor(Math.random() * emotionMessages.length);
  
  return emotionMessages[randomIndex];
}