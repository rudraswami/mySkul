/**
 * Smart Response Component
 * 
 * Intelligent response renderer that adapts structure based on question type.
 * Like ChatGPT/Gemini - different questions get different response structures.
 * 
 * FIXED: Uses AdaptiveMarkdown EVERYWHERE for proper LaTeX, tables, and formatting.
 */

import React, { useMemo, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Lightbulb, 
  Calculator, 
  Sparkles, 
  ChevronDown, 
  ChevronUp,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  Share2,
  Bookmark
} from 'lucide-react';
import AdaptiveMarkdown from './AdaptiveMarkdown';
import VisualSketchViewer from './visual/VisualSketchViewer';
import apiClient from '../api/client';

// SketchSense V6 - Magic Notebook Engine
import UniversalSketchCanvas from '../visual-engine/sketch/UniversalSketchCanvasV6';

// Legacy fallback (deprecated)
// import RevolutionarySketch from '../visual-engine/components/RevolutionarySketch';

// COGNITO-OS v4.0 - Teach Me Back (modal-based)
import TeachMeBackModal from './ui/TeachMeBackModal';

// DEPRECATED: FormattedExplanation forces template structure
// import { FormattedExplanation, formatExplanation } from '../utils/explanationFormatter';

/**
 * Check if this is a follow-up/context question
 */
const isFollowUpQuestion = (question) => {
  const q = (question || '').toLowerCase();
  return q.match(/(what did we|earlier|before|previously|last time|you said|you mentioned|continue|go on|more about)/);
};

/**
 * Detect response type from content
 */
const detectResponseType = (response, question) => {
  const q = (question || '').toLowerCase();
  const directives = response?.render_directives || {};
  
  // Check backend directives first - these take priority
  if (directives.greeting_only) return 'greeting';
  if (directives.show_steps) return 'calculation';
  if (directives.prefer_compare_layout) return 'comparison';
  
  // CRITICAL: Follow-up questions should use adaptive markdown, NOT templates
  if (isFollowUpQuestion(question)) return 'follow_up';
  
  // Simple acknowledgments and greetings
  if (q.match(/^(hi|hello|hey|namaste|good morning|good evening)/)) return 'greeting';
  // CRITICAL: Include ALL affirmations - students naturally say these
  if (q.match(/^(thank|thanks|ok|got it|okay|cool|nice|great|awesome|perfect|amazing|excellent|brilliant|fantastic|wonderful|superb|love it|good|understood|i see|makes sense|clear|helpful|wow)[\s!?.]*$/i)) return 'acknowledgment';
  
  // Calculation - needs step-by-step
  if (q.match(/(solve|calculate|find|evaluate|compute|integrate|differentiate)/)) return 'calculation';
  
  // Comparison - needs side-by-side
  if (q.match(/(difference|compare|vs|versus|distinguish|contrast)/)) return 'comparison';
  
  // Short factual questions - direct answer
  if (q.match(/^(who|when|where|which|how many|how much)\b/) && q.length < 50) return 'fact';
  
  // Definition - structured but concise
  if (q.match(/(what is|define|meaning|definition)/)) return 'definition';
  
  // Explanation - the AI decides structure
  if (q.match(/(explain|why|how|describe)/)) return 'explanation';
  
  // Example request
  if (q.match(/(example|for instance|show me)/)) return 'example';
  
  // Default: let AI decide structure
  return 'adaptive';
};

/**
 * Check if visual should be shown
 */
const shouldShowVisual = (question, visualSketch, response) => {
  if (!visualSketch?.svg && !response?.visual_sketch?.svg) return false;
  
  const q = (question || '').toLowerCase();
  
  // Topics that benefit from visuals
  const visualTopics = [
    'force', 'motion', 'gravity', 'friction', 'wave', 'light', 'electricity',
    'atom', 'molecule', 'cell', 'photosynthesis', 'dna', 'mitosis',
    'triangle', 'circle', 'graph', 'geometry', 'pythagoras', 'parabola',
    'circuit', 'momentum', 'energy', 'projectile', 'orbital', 'bond'
  ];
  
  // Don't show for theoretical/text-based topics
  const noVisualTopics = [
    'history', 'gandhi', 'nehru', 'freedom', 'war', 'battle',
    'literature', 'poem', 'story', 'author', 'grammar', 'meaning',
    'define', 'who', 'when', 'date', 'year'
  ];
  
  if (noVisualTopics.some(t => q.includes(t))) return false;
  if (visualTopics.some(t => q.includes(t))) return true;
  
  // Default: show if backend sent a visual
  return !!(response?.render_directives?.show_visual);
};

/**
 * Main Smart Response Component
 * 
 * COGNITO-OS v4.0: Now includes transparency components
 * - Agent Avatar: Shows which agent helped
 * - Verification Badge: Shows trust signals
 * - Reasoning Panel: Shows AI thinking process
 * - Learning Path: Shows knowledge graph connections
 */
const SmartResponse = ({ 
  response, 
  question = '',
  visualSketch = null,
  onFollowUp,
  onInteraction,
  isStreaming = false,
  whiteboardVisual = null
}) => {
  // State for visual expand/collapse - DEFAULT COLLAPSED so user reads text first
  const [isVisualExpanded, setIsVisualExpanded] = useState(false);
  
  // COGNITO-OS v4.0 - Extract transparency data from response
  const cognitoData = useMemo(() => {
    if (!response) return null;
    
    const metadata = response.metadata || {};
    const verification = response.verification || {};
    const knowledgeGraph = metadata.knowledge_graph || null;
    const learningPath = response.learning_path || [];
    
    // Determine which agent was primary
    const agentsUsed = metadata.agents_used || [];
    let primaryAgent = 'mentor';
    if (agentsUsed.includes('professor')) primaryAgent = 'professor';
    if (agentsUsed.includes('doubt_resolver')) primaryAgent = 'doubt_resolver';
    if (agentsUsed.includes('exam_coach')) primaryAgent = 'exam_coach';
    if (metadata.used_doubt_resolver) primaryAgent = 'doubt_resolver';
    
    // Build verification status
    const verificationStatus = {
      math: {
        status: verification.status === 'verified' ? 'verified' : 'not_checked',
        confidence: verification.confidence || 0.5
      },
      source: {
        status: response.rag?.curriculum_aligned ? 'verified' : 'not_checked'
      },
      logic: {
        status: verification.status === 'verified' ? 'verified' : 'not_checked'
      }
    };
    
    // Get sources
    const sources = response.rag?.sources_used || [];
    
    // Build reasoning chain from metadata
    const reasoningChain = metadata.reasoning_chain || [];
    const toolsUsed = metadata.tools_used || [];
    
    // COGNITO-OS v4.0: Always show transparency for educational content
    // Only hide for greetings/acknowledgments (determined in render)
    const showTransparency = metadata.cognito_os_enabled !== false; // Default to TRUE
    
    return {
      primaryAgent,
      agentsUsed,
      verification: verificationStatus,
      sources,
      reasoningChain,
      toolsUsed,
      knowledgeGraph,
      learningPath,
      confidence: verification.confidence || 0.75,
      complexity: metadata.complexity || 'standard',
      showTransparency
    };
  }, [response]);
  const responseType = useMemo(() => 
    detectResponseType(response, question), 
    [response, question]
  );
  
  const showVisual = useMemo(() => 
    shouldShowVisual(question, visualSketch, response),
    [question, visualSketch, response]
  );

  // Extract content from response
  const content = useMemo(() => {
    if (!response) return null;
    
    // CRITICAL: If response itself is a string, wrap it properly
    if (typeof response === 'string') {
      return {
        mainContent: response,
        greeting: null,
        metaphor: null,
        example: null,
        keyTakeaways: null,
        practiceProblems: null,
        steps: null,
        formula: null,
        explanation: null,
        quickFollowUps: []
      };
    }
    
    // CRITICAL: If response is not an object, return null
    if (typeof response !== 'object' || Array.isArray(response)) {
      console.warn('⚠️ SmartResponse: Invalid response type', typeof response);
      return null;
    }
    
    // Handle different response structures - be VERY robust
    const defaultView = response.default_view || {};
    const progressive = response.progressive_sections || {};
    const dualResponse = response.dual_response || {};
    
    // Helper function to safely extract string content
    const safeString = (value) => {
      if (typeof value === 'string') return value;
      if (typeof value === 'number') return String(value);
      if (Array.isArray(value)) return value.map(String).join('\n\n');
      if (value && typeof value === 'object') {
        // If it's an object, try to extract text/content field
        return value.text || value.content || value.message || JSON.stringify(value);
      }
      return null;
    };
    
    // Try multiple sources for main content (prioritize actual explanation)
    let mainContent = null;
    
    // Priority 1: Progressive sections explanation
    const progExplanation = safeString(progressive.explanation);
    if (progExplanation && progExplanation.length > 50) {
      mainContent = progExplanation;
    }
    // Priority 2: Main content
    else if (defaultView.main_content) {
      const mainContentValue = typeof defaultView.main_content === 'object' 
        ? defaultView.main_content.content || defaultView.main_content.text
        : defaultView.main_content;
      const safeMain = safeString(mainContentValue);
      if (safeMain && safeMain.length > 50) {
        mainContent = safeMain;
      }
    }
    // Priority 3: Dual response mentor content
    else if (dualResponse.mentor) {
      const mentorContent = safeString(dualResponse.mentor.content || dualResponse.mentor.text);
      if (mentorContent && mentorContent.length > 50) {
        mainContent = mentorContent;
      }
    }
    // Priority 4: Direct main_content string
    else if (typeof defaultView.main_content === 'string' && defaultView.main_content.length > 50) {
      mainContent = defaultView.main_content;
    }
    // Priority 5: Metaphor text as fallback
    else if (defaultView.metaphor) {
      const metaphorText = safeString(defaultView.metaphor.text || defaultView.metaphor);
      if (metaphorText && metaphorText.length > 50) {
        mainContent = metaphorText;
      }
    }
    // Priority 6: Key takeaways joined
    else if (progressive.key_takeaways) {
      const takeaways = safeString(progressive.key_takeaways);
      if (takeaways && takeaways.length > 10) {
        mainContent = takeaways;
      }
    }
    // Priority 7: Greeting as last resort
    else if (defaultView.greeting) {
      const greetingText = safeString(defaultView.greeting);
      if (greetingText && greetingText.length > 20) {
        mainContent = greetingText;
      }
    }
    
    // CRITICAL: Ensure mainContent is always a string or null, never an object
    if (mainContent && typeof mainContent !== 'string') {
      console.warn('⚠️ SmartResponse: mainContent is not a string, converting:', typeof mainContent);
      mainContent = safeString(mainContent) || null;
    }
    
    console.log('📝 SmartResponse content extraction:', {
      hasMainContent: !!mainContent,
      mainContentType: typeof mainContent,
      mainContentLength: mainContent?.length || 0,
      defaultView: Object.keys(defaultView),
      progressive: Object.keys(progressive)
    });
    
    return {
      greeting: safeString(defaultView.greeting),
      mainContent: mainContent, // Always string or null
      metaphor: safeString(defaultView.metaphor?.text || defaultView.metaphor),
      example: safeString(defaultView.indian_example),
      keyTakeaways: Array.isArray(progressive.key_takeaways) 
        ? progressive.key_takeaways.map(String)
        : safeString(progressive.key_takeaways),
      practiceProblems: safeString(progressive.practice_problem),
      steps: Array.isArray(progressive.strategy?.steps || progressive.steps)
        ? (progressive.strategy?.steps || progressive.steps).map(String)
        : safeString(progressive.strategy?.steps || progressive.steps),
      formula: safeString(progressive.formula),
      explanation: safeString(progressive.explanation),
      quickFollowUps: Array.isArray(defaultView.interactive_options)
        ? defaultView.interactive_options.map(o => String(o.button_text || o.text || o))
        : []
    };
  }, [response]);

  if (!content) return null;

  // COGNITO-OS v4.0 - Render response with transparency wrapper
  const renderMainContent = () => {
    switch (responseType) {
      case 'greeting':
        return <GreetingResponse content={content} />;
      
      case 'acknowledgment':
        return <AcknowledgmentResponse content={content} />;
    
    case 'calculation':
      return (
        <CalculationResponse 
          content={content} 
          showVisual={showVisual}
          visualSketch={visualSketch}
          question={question}
          response={response}
        />
      );
    
    case 'comparison':
      return <ComparisonResponse content={content} />;
    
    case 'definition':
      return (
        <DefinitionResponse 
          content={content}
          showVisual={showVisual}
          visualSketch={visualSketch}
          question={question}
          response={response}
        />
      );
    
    case 'example':
      return <ExampleResponse content={content} />;
    
    case 'follow_up':
    case 'adaptive':
      // For follow-ups and adaptive responses, use clean markdown
      // The AI decides structure, not the frontend
      if (!content.mainContent || typeof content.mainContent !== 'string') {
        return null;
      }
      return (
        <motion.div 
          className="space-y-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <AdaptiveMarkdown content={content.mainContent} />
          {showVisual && (
            <VisualSketchViewer
              svg={visualSketch?.svg || response?.visual_sketch?.svg}
              question={question}
              embedded={true}
            />
          )}
        </motion.div>
      );
    
    case 'fact':
      // Short factual answer - minimal formatting
      if (!content.mainContent || typeof content.mainContent !== 'string') {
        return null;
      }
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-gray-800 dark:text-gray-200"
        >
          <AdaptiveMarkdown content={content.mainContent} />
        </motion.div>
      );
    
    case 'explanation':
    default:
      return (
        <ExplanationResponse 
          content={content}
          showVisual={showVisual}
          visualSketch={visualSketch}
          question={question}
          response={response}
          onFollowUp={onFollowUp}
          whiteboardVisual={whiteboardVisual}
          isVisualExpanded={isVisualExpanded}
          setIsVisualExpanded={setIsVisualExpanded}
          isStreaming={isStreaming}
        />
      );
    }
  };

  // COGNITO-OS v4.0 - Clean answer only
  const isSimpleResponse = responseType === 'greeting' || responseType === 'acknowledgment';
  
  // Teach Me Back Modal - show for explanation responses (not greetings, not short facts)
  const [showTeachMeBackModal, setShowTeachMeBackModal] = useState(false);
  const showTeachMeBackOption = responseType === 'explanation' && content?.mainContent?.length > 200;
  
  // Interaction states
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null); // 'helpful' | 'not_helpful'
  const [bookmarked, setBookmarked] = useState(false);
  
  // Copy to clipboard
  const handleCopy = useCallback(() => {
    const textToCopy = content?.mainContent || '';
    if (textToCopy) {
      navigator.clipboard.writeText(textToCopy).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  }, [content?.mainContent]);
  
  // Handle feedback - sends to backend for quality improvement
  const handleFeedback = useCallback(async (type) => {
    setFeedback(type);
    
    // Send to backend for tracking
    try {
      await apiClient.post('/api/analytics/feedback', {
        feedback_type: type,
        question: question,
        response_preview: content?.mainContent?.substring(0, 300)
      });
    } catch (error) {
      console.log('Feedback tracking failed (non-critical):', error);
    }
    
    // Notify parent component
    if (onInteraction) {
      onInteraction(type === 'helpful' ? 'feedback_positive' : 'feedback_negative');
    }
  }, [onInteraction, question, content?.mainContent]);
  
  // Show interaction bar for non-greeting responses with content
  const showInteractionBar = !isSimpleResponse && content?.mainContent?.length > 50;
  
  return (
    <div className="smart-response-container">
      {/* CLEAN FINAL ANSWER - No panels, no badges, no chips, just content */}
      {renderMainContent()}
      
      {/* INTERACTION BAR - Copy, Feedback, Bookmark */}
      {showInteractionBar && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-5 pt-4 border-t border-gray-100 dark:border-gray-800"
        >
          <div className="flex items-center justify-between flex-wrap gap-3">
            {/* Left side - Feedback */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400 dark:text-gray-500 mr-1">Was this helpful?</span>
              <button
                onClick={() => handleFeedback('helpful')}
                className={`p-2 rounded-lg transition-all duration-200 ${
                  feedback === 'helpful'
                    ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 hover:text-emerald-600'
                }`}
                title="Yes, helpful!"
              >
                <ThumbsUp className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleFeedback('not_helpful')}
                className={`p-2 rounded-lg transition-all duration-200 ${
                  feedback === 'not_helpful'
                    ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600'
                }`}
                title="Not helpful"
              >
                <ThumbsDown className="w-4 h-4" />
              </button>
              {feedback && (
                <motion.span 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`text-xs font-medium ${
                    feedback === 'helpful' ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-500 dark:text-gray-400'
                  }`}
                >
                  {feedback === 'helpful' ? 'Thanks! 🙌' : 'We\'ll improve'}
                </motion.span>
              )}
            </div>
            
            {/* Right side - Actions */}
            <div className="flex items-center gap-2">
              {/* Copy button */}
              <button
                onClick={handleCopy}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                  copied
                    ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-purple-100 dark:hover:bg-purple-900/30 hover:text-purple-600 dark:hover:text-purple-400'
                }`}
                title="Copy response"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
              
              {/* Bookmark button */}
              <button
                onClick={() => setBookmarked(!bookmarked)}
                className={`p-2 rounded-lg transition-all duration-200 ${
                  bookmarked
                    ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-amber-50 dark:hover:bg-amber-900/20 hover:text-amber-600'
                }`}
                title={bookmarked ? 'Saved!' : 'Save for later'}
              >
                <Bookmark className={`w-4 h-4 ${bookmarked ? 'fill-current' : ''}`} />
              </button>
            </div>
          </div>
        </motion.div>
      )}
      
      {/* TEACH ME BACK - Subtle invitation for complex explanations */}
      {showTeachMeBackOption && (
        <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800">
          <button
            onClick={() => setShowTeachMeBackModal(true)}
            className="text-sm text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 flex items-center gap-2 transition-colors"
          >
            <span>💭</span>
            <span>Think you got it? Try explaining it back</span>
          </button>
        </div>
      )}
      
      {/* TEACH ME BACK MODAL - Full screen experience */}
      <TeachMeBackModal
        isOpen={showTeachMeBackModal}
        onClose={() => setShowTeachMeBackModal(false)}
        concept={question?.substring(0, 100) || 'this concept'}
        originalExplanation={content?.mainContent || ''}
      />
    </div>
  );
};

// ============ Response Type Components ============

/**
 * Greeting - Simple, friendly, minimal, globally impressive
 * No subject lists, no robotic tone - just warm & welcoming
 * 
 * FIX: No hardcoded fallback - if no real content exists, return null
 * to prevent showing placeholder messages during streaming
 */
const GreetingResponse = ({ content }) => {
  // Get the greeting text - prioritize greeting field
  // FIX: NO hardcoded fallback - don't render anything if no real content
  const greetingText = content.greeting || content.mainContent;
  const tagline = content.mainContent && content.greeting ? content.mainContent : null;
  
  // FIX: If there's no actual content, don't render anything
  // This prevents showing placeholder text during streaming
  if (!greetingText || greetingText.trim().length === 0) {
    return null;
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-2"
    >
      {/* Main greeting - prominent */}
      <div className="text-gray-900 dark:text-gray-100 font-medium" style={{ fontSize: '17px', lineHeight: '1.6' }}>
        <AdaptiveMarkdown content={greetingText} />
      </div>
      
      {/* Optional tagline - subtle */}
      {tagline && tagline !== greetingText && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-gray-600 dark:text-gray-400"
          style={{ fontSize: '15px', lineHeight: '1.5' }}
        >
          <AdaptiveMarkdown content={tagline} />
        </motion.div>
      )}
    </motion.div>
  );
};

/**
 * Acknowledgment - Very short response
 * FIX: No hardcoded fallback - if no content, return null
 */
const AcknowledgmentResponse = ({ content }) => {
  // CRITICAL: Ensure content is valid
  if (!content || typeof content !== 'object') {
    return null;
  }
  
  // FIX: Don't show hardcoded fallback during streaming
  if (!content.mainContent || typeof content.mainContent !== 'string' || content.mainContent.trim().length === 0) {
    return null;
  }
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="text-gray-800 dark:text-gray-200 leading-relaxed"
      style={{ fontSize: '16px', lineHeight: '1.75' }}
    >
      <AdaptiveMarkdown content={content.mainContent} />
    </motion.div>
  );
};

/**
 * Calculation - Focus on step-by-step solution
 * FIXED: Uses AdaptiveMarkdown for proper LaTeX rendering
 */
const CalculationResponse = ({ content, showVisual, visualSketch, question, response }) => {
  // CRITICAL: Ensure content is valid
  if (!content || typeof content !== 'object' || !content.mainContent || typeof content.mainContent !== 'string') {
    return null;
  }
  
  return (
    <motion.div 
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Main content with full markdown/LaTeX support */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-5 border border-blue-100 dark:border-blue-800">
        <div className="flex items-center space-x-2 mb-4">
          <Calculator className="w-5 h-5 text-blue-600" />
          <h4 className="font-semibold text-blue-800 dark:text-blue-300">Solution</h4>
        </div>
        
        {/* Use AdaptiveMarkdown for full LaTeX/table support */}
        <AdaptiveMarkdown content={content.mainContent} />
    </div>

      {/* Visual if needed */}
      {showVisual && (
        <VisualSketchViewer
          svg={visualSketch?.svg || response?.visual_sketch?.svg}
          question={question}
          embedded={true}
        />
      )}
    </motion.div>
  );
};

/**
 * Definition - Short answer
 * REFACTORED: Uses AdaptiveMarkdown instead of forced template
 */
const DefinitionResponse = ({ content, showVisual, visualSketch, question, response }) => {
  // CRITICAL: Ensure content is valid
  if (!content || typeof content !== 'object' || !content.mainContent || typeof content.mainContent !== 'string') {
    return null;
  }
  
  return (
    <motion.div 
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Direct Answer - Clean markdown */}
      <AdaptiveMarkdown content={content.mainContent} />

      {/* Visual if needed */}
      {showVisual && (
        <VisualSketchViewer
          svg={visualSketch?.svg || response?.visual_sketch?.svg}
          question={question}
          embedded={true}
        />
      )}
    </motion.div>
  );
};

/**
 * Comparison - Table/side-by-side format
 * FIXED: Uses AdaptiveMarkdown for proper table and LaTeX rendering
 */
const ComparisonResponse = ({ content }) => {
  // CRITICAL: Ensure content is valid
  if (!content || typeof content !== 'object' || !content.mainContent || typeof content.mainContent !== 'string') {
    return null;
  }
  
  return (
    <motion.div 
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Main comparison content - AdaptiveMarkdown handles tables properly */}
      <AdaptiveMarkdown content={content.mainContent} />
    </motion.div>
  );
};

/**
 * Example - Focus on practical examples
 * FIXED: Uses AdaptiveMarkdown for proper formatting
 */
const ExampleResponse = ({ content }) => {
  // CRITICAL: Ensure content is valid
  if (!content || typeof content !== 'object') {
    return null;
  }
  
  const exampleContent = typeof content.example === 'string' ? content.example : 
                         (typeof content.mainContent === 'string' ? content.mainContent : null);
  
  if (!exampleContent) {
    return null;
  }
  
  return (
  <motion.div 
    className="space-y-4"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
  >
    {/* Main Example */}
    <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-5 border border-green-100 dark:border-green-800">
      <div className="flex items-center space-x-2 mb-3">
        <Lightbulb className="w-5 h-5 text-green-600" />
        <h4 className="font-semibold text-green-800 dark:text-green-300">Example</h4>
      </div>
      <AdaptiveMarkdown content={exampleContent} />
    </div>
  </motion.div>
  );
};

/**
 * Explanation - Full explanation with whiteboard visual
 * 
 * NEXT-GEN: Uses WhiteboardSketch for animated, progressive visuals
 * Philosophy: No MCQs, pure understanding, Indian context
 */
const ExplanationResponse = ({ 
  content, 
  showVisual, 
  visualSketch, 
  question, 
  response, 
  onFollowUp,
  whiteboardVisual,
  isVisualExpanded,
  setIsVisualExpanded,
  isStreaming = false
}) => {
  // CRITICAL: Ensure content is valid
  if (!content || typeof content !== 'object') {
    return null;
  }
  
  const hasContent = content.mainContent && typeof content.mainContent === 'string' && content.mainContent.length > 10;
  
  // Whiteboard visual is the ONLY visual system
  const hasWhiteboardVisual = whiteboardVisual && whiteboardVisual.concept;
  const hasAnyVisual = hasWhiteboardVisual;

  return (
    <motion.div 
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Main Content - Rendered as clean markdown */}
      {/* REMOVED: "Generating explanation" warning - it was showing incorrectly */}
      {/* The thinking indicator in AITutorNeuroSymbolic handles loading state */}
      {hasContent && (
        <AdaptiveMarkdown content={content.mainContent} />
      )}

      {/* 🚀 SketchSense V5.0 - Universal Visual Engine */}
      {hasAnyVisual && (
        <div className="visual-section mt-6">
          <AnimatePresence>
            {isVisualExpanded ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
              >
                {/* Magic Notebook Engine V6 - Complete System */}
                <MagicNotebookEngine
                  question={question}
                  context={{
                    subject: whiteboardVisual?.subject || 'physics',
                    level: 'high_school',
                  }}
                  preGeneratedBlueprint={whiteboardVisual}
                  showControls={true}
                  showNarrative={true}
                  height={500}
                  width={600}
                  enableValidation={true}
                  enableFeedback={true}
                  style={{ minHeight: '400px', borderRadius: '12px' }}
                />
                
                {/* Collapse button */}
                <button
                  onClick={() => setIsVisualExpanded?.(false)}
                  className="w-full mt-2 py-1.5 text-xs text-gray-500 hover:text-gray-700 flex items-center justify-center gap-1 transition-colors"
                >
                  <ChevronUp className="w-3 h-3" />
                  Hide visual
                </button>
              </motion.div>
            ) : (
              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => setIsVisualExpanded?.(true)}
                className="w-full py-4 bg-gradient-to-r from-orange-50 via-amber-50 to-yellow-50 hover:from-orange-100 hover:via-amber-100 hover:to-yellow-100 rounded-xl border-2 border-dashed border-orange-300 hover:border-orange-400 flex items-center justify-center gap-3 transition-all shadow-sm hover:shadow-md"
              >
                <span className="text-2xl">🎬</span>
                <div className="text-left">
                  <span className="text-sm font-semibold text-orange-700 block">Watch Visual Explanation</span>
                  <span className="text-xs text-orange-500">Click to see animated diagram</span>
                </div>
                <ChevronDown className="w-5 h-5 text-orange-500 animate-bounce" />
              </motion.button>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Follow-up suggestions */}
      {content.quickFollowUps?.length > 0 && (
        <div className="pt-3 border-t border-gray-100 dark:border-gray-700">
          <p className="text-xs text-gray-500 mb-2">Related questions:</p>
          <div className="flex flex-wrap gap-2">
            {content.quickFollowUps.slice(0, 3).map((followUp, i) => (
              <button
                key={i}
                onClick={() => onFollowUp?.(followUp)}
                className="px-3 py-1.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                {followUp}
              </button>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default SmartResponse;

