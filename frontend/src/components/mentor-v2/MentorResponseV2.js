/**
 * Mentor Response Component v2.0 - Progressive Disclosure
 * Default view + interactive reveal system
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  Lightbulb, 
  Target, 
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Users
} from 'lucide-react';

export default function MentorResponseV2({ response, onInteraction }) {
  const [revealedSections, setRevealedSections] = useState(new Set());
  const [imageLoadError, setImageLoadError] = useState({});
  
  if (!response || !response.default_view) {
    return <div className="text-red-500">Error: Invalid response structure</div>;
  }
  
  const { default_view, progressive_sections } = response;
  
  // Handle button click to reveal section
  const handleReveal = (sectionKey) => {
    setRevealedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionKey)) {
        newSet.delete(sectionKey);
      } else {
        newSet.add(sectionKey);
      }
      return newSet;
    });
    
    // Notify parent for analytics
    if (onInteraction) {
      onInteraction(sectionKey);
    }
  };
  
  // Handle image load error
  const handleImageError = (imageKey) => {
    setImageLoadError(prev => ({ ...prev, [imageKey]: true }));
  };
  
  return (
    <div className="mentor-response-v2 space-y-4">
      {/* Default View - Always Visible */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-lg p-6 border-2 border-purple-100"
      >
        {/* Mentor Avatar + Greeting */}
        <div className="flex items-start gap-4 mb-4">
          {default_view.mentor_avatar && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', duration: 0.5 }}
              className="flex-shrink-0"
            >
              {!imageLoadError['mentor_avatar'] ? (
                <img
                  src={default_view.mentor_avatar.visual_url}
                  alt="Mentor Avatar"
                  className="w-16 h-16 rounded-full border-2 border-purple-300"
                  onError={() => handleImageError('mentor_avatar')}
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-purple-500 flex items-center justify-center text-white text-2xl">
                  🤝
                </div>
              )}
            </motion.div>
          )}
          <div className="flex-1">
            <div className="text-xl font-bold text-purple-900">
              {default_view.greeting}
            </div>
          </div>
        </div>
        
        {/* Hero Visual - VISUAL-FIRST */}
        {default_view.hero_visual && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="mb-4 rounded-xl overflow-hidden border-2 border-purple-200"
            style={{ backgroundColor: default_view.hero_visual.placeholder_color || '#F3F4F6' }}
          >
            {!imageLoadError['hero_visual'] ? (
              <img
                src={default_view.hero_visual.visual_url}
                alt={default_view.hero_visual.alt_text || 'Hero Visual'}
                className="w-full h-auto"
                loading="eager"
                onError={() => handleImageError('hero_visual')}
              />
            ) : (
              <div className="w-full h-64 flex items-center justify-center text-gray-600 bg-gradient-to-br from-purple-100 to-blue-100">
                <div className="text-center p-6">
                  <div className="text-6xl mb-3">
                    {getMetaphorIcon(default_view.metaphor?.category)}
                  </div>
                  <p className="text-sm font-medium text-gray-700">
                    {default_view.hero_visual.alt_text || default_view.metaphor?.text || 'Visual concept'}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    Visual assets loading...
                  </p>
                </div>
              </div>
            )}
          </motion.div>
        )}
        
        {/* Metaphor Card */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 mb-4 border border-purple-200">
          <div className="flex items-start gap-3">
            <div className="text-3xl mt-1">
              {getMetaphorIcon(default_view.metaphor?.category)}
            </div>
            <div className="flex-1">
              <p className="text-gray-800 leading-relaxed">
                {default_view.metaphor?.text}
              </p>
            </div>
          </div>
        </div>
        
        {/* Main Content */}
        <div className="bg-gray-50 rounded-xl p-5 mb-4">
          <div className="prose prose-purple max-w-none">
            <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap">
              {default_view.main_content?.content}
            </p>
            {default_view.main_content?.key_insight && (
              <div className="mt-4 flex items-center gap-2 bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                <Lightbulb className="w-5 h-5 text-yellow-600 flex-shrink-0" />
                <p className="text-sm text-yellow-900 font-medium m-0">
                  {default_view.main_content.key_insight}
                </p>
              </div>
            )}
          </div>
        </div>
        
        {/* Interactive Buttons */}
        {default_view.interactive_options && default_view.interactive_options.length > 0 && (
          <div className="flex flex-wrap gap-3 mb-4">
            {default_view.interactive_options.map((option, idx) => (
              <motion.button
                key={idx}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleReveal(option.reveals)}
                className={`px-6 py-3 rounded-xl font-semibold text-sm transition-all ${
                  revealedSections.has(option.reveals)
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'bg-white text-purple-600 border-2 border-purple-600 hover:bg-purple-50'
                }`}
              >
                {option.button_text}
                {revealedSections.has(option.reveals) ? (
                  <ChevronUp className="inline ml-2 w-4 h-4" />
                ) : (
                  <ChevronDown className="inline ml-2 w-4 h-4" />
                )}
              </motion.button>
            ))}
          </div>
        )}
        
        {/* Professor Badge */}
        {default_view.professor_badge && (
          <div className="flex items-center justify-between bg-green-50 rounded-lg p-3 border border-green-200">
            <div className="flex items-center gap-2">
              {default_view.professor_badge.badge_visual && !imageLoadError['professor_badge'] ? (
                <img
                  src={default_view.professor_badge.badge_visual}
                  alt="Professor Verified"
                  className="w-6 h-6"
                  onError={() => handleImageError('professor_badge')}
                />
              ) : (
                <CheckCircle className="w-5 h-5 text-green-600" />
              )}
              <span className="text-sm font-medium text-green-900">
                Professor-Verified ✓ {default_view.professor_badge.ncert_ref}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Users className="w-4 h-4" />
              <span>{default_view.professor_badge.students_solved || '10,000+'}  students solved this</span>
            </div>
          </div>
        )}
      </motion.div>
      
      {/* Progressive Sections - Revealed on Demand */}
      {progressive_sections && (
        <AnimatePresence>
          {/* Strategy Section */}
          {revealedSections.has('strategy') && progressive_sections.strategy && (
            <ProgressiveSection
              title={progressive_sections.strategy.title || 'Step-by-Step Strategy'}
              icon={<Target className="w-6 h-6" />}
              onClose={() => handleReveal('strategy')}
            >
              <div className="prose prose-purple max-w-none">
                {/* Strategy Steps */}
                {progressive_sections.strategy.steps && progressive_sections.strategy.steps.length > 0 ? (
                  <div className="space-y-4">
                    {progressive_sections.strategy.steps.map((step, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bg-white rounded-lg p-4 border border-purple-100"
                      >
                        {step.step_visual && !imageLoadError[`step_${idx}`] && (
                          <img
                            src={step.step_visual}
                            alt={`Step ${step.step_number || idx + 1}`}
                            className="w-full h-auto rounded-lg mb-3"
                            onError={() => handleImageError(`step_${idx}`)}
                          />
                        )}
                        <div className="flex items-start gap-3">
                          <div className="bg-purple-100 text-purple-700 rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                            {step.step_number || idx + 1}
                          </div>
                          <div className="flex-1">
                            <p className="text-gray-800">{step.step_text}</p>
                            {step.visual_highlight && (
                              <p className="text-sm text-purple-600 mt-2">
                                👁️ {step.visual_highlight}
                              </p>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-800 whitespace-pre-wrap">
                    {progressive_sections.strategy.content}
                  </div>
                )}
                
                {/* Tips */}
                {progressive_sections.strategy.tips && progressive_sections.strategy.tips.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <p className="font-semibold text-purple-900 mb-2">💡 Pro Tips:</p>
                    <ul className="list-disc pl-5 space-y-1">
                      {progressive_sections.strategy.tips.map((tip, idx) => {
                        // Handle both string and object formats
                        const tipText = typeof tip === 'string' ? tip : tip.tip_text;
                        const tipIcon = typeof tip === 'object' ? tip.tip_icon : '💡';
                        return (
                          <li key={idx} className="text-gray-700">
                            {tipIcon && <span className="mr-2">{tipIcon}</span>}
                            {tipText}
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </div>
            </ProgressiveSection>
          )}
          
          {/* Visual Schema Section */}
          {revealedSections.has('visual') && progressive_sections.visual_schema && (
            <ProgressiveSection
              title="Visual Understanding"
              icon={<Lightbulb className="w-6 h-6" />}
              onClose={() => handleReveal('visual')}
            >
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">
                  {progressive_sections.visual_schema.mental_model}
                </p>
                {/* Simple visual diagram - can be enhanced later */}
                <div className="text-center text-gray-500 py-8">
                  <Lightbulb className="w-16 h-16 mx-auto mb-2 text-blue-400" />
                  <p>Visual diagram placeholder</p>
                </div>
              </div>
            </ProgressiveSection>
          )}
          
          {/* Interactive Solver Section */}
          {revealedSections.has('interactive_solver') && progressive_sections.interactive_solver && (
            <ProgressiveSection
              title="Let's Solve Step-by-Step"
              icon={<Target className="w-6 h-6" />}
              onClose={() => handleReveal('interactive_solver')}
            >
              <div className="space-y-4">
                {progressive_sections.interactive_solver.problem_breakdown && (
                  <ol className="list-decimal pl-5 space-y-2">
                    {progressive_sections.interactive_solver.problem_breakdown.map((step, idx) => (
                      <li key={idx} className="text-gray-800">{step}</li>
                    ))}
                  </ol>
                )}
                {progressive_sections.interactive_solver.solution_approach && (
                  <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                    <p className="text-sm font-semibold text-green-900 mb-2">✅ Solution Approach:</p>
                    <p className="text-gray-800">{progressive_sections.interactive_solver.solution_approach}</p>
                  </div>
                )}
              </div>
            </ProgressiveSection>
          )}
          
          {/* Mini Practice Section */}
          {revealedSections.has('practice') && progressive_sections.mini_practice && (
            <ProgressiveSection
              title="Mini Practice"
              icon={<TrendingUp className="w-6 h-6" />}
              onClose={() => handleReveal('practice')}
            >
              <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                <p className="font-semibold text-gray-900 mb-3">
                  {progressive_sections.mini_practice.question}
                </p>
                {progressive_sections.mini_practice.hint && (
                  <p className="text-sm text-gray-600 mt-2">
                    💡 Hint: {progressive_sections.mini_practice.hint}
                  </p>
                )}
                {progressive_sections.mini_practice.time_estimate && (
                  <p className="text-xs text-gray-500 mt-2">
                    ⏱️ Time: {progressive_sections.mini_practice.time_estimate}
                  </p>
                )}
              </div>
            </ProgressiveSection>
          )}
        </AnimatePresence>
      )}
      
      {/* Encouragement & What's Next - Always at bottom */}
      {progressive_sections && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-200">
          {progressive_sections.encouragement && (
            <p className="text-purple-900 font-medium mb-3">
              ✨ {progressive_sections.encouragement.message}
            </p>
          )}
          {progressive_sections.whats_next && progressive_sections.whats_next.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-purple-900 mb-2">➕ What's Next?</p>
              <ul className="text-sm text-purple-800 space-y-1">
                {progressive_sections.whats_next.map((item, idx) => (
                  <li key={idx}>• {item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Progressive Section Component
function ProgressiveSection({ title, icon, children, onClose }) {
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white rounded-2xl shadow-lg border-2 border-purple-100 overflow-hidden"
    >
      <div className="bg-gradient-to-r from-purple-500 to-blue-500 text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {icon}
          <h3 className="font-bold text-lg">{title}</h3>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:bg-white/20 rounded-full p-2 transition-colors"
        >
          <ChevronUp className="w-5 h-5" />
        </button>
      </div>
      <div className="p-6">
        {children}
      </div>
    </motion.div>
  );
}

// Helper function to get metaphor icon
function getMetaphorIcon(category) {
  const icons = {
    cricket: '🏏',
    bollywood: '🎬',
    cooking: '🍳',
    gaming: '🎮'
  };
  return icons[category] || '💡';
}
