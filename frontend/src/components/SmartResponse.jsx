/**
 * Smart Response Component
 * 
 * Intelligent response renderer that adapts structure based on question type.
 * Like ChatGPT/Gemini - different questions get different response structures.
 * 
 * NO MORE STATIC TEMPLATE!
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  Lightbulb, BookOpen, Target, AlertTriangle, 
  Calculator, CheckCircle, ArrowRight, Brain,
  Zap, HelpCircle, List, Info
} from 'lucide-react';
import { MarkdownParagraph } from '../utils/markdownRenderer';
import VisualSketchViewer from './visual/VisualSketchViewer';

/**
 * Detect response type from content
 */
const detectResponseType = (response, question) => {
  const q = (question || '').toLowerCase();
  const directives = response?.render_directives || {};
  
  // Check backend directives first
  if (directives.greeting_only) return 'greeting';
  if (directives.show_steps) return 'calculation';
  if (directives.prefer_compare_layout) return 'comparison';
  
  // Detect from question
  if (q.match(/^(hi|hello|hey|namaste|good morning|good evening)/)) return 'greeting';
  if (q.match(/(solve|calculate|find|evaluate|compute)/)) return 'calculation';
  if (q.match(/(difference|compare|vs|versus|distinguish)/)) return 'comparison';
  if (q.match(/(what is|define|meaning|definition)/)) return 'definition';
  if (q.match(/(explain|why|how|describe)/)) return 'explanation';
  if (q.match(/(example|for instance)/)) return 'example';
  if (q.match(/(thank|thanks|ok|got it)/)) return 'acknowledgment';
  
  return 'standard';
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
 */
const SmartResponse = ({ 
  response, 
  question = '',
  visualSketch = null,
  onFollowUp,
  onInteraction,
  isStreaming = false
}) => {
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
    
    // Handle different response structures - be VERY robust
    const defaultView = response.default_view || {};
    const progressive = response.progressive_sections || {};
    const dualResponse = response.dual_response || {};
    
    // Try multiple sources for main content (prioritize actual explanation)
    let mainContent = null;
    
    // Priority 1: Progressive sections explanation
    if (progressive.explanation && progressive.explanation.length > 50) {
      mainContent = progressive.explanation;
    }
    // Priority 2: Main content
    else if (defaultView.main_content?.content && defaultView.main_content.content.length > 50) {
      mainContent = defaultView.main_content.content;
    }
    // Priority 3: Dual response mentor content
    else if (dualResponse.mentor?.content && dualResponse.mentor.content.length > 50) {
      mainContent = dualResponse.mentor.content;
    }
    // Priority 4: Direct main_content string
    else if (typeof defaultView.main_content === 'string' && defaultView.main_content.length > 50) {
      mainContent = defaultView.main_content;
    }
    // Priority 5: Metaphor text as fallback
    else if (defaultView.metaphor?.text && defaultView.metaphor.text.length > 50) {
      mainContent = defaultView.metaphor.text;
    }
    // Priority 6: Key takeaways joined
    else if (progressive.key_takeaways?.length > 0) {
      mainContent = Array.isArray(progressive.key_takeaways) 
        ? progressive.key_takeaways.join('\n\n') 
        : progressive.key_takeaways;
    }
    // Priority 7: Greeting as last resort
    else if (defaultView.greeting && defaultView.greeting.length > 20) {
      mainContent = defaultView.greeting;
    }
    
    console.log('📝 SmartResponse content extraction:', {
      hasMainContent: !!mainContent,
      mainContentLength: mainContent?.length || 0,
      defaultView: Object.keys(defaultView),
      progressive: Object.keys(progressive)
    });
    
    return {
      greeting: defaultView.greeting,
      mainContent: mainContent,
      metaphor: defaultView.metaphor?.text,
      example: defaultView.indian_example,
      keyTakeaways: progressive.key_takeaways,
      practiceProblems: progressive.practice_problem,
      steps: progressive.strategy?.steps || progressive.steps,
      formula: progressive.formula,
      explanation: progressive.explanation,
      quickFollowUps: defaultView.interactive_options?.map(o => o.button_text) || []
    };
  }, [response]);

  if (!content) return null;

  // Render based on response type
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
        />
      );
  }
};

// ============ Response Type Components ============

/**
 * Greeting - Simple, friendly, minimal
 */
const GreetingResponse = ({ content }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="text-gray-800 dark:text-gray-200 leading-relaxed"
    style={{ fontSize: '16px', lineHeight: '1.75' }}
  >
    <MarkdownParagraph className="text-gray-800 dark:text-gray-200">
      {content.greeting || content.mainContent || "Hey! How can I help you today? 👋"}
    </MarkdownParagraph>
  </motion.div>
);

/**
 * Acknowledgment - Very short response
 */
const AcknowledgmentResponse = ({ content }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="text-gray-800 dark:text-gray-200 leading-relaxed"
    style={{ fontSize: '16px', lineHeight: '1.75' }}
  >
    <MarkdownParagraph className="text-gray-800 dark:text-gray-200">
      {content.mainContent || "Got it! Let me know if you have any other questions. 😊"}
    </MarkdownParagraph>
  </motion.div>
);

/**
 * Calculation - Focus on step-by-step solution
 */
const CalculationResponse = ({ content, showVisual, visualSketch, question, response }) => (
  <motion.div 
    className="space-y-4"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
  >
    {/* Solution Steps */}
    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-5 border border-blue-100 dark:border-blue-800">
      <div className="flex items-center space-x-2 mb-4">
        <Calculator className="w-5 h-5 text-blue-600" />
        <h4 className="font-semibold text-blue-800 dark:text-blue-300">Solution</h4>
      </div>
      
      {content.steps ? (
        <div className="space-y-3">
          {(Array.isArray(content.steps) ? content.steps : [content.steps]).map((step, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-start space-x-3"
            >
              <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                {i + 1}
              </span>
              <div className="flex-1 pt-0.5">
                <MarkdownParagraph className="text-gray-800 dark:text-gray-200">
                  {typeof step === 'string' ? step : step.content || step.text || JSON.stringify(step)}
                </MarkdownParagraph>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <MarkdownParagraph className="text-gray-800 dark:text-gray-200">
          {content.mainContent}
        </MarkdownParagraph>
      )}
    </div>

    {/* Formula if present */}
    {content.formula && (
      <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border border-purple-100 dark:border-purple-800">
        <div className="flex items-center space-x-2 mb-2">
          <Zap className="w-4 h-4 text-purple-600" />
          <span className="font-medium text-purple-800 dark:text-purple-300 text-sm">Formula Used</span>
        </div>
        <div className="font-mono text-lg text-center py-2 bg-white dark:bg-gray-800 rounded-lg">
          {content.formula}
        </div>
      </div>
    )}

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

/**
 * Definition - Short answer with optional expansion
 */
const DefinitionResponse = ({ content, showVisual, visualSketch, question, response }) => (
  <motion.div 
    className="space-y-4"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
  >
    {/* Direct Answer */}
    <div className="prose prose-sm dark:prose-invert max-w-none">
      <MarkdownParagraph>
        {content.mainContent}
      </MarkdownParagraph>
    </div>

    {/* Example if present */}
    {content.example && (
      <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 border border-green-100 dark:border-green-800">
        <div className="flex items-center space-x-2 mb-2">
          <Lightbulb className="w-4 h-4 text-green-600" />
          <span className="font-medium text-green-800 dark:text-green-300 text-sm">Example</span>
        </div>
        <MarkdownParagraph className="text-gray-800 dark:text-gray-200">
          {content.example}
        </MarkdownParagraph>
      </div>
    )}

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

/**
 * Comparison - Table/side-by-side format
 */
const ComparisonResponse = ({ content }) => (
  <motion.div 
    className="space-y-4"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
  >
    {/* Summary */}
    {content.metaphor && (
      <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl p-4 border border-indigo-100 dark:border-indigo-800 mb-4">
        <MarkdownParagraph className="text-gray-800 dark:text-gray-200">
          {content.metaphor}
        </MarkdownParagraph>
      </div>
    )}

    {/* Main comparison content */}
    <div className="prose prose-sm dark:prose-invert max-w-none">
      <MarkdownParagraph>
        {content.mainContent}
      </MarkdownParagraph>
    </div>

    {/* Key Takeaways */}
    {content.keyTakeaways && (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-4 border border-yellow-100 dark:border-yellow-800">
        <div className="flex items-center space-x-2 mb-2">
          <CheckCircle className="w-4 h-4 text-yellow-600" />
          <span className="font-medium text-yellow-800 dark:text-yellow-300 text-sm">Key Differences</span>
        </div>
        <ul className="space-y-1">
          {(Array.isArray(content.keyTakeaways) ? content.keyTakeaways : [content.keyTakeaways]).map((point, i) => (
            <li key={i} className="flex items-start space-x-2 text-gray-800 dark:text-gray-200 text-sm">
              <span className="text-yellow-600">•</span>
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </div>
    )}
  </motion.div>
);

/**
 * Example - Focus on practical examples
 */
const ExampleResponse = ({ content }) => (
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
      <MarkdownParagraph className="text-gray-800 dark:text-gray-200">
        {content.example || content.mainContent}
      </MarkdownParagraph>
    </div>
  </motion.div>
);

/**
 * Explanation - Full explanation with optional visual and memory hook
 * CRITICAL: Explanation text ALWAYS comes first, visual comes after
 */
const ExplanationResponse = ({ content, showVisual, visualSketch, question, response, onFollowUp }) => {
  // Don't show memory hook if it's too similar to main content
  const showMemoryHook = content.metaphor && 
    content.mainContent && 
    content.mainContent.length > 50 &&
    !content.mainContent.toLowerCase().includes(content.metaphor?.toLowerCase()?.substring(0, 30) || '');

  // Check if we have actual content to display
  const hasContent = content.mainContent && content.mainContent.length > 10;

  return (
    <motion.div 
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* PRIORITY 1: Main Explanation Text - ALWAYS FIRST */}
      {hasContent ? (
        <div className="prose prose-sm dark:prose-invert max-w-none bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
          <MarkdownParagraph className="text-gray-800 dark:text-gray-200 leading-relaxed" style={{ fontSize: '16px', lineHeight: '1.75' }}>
            {content.mainContent}
          </MarkdownParagraph>
        </div>
      ) : (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-4 border border-yellow-200 dark:border-yellow-800">
          <p className="text-yellow-800 dark:text-yellow-300">
            ⚠️ Generating explanation... Please wait.
          </p>
        </div>
      )}

      {/* Example if present */}
      {content.example && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 border border-green-100 dark:border-green-800">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-lg">🇮🇳</span>
            <span className="font-medium text-green-800 dark:text-green-300 text-sm">Real-World Example</span>
          </div>
          <MarkdownParagraph className="text-gray-800 dark:text-gray-200 text-sm">
            {content.example}
          </MarkdownParagraph>
        </div>
      )}

      {/* Memory Hook - Only if adds value */}
      {showMemoryHook && (
        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border border-purple-100 dark:border-purple-800">
          <div className="flex items-center space-x-2 mb-2">
            <Brain className="w-4 h-4 text-purple-600" />
            <span className="font-medium text-purple-800 dark:text-purple-300 text-sm">Memory Hook</span>
          </div>
          <MarkdownParagraph className="text-gray-700 dark:text-gray-300 text-sm italic">
            {content.metaphor}
          </MarkdownParagraph>
        </div>
      )}

      {/* PRIORITY 2: Visual - AFTER explanation text */}
      {showVisual && (
        <VisualSketchViewer
          svg={visualSketch?.svg || response?.visual_sketch?.svg}
          metaphors={visualSketch?.metaphors || response?.visual_sketch?.metaphors || []}
          estimatedMarks={visualSketch?.estimated_marks || response?.visual_sketch?.estimated_marks}
          question={question}
          embedded={true}
        />
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

