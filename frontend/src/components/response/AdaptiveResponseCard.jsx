/**
 * 🎯 ADAPTIVE RESPONSE CARD V2.0
 * ==============================
 * 
 * Revolutionary AI response rendering that makes students ADDICTED to learning.
 * 
 * Philosophy:
 * - Progressive disclosure (reveal step by step)
 * - Gamification (XP, progress, achievements)
 * - Memory hooks (mnemonics, stories, analogies)
 * - Exam warrior mode (marks, topper tips, common mistakes)
 * - Indian context (relatable examples)
 * - Emotional connection (friendly, encouraging)
 * 
 * Response Sections:
 * 1. 🎬 Hook - Grab attention in 3 seconds
 * 2. 💡 Core Concept - "In simple words..."
 * 3. 🎯 Exam Focus - Marks breakdown, important points
 * 4. 🧠 Memory Palace - Mnemonics, analogies, stories
 * 5. 🏏 Indian Context - Relatable examples
 * 6. ⚠️ Common Mistakes - "90% students miss this"
 * 7. 🏆 Topper Tips - "AIR 124 says..."
 * 8. ✅ Quick Recall - Flashcard summary
 * 9. 🎮 XP & Progress - Gamification elements
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Section type icons and colors
const SECTION_STYLES = {
  hook: {
    icon: '🎬',
    color: '#FF9933',
    bgColor: '#FFF7ED',
    label: 'Quick Hook',
  },
  definition: {
    icon: '💡',
    color: '#3B82F6',
    bgColor: '#EFF6FF',
    label: 'In Simple Words',
  },
  formula: {
    icon: '📐',
    color: '#8B5CF6',
    bgColor: '#FAF5FF',
    label: 'Key Formula',
  },
  examFocus: {
    icon: '🎯',
    color: '#EF4444',
    bgColor: '#FEF2F2',
    label: 'Exam Focus',
  },
  memory: {
    icon: '🧠',
    color: '#10B981',
    bgColor: '#ECFDF5',
    label: 'Memory Hook',
  },
  indianContext: {
    icon: '🇮🇳',
    color: '#FF9933',
    bgColor: '#FFFBEB',
    label: 'Desi Example',
  },
  commonMistakes: {
    icon: '⚠️',
    color: '#F59E0B',
    bgColor: '#FFFBEB',
    label: 'Common Mistakes',
  },
  topperTips: {
    icon: '🏆',
    color: '#6366F1',
    bgColor: '#EEF2FF',
    label: 'Topper Secret',
  },
  steps: {
    icon: '📋',
    color: '#06B6D4',
    bgColor: '#ECFEFF',
    label: 'Step by Step',
  },
  quickRecall: {
    icon: '⚡',
    color: '#EC4899',
    bgColor: '#FDF2F8',
    label: 'Quick Recall',
  },
};

// Animated section wrapper
const ResponseSection = ({ type, children, delay = 0, isExpanded = true }) => {
  const [expanded, setExpanded] = useState(isExpanded);
  const style = SECTION_STYLES[type] || SECTION_STYLES.definition;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="mb-4"
    >
      <div
        className="rounded-xl overflow-hidden border-2 transition-all"
        style={{ borderColor: style.color + '40', backgroundColor: style.bgColor }}
      >
        {/* Section header */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">{style.icon}</span>
            <span className="font-bold text-sm" style={{ color: style.color }}>
              {style.label}
            </span>
          </div>
          <motion.span
            animate={{ rotate: expanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
            className="text-gray-400"
          >
            ▼
          </motion.span>
        </button>

        {/* Section content */}
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="px-4 pb-4"
            >
              {children}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

// Hook section - Grabs attention
const HookSection = ({ text, emoji = '🎯' }) => (
  <ResponseSection type="hook" delay={0}>
    <div className="flex items-start gap-3 bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg p-4">
      <span className="text-3xl">{emoji}</span>
      <div>
        <p className="text-lg font-medium text-gray-800 leading-relaxed">{text}</p>
        <p className="text-sm text-orange-600 mt-2 font-medium">
          ⏱️ 3-minute read • 💡 Easy to understand
        </p>
      </div>
    </div>
  </ResponseSection>
);

// Definition section - Core concept
const DefinitionSection = ({ title, content, hindiTerm = '' }) => (
  <ResponseSection type="definition" delay={0.1}>
    <div className="space-y-3">
      <h3 className="text-lg font-bold text-blue-800 flex items-center gap-2">
        {title}
        {hindiTerm && (
          <span className="text-sm font-normal text-blue-500 bg-blue-100 px-2 py-1 rounded">
            ({hindiTerm})
          </span>
        )}
      </h3>
      <p className="text-gray-700 leading-relaxed">{content}</p>
    </div>
  </ResponseSection>
);

// Formula section with highlight
const FormulaSection = ({ formula, explanation, marks = 0 }) => (
  <ResponseSection type="formula" delay={0.2}>
    <div className="space-y-3">
      {/* Formula display */}
      <div className="bg-gradient-to-r from-purple-100 to-violet-100 rounded-lg p-4 text-center">
        <p className="text-xl font-mono font-bold text-purple-800">{formula}</p>
      </div>
      
      {/* Explanation */}
      <p className="text-gray-600 text-sm">{explanation}</p>
      
      {/* Marks indicator */}
      {marks > 0 && (
        <div className="flex items-center gap-2 bg-red-50 text-red-700 px-3 py-2 rounded-lg text-sm font-medium">
          <span>🎯</span>
          <span>Worth {marks} marks in exams!</span>
        </div>
      )}
    </div>
  </ResponseSection>
);

// Exam Focus section
const ExamFocusSection = ({ points, marksBreakdown = null }) => (
  <ResponseSection type="examFocus" delay={0.3}>
    <div className="space-y-4">
      {/* Marks breakdown */}
      {marksBreakdown && (
        <div className="bg-red-50 rounded-lg p-3 border border-red-200">
          <p className="text-sm font-bold text-red-700 mb-2">📊 Marks Distribution:</p>
          <div className="flex flex-wrap gap-2">
            {marksBreakdown.map((item, i) => (
              <span
                key={i}
                className="bg-white text-red-600 px-3 py-1 rounded-full text-sm font-medium border border-red-200"
              >
                {item.topic}: {item.marks}M
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Important points */}
      <div className="space-y-2">
        <p className="text-sm font-bold text-red-700">🎯 Must Remember:</p>
        {points.map((point, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 + i * 0.1 }}
            className="flex items-start gap-2 bg-white rounded-lg p-3 border border-red-100"
          >
            <span className="bg-red-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
              {i + 1}
            </span>
            <p className="text-gray-700 text-sm">{point}</p>
          </motion.div>
        ))}
      </div>
    </div>
  </ResponseSection>
);

// Memory Hook section - Mnemonics, analogies
const MemorySection = ({ mnemonic, analogy, story = null }) => (
  <ResponseSection type="memory" delay={0.4}>
    <div className="space-y-4">
      {/* Mnemonic */}
      {mnemonic && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border-l-4 border-green-500">
          <p className="text-sm font-bold text-green-700 mb-1">🧠 Memory Trick:</p>
          <p className="text-green-800 font-medium text-lg">{mnemonic}</p>
        </div>
      )}

      {/* Analogy */}
      {analogy && (
        <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded-lg p-4">
          <p className="text-sm font-bold text-teal-700 mb-1">💭 Think of it like:</p>
          <p className="text-gray-700">{analogy}</p>
        </div>
      )}

      {/* Story */}
      {story && (
        <div className="bg-gradient-to-r from-emerald-50 to-green-50 rounded-lg p-4">
          <p className="text-sm font-bold text-emerald-700 mb-1">📖 Story Time:</p>
          <p className="text-gray-700 italic">{story}</p>
        </div>
      )}
    </div>
  </ResponseSection>
);

// Indian Context section
const IndianContextSection = ({ examples }) => (
  <ResponseSection type="indianContext" delay={0.5}>
    <div className="space-y-3">
      {examples.map((example, i) => (
        <div
          key={i}
          className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg p-4 border-l-4 border-orange-400"
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">{example.emoji || '🇮🇳'}</span>
            <div>
              <p className="font-medium text-orange-800">{example.title}</p>
              <p className="text-gray-600 text-sm mt-1">{example.description}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  </ResponseSection>
);

// Common Mistakes section
const CommonMistakesSection = ({ mistakes }) => (
  <ResponseSection type="commonMistakes" delay={0.6}>
    <div className="space-y-3">
      <p className="text-sm text-amber-700 font-medium">
        ⚠️ 90% students lose marks here!
      </p>
      {mistakes.map((mistake, i) => (
        <div
          key={i}
          className="bg-white rounded-lg p-3 border border-amber-200 flex items-start gap-3"
        >
          <span className="text-red-500 text-xl">✗</span>
          <div className="flex-1">
            <p className="text-red-600 font-medium text-sm line-through">{mistake.wrong}</p>
            <p className="text-green-600 font-medium text-sm mt-1">✓ {mistake.correct}</p>
          </div>
        </div>
      ))}
    </div>
  </ResponseSection>
);

// Topper Tips section
const TopperTipsSection = ({ tips }) => (
  <ResponseSection type="topperTips" delay={0.7}>
    <div className="space-y-3">
      {tips.map((tip, i) => (
        <div
          key={i}
          className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-200"
        >
          <div className="flex items-start gap-3">
            <div className="bg-indigo-500 text-white w-10 h-10 rounded-full flex items-center justify-center text-lg">
              🏆
            </div>
            <div>
              <p className="text-indigo-800 font-medium">{tip.content}</p>
              {tip.source && (
                <p className="text-indigo-500 text-sm mt-1">— {tip.source}</p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  </ResponseSection>
);

// Steps section - Progressive reveal
const StepsSection = ({ steps, title = 'Step by Step' }) => {
  const [revealedSteps, setRevealedSteps] = useState(1);

  return (
    <ResponseSection type="steps" delay={0.3}>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <p className="font-bold text-cyan-700">{title}</p>
          <span className="text-sm text-cyan-500">
            {revealedSteps}/{steps.length} steps
          </span>
        </div>

        {steps.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ 
              opacity: i < revealedSteps ? 1 : 0.3,
              x: 0 
            }}
            transition={{ delay: i * 0.1 }}
            className={`rounded-lg p-4 border-2 transition-all ${
              i < revealedSteps
                ? 'bg-cyan-50 border-cyan-300'
                : 'bg-gray-50 border-gray-200'
            }`}
          >
            <div className="flex items-start gap-3">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                  i < revealedSteps
                    ? 'bg-cyan-500 text-white'
                    : 'bg-gray-300 text-gray-500'
                }`}
              >
                {i + 1}
              </div>
              <div className="flex-1">
                <p className="font-medium text-gray-800">{step.title}</p>
                {i < revealedSteps && (
                  <p className="text-gray-600 text-sm mt-1">{step.content}</p>
                )}
              </div>
            </div>
          </motion.div>
        ))}

        {revealedSteps < steps.length && (
          <button
            onClick={() => setRevealedSteps(prev => Math.min(prev + 1, steps.length))}
            className="w-full py-3 bg-cyan-500 text-white rounded-lg font-medium hover:bg-cyan-600 transition-colors flex items-center justify-center gap-2"
          >
            <span>Show Next Step</span>
            <span>→</span>
          </button>
        )}
      </div>
    </ResponseSection>
  );
};

// Quick Recall section - Flashcard style
const QuickRecallSection = ({ cards }) => {
  const [currentCard, setCurrentCard] = useState(0);
  const [flipped, setFlipped] = useState(false);

  return (
    <ResponseSection type="quickRecall" delay={0.8}>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="font-bold text-pink-700">Quick Recall Cards</p>
          <span className="text-sm text-pink-500">
            {currentCard + 1}/{cards.length}
          </span>
        </div>

        {/* Flashcard */}
        <motion.div
          className="relative h-40 cursor-pointer"
          onClick={() => setFlipped(!flipped)}
        >
          <motion.div
            className="absolute inset-0 rounded-xl p-6 flex items-center justify-center text-center"
            animate={{ rotateY: flipped ? 180 : 0 }}
            transition={{ duration: 0.4 }}
            style={{
              background: flipped
                ? 'linear-gradient(135deg, #10B981, #059669)'
                : 'linear-gradient(135deg, #EC4899, #DB2777)',
              backfaceVisibility: 'hidden',
            }}
          >
            <p className="text-white font-medium text-lg">
              {flipped ? '' : cards[currentCard].question}
            </p>
          </motion.div>
          <motion.div
            className="absolute inset-0 rounded-xl p-6 flex items-center justify-center text-center"
            initial={{ rotateY: 180 }}
            animate={{ rotateY: flipped ? 0 : 180 }}
            transition={{ duration: 0.4 }}
            style={{
              background: 'linear-gradient(135deg, #10B981, #059669)',
              backfaceVisibility: 'hidden',
            }}
          >
            <p className="text-white font-medium text-lg">
              {flipped ? cards[currentCard].answer : ''}
            </p>
          </motion.div>
        </motion.div>

        <p className="text-center text-sm text-gray-500">
          👆 Tap to flip
        </p>

        {/* Navigation */}
        <div className="flex gap-2">
          <button
            onClick={() => {
              setCurrentCard(prev => Math.max(0, prev - 1));
              setFlipped(false);
            }}
            disabled={currentCard === 0}
            className="flex-1 py-2 bg-gray-100 text-gray-600 rounded-lg font-medium disabled:opacity-50"
          >
            ← Previous
          </button>
          <button
            onClick={() => {
              setCurrentCard(prev => Math.min(cards.length - 1, prev + 1));
              setFlipped(false);
            }}
            disabled={currentCard === cards.length - 1}
            className="flex-1 py-2 bg-pink-500 text-white rounded-lg font-medium disabled:opacity-50"
          >
            Next →
          </button>
        </div>
      </div>
    </ResponseSection>
  );
};

// Progress & XP Section
const ProgressSection = ({ xpEarned = 10, conceptProgress = 60, streak = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 1 }}
    className="bg-gradient-to-r from-violet-500 to-purple-600 rounded-xl p-4 text-white"
  >
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="bg-white/20 rounded-full p-2">
          <span className="text-2xl">⚡</span>
        </div>
        <div>
          <p className="font-bold">+{xpEarned} XP Earned!</p>
          <p className="text-sm text-white/80">Keep learning to level up</p>
        </div>
      </div>
      
      {streak > 0 && (
        <div className="bg-white/20 rounded-lg px-3 py-2 text-center">
          <p className="text-2xl">🔥</p>
          <p className="text-sm font-bold">{streak} day streak</p>
        </div>
      )}
    </div>

    {/* Progress bar */}
    <div className="mt-4">
      <div className="flex items-center justify-between text-sm mb-1">
        <span>Concept Mastery</span>
        <span>{conceptProgress}%</span>
      </div>
      <div className="h-2 bg-white/20 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-white rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${conceptProgress}%` }}
          transition={{ delay: 1.2, duration: 0.8 }}
        />
      </div>
    </div>
  </motion.div>
);

// Main Adaptive Response Card
const AdaptiveResponseCard = ({
  response = {},
  showProgress = true,
  onComplete,
}) => {
  const {
    hook,
    definition,
    formula,
    examFocus,
    memory,
    indianContext,
    commonMistakes,
    topperTips,
    steps,
    quickRecall,
    xp = 10,
    progress = 60,
    streak = 0,
  } = response;

  return (
    <div className="adaptive-response space-y-4">
      {/* Hook - Always first */}
      {hook && <HookSection text={hook.text} emoji={hook.emoji} />}

      {/* Definition */}
      {definition && (
        <DefinitionSection
          title={definition.title}
          content={definition.content}
          hindiTerm={definition.hindiTerm}
        />
      )}

      {/* Formula */}
      {formula && (
        <FormulaSection
          formula={formula.formula}
          explanation={formula.explanation}
          marks={formula.marks}
        />
      )}

      {/* Steps */}
      {steps && <StepsSection steps={steps.items} title={steps.title} />}

      {/* Exam Focus */}
      {examFocus && (
        <ExamFocusSection
          points={examFocus.points}
          marksBreakdown={examFocus.marksBreakdown}
        />
      )}

      {/* Memory Hook */}
      {memory && (
        <MemorySection
          mnemonic={memory.mnemonic}
          analogy={memory.analogy}
          story={memory.story}
        />
      )}

      {/* Indian Context */}
      {indianContext && <IndianContextSection examples={indianContext.examples} />}

      {/* Common Mistakes */}
      {commonMistakes && <CommonMistakesSection mistakes={commonMistakes.items} />}

      {/* Topper Tips */}
      {topperTips && <TopperTipsSection tips={topperTips.items} />}

      {/* Quick Recall */}
      {quickRecall && <QuickRecallSection cards={quickRecall.cards} />}

      {/* Progress & XP */}
      {showProgress && (
        <ProgressSection xpEarned={xp} conceptProgress={progress} streak={streak} />
      )}
    </div>
  );
};

// Export individual sections for flexible use
export {
  ResponseSection,
  HookSection,
  DefinitionSection,
  FormulaSection,
  ExamFocusSection,
  MemorySection,
  IndianContextSection,
  CommonMistakesSection,
  TopperTipsSection,
  StepsSection,
  QuickRecallSection,
  ProgressSection,
};

export default AdaptiveResponseCard;

