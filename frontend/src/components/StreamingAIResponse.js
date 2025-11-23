/**
 * Streaming AI Response Component
 * Receives and displays AI responses progressively like ChatGPT
 * Adaptive UI based on content type and student context
 */
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Zap, Lightbulb, BookOpen, Brain } from 'lucide-react';

export default function StreamingAIResponse({ 
  message, 
  sessionId, 
  subject = "General",
  onComplete 
}) {
  const [greeting, setGreeting] = useState('');
  const [currentSection, setCurrentSection] = useState(null);
  const [sections, setSections] = useState({});
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingStyle, setStreamingStyle] = useState(null);
  const [error, setError] = useState(null);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    startStreaming();
    
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [message]);

  const startStreaming = async () => {
    try {
      setIsStreaming(true);
      setError(null);

      // Use fetch with streaming
      const response = await fetch('/api/ai/stream/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          subject
        })
      });

      if (!response.ok) {
        throw new Error('Streaming failed');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            handleStreamEvent(data);
          }
        }
      }

    } catch (err) {
      console.error('Streaming error:', err);
      setError(err.message);
    } finally {
      setIsStreaming(false);
      if (onComplete) onComplete();
    }
  };

  const handleStreamEvent = (event) => {
    switch (event.type) {
      case 'start':
        console.log('🎬 Stream started', event.metadata);
        break;

      case 'greeting':
        setGreeting(event.text);
        setStreamingStyle(event.style);
        break;

      case 'section':
        setCurrentSection({
          type: event.section_type,
          title: event.title,
          content: '',
          category: event.category
        });
        break;

      case 'chunk':
        setSections(prev => {
          const sectionKey = event.section || 'main';
          return {
            ...prev,
            [sectionKey]: {
              ...prev[sectionKey],
              content: (prev[sectionKey]?.content || '') + event.text
            }
          };
        });
        break;

      case 'expandable_section':
        setSections(prev => ({
          ...prev,
          expandable: [...(prev.expandable || []), {
            key: event.key,
            title: event.title,
            expandable: event.expandable
          }]
        }));
        break;

      case 'complete':
        setIsStreaming(false);
        console.log('✅ Stream complete', event.metadata);
        break;

      case 'error':
        setError(event.message);
        break;
    }
  };

  // Get adaptive styling based on stream style
  const getAdaptiveStyle = () => {
    const styles = {
      excited_discovery: {
        container: 'bg-gradient-to-br from-orange-50 to-pink-50 border-2 border-orange-200',
        greeting: 'text-orange-700 font-bold',
        icon: '🔥',
        IconComponent: Sparkles,
        accentColor: 'orange'
      },
      calm_walkthrough: {
        container: 'bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-blue-200',
        greeting: 'text-blue-700 font-medium',
        icon: '🧭',
        IconComponent: BookOpen,
        accentColor: 'blue'
      },
      exam_panic_mode: {
        container: 'bg-gradient-to-br from-red-50 to-yellow-50 border-2 border-red-200',
        greeting: 'text-red-700 font-bold',
        icon: '⚡',
        IconComponent: Zap,
        accentColor: 'red'
      },
      story_narrative: {
        container: 'bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-purple-200',
        greeting: 'text-purple-700 font-medium',
        icon: '📖',
        IconComponent: BookOpen,
        accentColor: 'purple'
      },
      quick_intuition: {
        container: 'bg-gradient-to-br from-yellow-50 to-amber-50 border-2 border-yellow-200',
        greeting: 'text-yellow-800 font-bold',
        icon: '💡',
        IconComponent: Lightbulb,
        accentColor: 'yellow'
      },
      visual_thinker: {
        container: 'bg-gradient-to-br from-teal-50 to-emerald-50 border-2 border-teal-200',
        greeting: 'text-teal-700 font-medium',
        icon: '👁️',
        IconComponent: Brain,
        accentColor: 'teal'
      }
    };

    return styles[streamingStyle] || styles.calm_walkthrough;
  };

  const style = getAdaptiveStyle();
  const IconComp = style.IconComponent;

  if (error) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4">
        <p className="text-red-700 text-sm">Error: {error}</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Greeting with adaptive style */}
      {greeting && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`${style.container} rounded-2xl p-5 shadow-sm`}
        >
          <div className="flex items-start gap-3">
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 0.5 }}
            >
              <IconComp className={`w-6 h-6 text-${style.accentColor}-600`} />
            </motion.div>
            <p className={`${style.greeting} text-lg leading-relaxed`}>
              {greeting}
            </p>
          </div>
        </motion.div>
      )}

      {/* Metaphor Section (if exists) */}
      {sections.metaphor && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 border-l-4 border-purple-400"
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">🎯</span>
            <div className="flex-1">
              <h4 className="text-purple-800 font-semibold text-sm mb-2">Quick Insight</h4>
              <p className="text-gray-700 leading-relaxed">
                {sections.metaphor.content}
                {isStreaming && sections.metaphor.content && (
                  <motion.span
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                    className="inline-block ml-1 w-2 h-4 bg-purple-600"
                  />
                )}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Main Content Section */}
      {sections.main && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`${style.container} rounded-xl p-5`}
        >
          <div className="space-y-3">
            {currentSection?.type === 'main' && currentSection.title && (
              <h4 className={`${style.greeting} text-base flex items-center gap-2`}>
                <span>{style.icon}</span>
                {currentSection.title}
              </h4>
            )}
            <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
              {sections.main.content}
              {isStreaming && currentSection?.type === 'main' && (
                <motion.span
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                  className={`inline-block ml-1 w-2 h-4 bg-${style.accentColor}-600`}
                />
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Key Insight Section */}
      {sections.insight && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-4"
        >
          <div className="flex items-start gap-3">
            <Lightbulb className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h4 className="text-yellow-800 font-semibold text-sm mb-2">💡 Key Insight</h4>
              <p className="text-gray-800 leading-relaxed">
                {sections.insight.content}
                {isStreaming && sections.insight.content && (
                  <motion.span
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                    className="inline-block ml-1 w-2 h-4 bg-yellow-600"
                  />
                )}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Expandable Sections */}
      {sections.expandable && sections.expandable.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-4">
          {sections.expandable.map((section, idx) => (
            <button
              key={idx}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700 transition-colors"
            >
              {section.title}
            </button>
          ))}
        </div>
      )}

      {/* Streaming Indicator */}
      {isStreaming && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-2 text-gray-500 text-sm"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full"
          />
          <span>AI is typing...</span>
        </motion.div>
      )}
    </motion.div>
  );
}



