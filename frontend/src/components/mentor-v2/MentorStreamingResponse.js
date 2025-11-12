import React, { useMemo, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Target } from 'lucide-react';

const ICONS = {
  greeting: '🤝',
  metaphor: '🟣',
  core: '📘',
  insight: '💡'
};

const METAPHOR_EMOJIS = {
  cricket: '🏏',
  bollywood: '🎬',
  cooking: '🍳',
  gaming: '🎮'
};

export default function MentorStreamingResponse({
  defaultView = {},
  progressiveSections = {},
  isThinking,
  isComplete
}) {
  const metaphorEmoji = METAPHOR_EMOJIS[defaultView?.metaphor?.category] || '🟣';

  const blocks = useMemo(() => {
    const items = [];
    if (defaultView?.greeting) {
      items.push({
        key: 'greeting',
        icon: ICONS.greeting,
        title: 'Greeting',
        text: defaultView.greeting,
        tone: 'text-purple-900'
      });
    }
    if (defaultView?.metaphor?.text) {
      items.push({
        key: 'metaphor',
        icon: metaphorEmoji,
        title: 'Memory Hook',
        text: defaultView.metaphor.text,
        tone: 'text-gray-800'
      });
    }
    if (defaultView?.main_content?.content) {
      items.push({
        key: 'core',
        icon: ICONS.core,
        title: 'Core Idea',
        text: defaultView.main_content.content,
        tone: 'text-gray-900'
      });
    }
    if (defaultView?.main_content?.key_insight) {
      items.push({
        key: 'insight',
        icon: ICONS.insight,
        title: 'Key Insight',
        text: defaultView.main_content.key_insight,
        tone: 'text-yellow-800'
      });
    }
    return items;
  }, [defaultView, metaphorEmoji]);

  const strategySteps = progressiveSections?.strategy?.steps || [];

  return (
    <div className="space-y-4">
      {isThinking && <ThinkingLoader />}

      {blocks.map((block, index) => (
        <motion.div
          key={block.key}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.15 }}
          className="bg-white border border-purple-100 rounded-2xl p-4 shadow-sm"
        >
          <div className="flex items-start gap-3">
            <div className="text-2xl">{block.icon}</div>
            <div className="flex-1">
              <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">{block.title}</p>
              <TypewriterText text={block.text} className={`text-sm whitespace-pre-wrap ${block.tone}`} />
            </div>
          </div>
        </motion.div>
      ))}

      {strategySteps.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: blocks.length * 0.15 }}
          className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-100 rounded-2xl p-4"
        >
          <div className="flex items-center gap-2 mb-3">
            <Target className="w-4 h-4 text-purple-600" />
            <p className="text-sm font-semibold text-purple-900">Topper Flow</p>
          </div>
          <div className="space-y-3">
            {strategySteps.map((step, idx) => (
              <div key={idx} className="flex items-start gap-3 bg-white rounded-xl p-3 border border-purple-100 shadow-sm">
                <div className="w-6 h-6 rounded-full bg-purple-600 text-white text-xs flex items-center justify-center mt-0.5">
                  {step.step_number || idx + 1}
                </div>
                <TypewriterText text={step.step_text} className="text-sm text-gray-800" speed={20} />
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {isComplete && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2 text-xs text-green-600"
        >
          <Sparkles className="w-4 h-4" />
          Stream complete
        </motion.div>
      )}
    </div>
  );
}

function ThinkingLoader() {
  return (
    <div className="bg-white border border-purple-100 rounded-2xl p-4 flex items-center gap-3 shadow-sm">
      <div className="flex space-x-1">
        <span className="w-2 h-2 rounded-full bg-purple-500 animate-bounce" style={{ animationDelay: '0ms' }}></span>
        <span className="w-2 h-2 rounded-full bg-purple-500 animate-bounce" style={{ animationDelay: '150ms' }}></span>
        <span className="w-2 h-2 rounded-full bg-purple-500 animate-bounce" style={{ animationDelay: '300ms' }}></span>
      </div>
      <p className="text-sm text-gray-500">Dhruv AI Mentor is thinking...</p>
    </div>
  );
}

function TypewriterText({ text = '', speed = 25, className = '' }) {
  const [display, setDisplay] = useState('');

  useEffect(() => {
    if (!text) {
      setDisplay('');
      return;
    }
    setDisplay('');
    let index = 0;
    const interval = setInterval(() => {
      index += 1;
      setDisplay(text.slice(0, index));
      if (index >= text.length) {
        clearInterval(interval);
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);

  const isComplete = display.length === text.length;

  return (
    <p className={`leading-relaxed ${className}`}>
      {display}
      {!isComplete && (
        <span className="inline-block w-2 h-4 bg-purple-500/40 ml-0.5 animate-pulse align-middle" />
      )}
    </p>
  );
}
