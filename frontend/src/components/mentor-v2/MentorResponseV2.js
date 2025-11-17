/**
 * Mentor Response Component v2.0 - Progressive Disclosure
 * Default view + interactive reveal system
 */
import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  Lightbulb, 
  Target, 
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Users,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check
} from 'lucide-react';

import DynamicSceneComposer from '../DynamicSceneComposer';
import { buildSceneFromMetaphor } from '../../utils/svgGenerator';
import atomicStructure from '../../teaching/scripts/atomicStructureElectronConfig';
import AtomicInteractiveCard from '../../teaching/AtomicInteractiveCard';
import CovalentInteractiveCard from '../../teaching/CovalentInteractiveCard';
import TeachingVisualPlayer from '../TeachingVisualPlayer';
import TipCard from '../teaching/blocks/TipCard';
import { MarkdownParagraph } from '../../utils/markdownRenderer';

export default function MentorResponseV2({ response, onInteraction }) {
  const [revealedSections, setRevealedSections] = useState(new Set());
  const [imageLoadError, setImageLoadError] = useState({});
  const [visualDebugInfo, setVisualDebugInfo] = useState({});
  const [feedback, setFeedback] = useState(null); // 'helpful' or 'not_helpful'
  const [copied, setCopied] = useState(false);
  
  // Intent-driven rendering hints from backend
  const intent = response?.intent || null;
  const directives = response?.render_directives || {};
  const skipGreeting = !!directives.skip_greeting;
  const suppressMetaphor = !!directives.suppress_metaphor;
  const suppressCTA = !!directives.suppress_cta;
  const preferApplicationCard = !!directives.prefer_application_card;
  const preferLayers = !!directives.prefer_layers;
  const suppressBasicSteps = !!directives.suppress_basic_steps;
  const preferCompareLayout = !!directives.prefer_compare_layout;
  const preferParagraphFirst = !!directives.prefer_paragraph_first;
  
  // NEW: Greeting-specific directives (prevents duplication)
  const suppressMainContent = !!directives.suppress_main_content;
  const suppressVisualPlaceholder = !!directives.suppress_visual_placeholder;
  const greetingOnly = !!directives.greeting_only;
  
  if (!response || !response.default_view) {
    console.error('❌ Invalid response structure:', response);
    return <div className="text-red-500">Error: Invalid response structure</div>;
  }
  
  const { default_view, progressive_sections } = response;

  // Compute domain-specific flags used across rendering and scene synthesis
  const chemAtomic = useMemo(() => {
    try {
      const seed =
        default_view?.metaphor?.text ||
        default_view?.main_content?.title ||
        default_view?.main_content?.content ||
        default_view?.greeting || '';
      const blob = [seed, progressive_sections?.explanation, progressive_sections?.key_takeaways]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return /(atomic structure|electron(ic)? configuration|bohr|shell|orbital)/i.test(blob);
    } catch {
      return false;
    }
  }, [default_view, progressive_sections]);

  // Check for animated teaching visual from new Visual Teaching Engine
  const animatedTeachingVisual = useMemo(() => {
    try {
      // Check if backend sent animated teaching visual data
      // Could be at response.teaching_visual or response.dual_response.teaching_visual
      const teachingVisual = response?.teaching_visual || response?.dual_response?.teaching_visual;

      // Debug logging
      console.log('🔍 MentorResponseV2 - Checking for teaching_visual:', {
        hasTeachingVisual: !!teachingVisual,
        hasStages: !!(teachingVisual?.stages),
        stagesLength: teachingVisual?.stages?.length,
        responseKeys: Object.keys(response || {}),
        teachingVisualKeys: teachingVisual ? Object.keys(teachingVisual) : []
      });

      if (teachingVisual && teachingVisual?.stages && teachingVisual.stages.length > 0) {
        console.log('✅ ANIMATED TEACHING VISUAL DETECTED:', {
          visualId: teachingVisual.visual_id,
          type: teachingVisual.type,
          numStages: teachingVisual.stages?.length,
          totalDuration: teachingVisual.total_duration_ms,
          metadata: teachingVisual.metadata
        });
        return teachingVisual;
      } else {
        console.warn('⚠️ Teaching visual missing or invalid:', {
          hasTeachingVisual: !!teachingVisual,
          hasStages: !!(teachingVisual?.stages),
          stagesLength: teachingVisual?.stages?.length
        });
      }
    } catch (e) {
      console.error('❌ VISUAL_ENGINE: animated teaching visual check failed', e);
    }
    return null;
  }, [response]);

  // CRITICAL FIX: Check for backend-generated SVG first (solution visuals)
  const backendSVG = useMemo(() => {
    try {
      // Check if backend sent SVG content (from unified_visual_system.py)
      if (response?.visual_data?.content && response?.visual_data?.type === 'svg') {
        console.log('✅ BACKEND SVG DETECTED:', {
          length: response.visual_data.content.length,
          visualType: response.visual_data.visual_type,
          friendTestPassed: response.visual_data.friend_test_passed
        });
        return {
          hasSVG: true,
          svg: response.visual_data.content,
          visualType: response.visual_data.visual_type,
          metadata: response.visual_data.metadata
        };
      }
    } catch (e) {
      console.warn('VISUAL_ENGINE: backend SVG check failed', e);
    }
    return { hasSVG: false };
  }, [response]);

  // Prefer dynamic scene_json provided by backend; otherwise synthesize from metaphor text
  const dynamicScene = useMemo(() => {
    try {
      const hv = default_view?.hero_visual;
      if (hv?.scene_json) {
        return {
          type: 'story_scene',
          generated: true,
          scene_json: hv.scene_json,
          interaction_flow: hv.interaction_flow || [],
          neuro_symbolic_map: hv.neuro_symbolic_map || [],
          caption_text: hv.caption_text || default_view?.metaphor?.text || ''
        };
      }
      if (response?.visual_data?.scene_json) {
        const vd = response.visual_data;
        return {
          type: 'story_scene',
          generated: true,
          scene_json: vd.scene_json,
          interaction_flow: vd.interaction_flow || [],
          neuro_symbolic_map: vd.neuro_symbolic_map || [],
          caption_text: vd.caption_text || default_view?.metaphor?.text || ''
        };
      }
      // As a last resort, synthesize from available text to avoid static visuals
      const seed =
        default_view?.metaphor?.text ||
        default_view?.main_content?.title ||
        default_view?.main_content?.content ||
        default_view?.greeting || '';
      // Chemistry atomic structure override to prevent mismatched math visuals
      if (chemAtomic) {
        const { scene } = atomicStructure({ complexity: 'simple' });
        try { console.debug('[TEACHING] Chemistry atomic override active'); } catch {}
        return scene;
      }
      if (seed) return buildSceneFromMetaphor(seed, 'general');
    } catch (e) {
      console.warn('VISUAL_ENGINE: dynamic scene generation failed', e);
    }
    return null;
  }, [default_view, response, chemAtomic]);

  // Optional flag to force dynamic scenes even if images exist
  const forceDynamic = (process.env.REACT_APP_FORCE_DYNAMIC_SCENE || '').toLowerCase() === 'true' ||
                       process.env.REACT_APP_FORCE_DYNAMIC_SCENE === '1';
  
  // Debug: Log visual data
  useEffect(() => {
    if (default_view.hero_visual) {
      const visualInfo = {
        hasHeroVisual: !!default_view.hero_visual,
        hasVisualUrl: !!default_view.hero_visual.visual_url,
        urlType: default_view.hero_visual.visual_url?.startsWith('data:') ? 'data URI' : 'external URL',
        urlLength: default_view.hero_visual.visual_url?.length || 0,
        tier: default_view.hero_visual.tier,
        fallbackEmoji: default_view.hero_visual.fallback_emoji,
        placeholderColor: default_view.hero_visual.placeholder_color
      };
      console.log('🎨 Visual Debug Info:', visualInfo);
      console.log('🎨 Visual URL (first 200 chars):', default_view.hero_visual.visual_url?.substring(0, 200));
      setVisualDebugInfo(visualInfo);
    } else {
      console.warn('⚠️ No hero_visual in response');
    }
  }, [default_view]);
  
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
  const handleImageError = (imageKey, event) => {
    console.error(`❌ Image load error for ${imageKey}:`, event);
    setImageLoadError(prev => ({ ...prev, [imageKey]: true }));
  };
  
  // Handle image load success
  const handleImageLoad = (imageKey) => {
    console.log(`✅ Image loaded successfully: ${imageKey}`);
  };
  
  // Render helper: hero visual block with all priority fallbacks
  const renderHeroVisual = () => {
    // Suppress hero visuals for compare/contrast or when explicitly requested
    if (preferCompareLayout || intent === 'compare_contrast') return null;
    return (
    (default_view.hero_visual || animatedTeachingVisual) && !suppressMetaphor && (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="mb-4 relative"
        style={{ backgroundColor: (animatedTeachingVisual || backendSVG.hasSVG || dynamicScene || forceDynamic) ? 'transparent' : (default_view.hero_visual?.placeholder_color || '#F3F4F6') }}
      >
        {/* PRIORITY 0: Animated Teaching Visual (ALWAYS USE IF EXISTS) */}
        {animatedTeachingVisual ? (
          <div className="w-full">
            <TeachingVisualPlayer
              visualData={animatedTeachingVisual}
              onComplete={(result) => {
                if (onInteraction) onInteraction('visual_complete', result);
              }}
              onInteraction={(interaction) => {
                if (onInteraction) onInteraction('visual_interaction', interaction);
              }}
            />
          </div>
        ) : (
          <>
            {/* LEGACY VISUALS DISABLED - Only show if teaching_visual is missing */}
            {/* PRIORITY 1: Backend-generated SVG (DISABLED - legacy system) */}
            {false && backendSVG.hasSVG && (
          <div className="w-full overflow-x-auto bg-white rounded-lg border-2 border-purple-200 p-4">
            <div
              dangerouslySetInnerHTML={{ __html: backendSVG.svg }}
              style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}
            />
            {backendSVG.visualType === 'solution' && (
              <div className="mt-3 text-center">
                <span className="inline-block bg-green-100 text-green-800 text-xs font-semibold px-3 py-1 rounded-full">
                  ✓ Step-by-Step Solution Visual
                </span>
              </div>
            )}
          </div>
            )}

            {/* PRIORITY 2: Dynamic scene_json (DISABLED - legacy system) */}
            {false && !backendSVG.hasSVG && (dynamicScene || forceDynamic) && (
          <div className="w-full">
            {chemAtomic ? (
              (() => {
                const covBlob = [default_view?.metaphor?.text, default_view?.main_content?.title, default_view?.main_content?.content]
                  .filter(Boolean).join(' ').toLowerCase();
                return /covalent/.test(covBlob)
                  ? <CovalentInteractiveCard />
                  : <AtomicInteractiveCard visualData={dynamicScene} />;
              })()
            ) : (
              <DynamicSceneComposer visualData={dynamicScene || buildSceneFromMetaphor(default_view?.metaphor?.text || default_view?.main_content?.title || default_view?.main_content?.content || default_view?.greeting || 'concept', 'general')} />
            )}
          </div>
            )}

            {/* PRIORITY 3: Static image fallback (DISABLED - legacy system) */}
            {false && !backendSVG.hasSVG && !imageLoadError['hero_visual'] && default_view.hero_visual ? (
          <img
            src={default_view.hero_visual.visual_url}
            alt={default_view.hero_visual.alt_text || 'Hero Visual'}
            className="w-full h-auto"
            loading="eager"
            onLoad={() => handleImageLoad('hero_visual')}
            onError={(e) => handleImageError('hero_visual', e)}
            style={{ minHeight: '200px', display: (dynamicScene || forceDynamic) ? 'none' : undefined }}
          />
        ) : !backendSVG.hasSVG && imageLoadError['hero_visual'] && default_view.hero_visual && (
          <div className="w-full h-64 flex flex-col items-center justify-center text-gray-600 bg-gradient-to-br from-purple-100 to-blue-100 p-6" style={{ display: (dynamicScene || forceDynamic) ? 'none' : undefined }}>
            <div className="text-center">
              <div className="text-6xl mb-3">
                {default_view.hero_visual.fallback_emoji || getMetaphorIcon(default_view.metaphor?.category) || '💡'}
              </div>
              <p className="text-sm font-medium text-gray-700 mb-2">
                {default_view.hero_visual.alt_text || default_view.metaphor?.text || 'Visual concept'}
              </p>
              <p className="text-xs text-gray-500">Visual Tier {default_view.hero_visual.tier || 1} - Fallback Active</p>
            </div>
          </div>
            )}
          </>
        )}
      </motion.div>
    )
    );
  };

  return (
    <div className="mentor-response-v2 space-y-4">
      {/* Default View - Always Visible */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-lg p-6 border-2 border-purple-100"
      >
        {/* Mentor Avatar + Greeting (skipped for clarifications) */}
        {!skipGreeting && default_view.greeting && (
        <div className="flex items-start gap-4 mb-6">
          {default_view.mentor_avatar && !suppressMetaphor && (
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
            <div className="text-xl md:text-2xl font-bold text-purple-800 leading-relaxed">
              {default_view.greeting}
            </div>
          </div>
        </div>
        )}
        
        {/* Hero Visual - paragraph-first if directed */}
        {!preferParagraphFirst && !suppressVisualPlaceholder && renderHeroVisual()}
        
        {/* Metaphor Card - SKIP if it's repetitive with main content */}
        {!suppressMetaphor && default_view.metaphor?.text && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-5 mb-4 border-2 border-purple-200">
          <div className="flex items-start gap-4">
            <div className="text-4xl">
              {getMetaphorIcon(default_view.metaphor?.category)}
            </div>
            <div className="flex-1">
              <div className="text-xs font-semibold text-purple-600 uppercase mb-1">🎯 Intuitive Understanding</div>
              <MarkdownParagraph className="text-gray-800 text-base leading-relaxed">
                {default_view.metaphor?.text}
              </MarkdownParagraph>
            </div>
          </div>
        </div>
        )}
        
        {/* Main Content - HIDE if suppress_main_content is true (for greetings) */}
        {/* Render as structured content with better formatting */}
        {!suppressMainContent && default_view.main_content?.content && (
        <div className="space-y-4 mb-4">
          {/* Parse and render content with better structure */}
          <div className="bg-white rounded-xl p-6 border-2 border-gray-200 shadow-sm">
            <div className="text-xs font-semibold text-gray-600 uppercase mb-3">📚 Detailed Explanation</div>
            <div className="prose prose-lg max-w-none">
              <div className="text-gray-800 leading-relaxed space-y-4">
                {/* Smart content rendering with markdown support */}
                {default_view.main_content.content.split('\n\n').map((paragraph, idx) => (
                  <MarkdownParagraph key={idx} className="text-base leading-relaxed">
                    {paragraph}
                  </MarkdownParagraph>
                ))}
              </div>
            </div>
            
            {/* Key Insight Badge - moved inside main content */}
            {default_view.main_content?.key_insight && (
              <div className="mt-6 flex items-start gap-3 bg-yellow-50 p-4 rounded-lg border-2 border-yellow-200">
                <Lightbulb className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <div className="text-xs font-semibold text-yellow-700 uppercase mb-1">💡 Key Insight</div>
                  <MarkdownParagraph className="text-sm text-yellow-900 font-medium leading-relaxed">
                    {default_view.main_content.key_insight}
                  </MarkdownParagraph>
                </div>
              </div>
            )}
          </div>
        </div>
        )}

        {/* Application Card (if requested) */}
        {preferApplicationCard && (
          <div className="mb-4">
            <TipCard tip_type="application" text={"Real-world: Observe this concept today and note one example from your surroundings."} />
          </div>
        )}

        {/* Hero visual after paragraph if requested */}
        {preferParagraphFirst && renderHeroVisual()}
        
        {/* Interactive Buttons */}
        {!suppressCTA && default_view.interactive_options && default_view.interactive_options.length > 0 && (
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
      {progressive_sections && Object.keys(progressive_sections).length > 0 && (
        <AnimatePresence>
          {/* Strategy Section */}
          {(preferLayers || revealedSections.has('strategy')) && progressive_sections.strategy && (
            <ProgressiveSection
              title={progressive_sections.strategy.title || 'Step-by-Step Strategy'}
              icon={<Target className="w-6 h-6" />}
              onClose={() => handleReveal('strategy')}
            >
              <div className="prose prose-purple max-w-none">
                {/* Strategy Steps */}
                {!suppressBasicSteps && progressive_sections.strategy.steps && progressive_sections.strategy.steps.length > 0 ? (
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
      
      {/* Encouragement & What's Next - Only show if has actual content */}
      {progressive_sections && Object.keys(progressive_sections).length > 0 && 
       (progressive_sections.encouragement || (progressive_sections.whats_next && progressive_sections.whats_next.length > 0)) && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-200">
          {progressive_sections.encouragement && (
            <p className="text-purple-900 font-medium mb-3">
              ✨ {typeof progressive_sections.encouragement === 'string' 
                ? progressive_sections.encouragement 
                : progressive_sections.encouragement.message}
            </p>
          )}
          {progressive_sections.whats_next && progressive_sections.whats_next.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-purple-900 mb-2">➕ What's Next?</p>
              <ul className="text-sm text-purple-800 space-y-1">
                {progressive_sections.whats_next.map((item, idx) => {
                  // Handle both string and object formats
                  const suggestion = typeof item === 'string' ? item : item.suggestion;
                  return (
                    <li key={idx}>• {suggestion}</li>
                  );
                })}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {/* Follow-Up Question Suggestions */}
      {!greetingOnly && (
        <div className="mt-6 mb-4">
          <div className="text-sm font-semibold text-gray-700 mb-3">💬 Continue Learning:</div>
          <div className="flex flex-wrap gap-2">
            <button 
              onClick={() => onInteraction && onInteraction('followup', 'practice')}
              className="px-4 py-2 bg-gradient-to-r from-purple-50 to-blue-50 text-purple-700 rounded-lg border border-purple-200 hover:border-purple-400 hover:shadow-md transition-all text-sm font-medium"
            >
              ⚡ Practice problem
            </button>
            <button 
              onClick={() => onInteraction && onInteraction('followup', 'example')}
              className="px-4 py-2 bg-gradient-to-r from-blue-50 to-teal-50 text-blue-700 rounded-lg border border-blue-200 hover:border-blue-400 hover:shadow-md transition-all text-sm font-medium"
            >
              🔍 More examples
            </button>
            <button 
              onClick={() => onInteraction && onInteraction('followup', 'application')}
              className="px-4 py-2 bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 rounded-lg border border-green-200 hover:border-green-400 hover:shadow-md transition-all text-sm font-medium"
            >
              🌍 Real-world use
            </button>
            <button 
              onClick={() => onInteraction && onInteraction('followup', 'related')}
              className="px-4 py-2 bg-gradient-to-r from-orange-50 to-yellow-50 text-orange-700 rounded-lg border border-orange-200 hover:border-orange-400 hover:shadow-md transition-all text-sm font-medium"
            >
              🔗 Related concepts
            </button>
          </div>
        </div>
      )}
      
      {/* Quick Actions Bar - Feedback & Copy */}
      <div className="mt-6 pt-4 border-t border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600 font-medium">Was this helpful?</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setFeedback('helpful');
                if (onInteraction) onInteraction('feedback_positive');
              }}
              className={`p-2 rounded-lg transition-all ${
                feedback === 'helpful'
                  ? 'bg-green-100 text-green-600'
                  : 'bg-gray-100 text-gray-600 hover:bg-green-50 hover:text-green-600'
              }`}
              title="This was helpful!"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                setFeedback('not_helpful');
                if (onInteraction) onInteraction('feedback_negative');
              }}
              className={`p-2 rounded-lg transition-all ${
                feedback === 'not_helpful'
                  ? 'bg-red-100 text-red-600'
                  : 'bg-gray-100 text-gray-600 hover:bg-red-50 hover:text-red-600'
              }`}
              title="Not helpful"
            >
              <ThumbsDown className="w-4 h-4" />
            </button>
          </div>
          {feedback === 'helpful' && (
            <span className="text-sm text-green-600 font-medium">Thanks for the feedback! 🙌</span>
          )}
        </div>
        
        <button
          onClick={() => {
            // Copy full response to clipboard
            const textToCopy = [
              default_view.greeting,
              default_view.metaphor?.text,
              default_view.main_content?.content,
              default_view.main_content?.key_insight
            ].filter(Boolean).join('\n\n');
            
            navigator.clipboard.writeText(textToCopy).then(() => {
              setCopied(true);
              setTimeout(() => setCopied(false), 2000);
            });
          }}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-100 text-purple-600 hover:bg-purple-200 transition-all"
          title="Copy response"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              <span className="text-sm font-medium">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span className="text-sm font-medium">Copy</span>
            </>
          )}
        </button>
      </div>
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
