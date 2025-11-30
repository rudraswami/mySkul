/**
 * Adaptive Response Component
 * Renders AI responses DYNAMICALLY based on content - NOT a fixed template!
 * 
 * Like ChatGPT/Gemini - different questions get different response structures.
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  Lightbulb, Calculator, BookOpen, AlertTriangle, 
  Target, HelpCircle, CheckCircle, ArrowRight,
  Zap, Brain, List
} from 'lucide-react';
import { MarkdownParagraph } from '../utils/markdownRenderer';
import VisualSketchViewer from './visual/VisualSketchViewer';

/**
 * Main Adaptive Response Component
 * Automatically decides what to show based on the response content
 */
const AdaptiveResponse = ({ 
  response, 
  question = '',
  visualSketch = null,
  onFollowUp,
}) => {
  // Parse the response - it might be a string or structured object
  const parsedContent = useMemo(() => {
    if (!response) return null;
    
    // If it's already structured from backend
    if (typeof response === 'object' && response.content) {
      return parseStructuredResponse(response);
    }
    
    // If it's a plain string, parse it intelligently
    if (typeof response === 'string') {
      return parseStringResponse(response);
    }
    
    // Handle the dual_response format from current backend
    if (response.dual_response) {
      return parseDualResponse(response.dual_response);
    }
    
    return parseStructuredResponse(response);
  }, [response]);

  if (!parsedContent) {
    return <div className="text-gray-500">No response available</div>;
  }

  // Determine what sections to show based on parsed content
  const hasMultipleSections = Object.keys(parsedContent.sections || {}).length > 1;
  
  return (
    <motion.div 
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Main Content - Always show if exists */}
      {parsedContent.mainContent && (
        <MainContent content={parsedContent.mainContent} isSimple={!hasMultipleSections} />
      )}

      {/* Steps - Only if present */}
      {parsedContent.sections?.steps && (
        <StepsSection steps={parsedContent.sections.steps} />
      )}

      {/* Example - Only if present */}
      {parsedContent.sections?.example && (
        <ExampleSection example={parsedContent.sections.example} />
      )}

      {/* Visual - Only if topic benefits from it AND visual is available */}
      {parsedContent.showVisual && visualSketch && (
        <VisualSection visualSketch={visualSketch} question={question} />
      )}

      {/* Formula Box - Only if present */}
      {parsedContent.sections?.formula && (
        <FormulaSection formula={parsedContent.sections.formula} />
      )}

      {/* Memory Hook - Only if present AND not a simple answer */}
      {parsedContent.sections?.memoryHook && hasMultipleSections && (
        <MemoryHookSection hook={parsedContent.sections.memoryHook} />
      )}

      {/* Common Mistakes - Only if present */}
      {parsedContent.sections?.mistakes && (
        <MistakesSection mistakes={parsedContent.sections.mistakes} />
      )}

      {/* Follow-up - Only if present */}
      {parsedContent.sections?.followUp && (
        <FollowUpSection suggestions={parsedContent.sections.followUp} onFollowUp={onFollowUp} />
      )}
    </motion.div>
  );
};

/**
 * Parse structured response from backend
 */
function parseStructuredResponse(response) {
  const sections = {};
  let mainContent = '';
  let showVisual = false;

  // Handle render_directives if present
  const directives = response.render_directives || {};
  showVisual = directives.show_visual || false;

  // Extract main content
  if (response.default_view?.main_content?.content) {
    mainContent = response.default_view.main_content.content;
  } else if (response.content) {
    mainContent = typeof response.content === 'string' ? response.content : '';
  } else if (response.text) {
    mainContent = response.text;
  }

  // Extract sections based on directives
  if (directives.show_steps && response.progressive_sections?.steps) {
    sections.steps = response.progressive_sections.steps;
  }

  if (directives.show_examples && response.progressive_sections?.examples) {
    sections.example = response.progressive_sections.examples;
  }

  if (directives.show_formula_box && response.progressive_sections?.formulas) {
    sections.formula = response.progressive_sections.formulas;
  }

  if (directives.show_memory_hook && response.progressive_sections?.memory_hook) {
    sections.memoryHook = response.progressive_sections.memory_hook;
  }

  if (directives.show_common_mistakes && response.progressive_sections?.mistakes) {
    sections.mistakes = response.progressive_sections.mistakes;
  }

  if (directives.show_follow_up && response.progressive_sections?.follow_up) {
    sections.followUp = response.progressive_sections.follow_up;
  }

  return { mainContent, sections, showVisual };
}

/**
 * Parse plain string response - extract sections if formatted
 */
function parseStringResponse(text) {
  const sections = {};
  let mainContent = text;
  let showVisual = false;

  // Check for section markers in the text
  const stepMatch = text.match(/(?:steps?:|solution:)([\s\S]*?)(?=\n\n|example:|formula:|$)/i);
  if (stepMatch) {
    sections.steps = stepMatch[1].trim();
  }

  const exampleMatch = text.match(/(?:example:|for example:)([\s\S]*?)(?=\n\n|formula:|$)/i);
  if (exampleMatch) {
    sections.example = exampleMatch[1].trim();
  }

  const formulaMatch = text.match(/(?:formula:|equation:)([\s\S]*?)(?=\n\n|$)/i);
  if (formulaMatch) {
    sections.formula = formulaMatch[1].trim();
  }

  // If no sections found, just use the whole text as main content
  if (Object.keys(sections).length === 0) {
    mainContent = text;
  }

  return { mainContent, sections, showVisual };
}

/**
 * Parse dual_response format from current backend
 */
function parseDualResponse(dualResponse) {
  const sections = {};
  let mainContent = '';
  let showVisual = false;

  // Extract mentor response as main content
  if (dualResponse.mentor?.content) {
    mainContent = dualResponse.mentor.content;
  }

  // Check if visual should be shown
  if (dualResponse.visual_data || dualResponse.visual_sketch) {
    showVisual = true;
  }

  return { mainContent, sections, showVisual };
}

// ============ Section Components ============

const MainContent = ({ content, isSimple }) => (
  <div className={`${isSimple ? '' : 'bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700'}`}>
    <div className="prose prose-sm dark:prose-invert max-w-none">
      <MarkdownParagraph content={content} />
    </div>
  </div>
);

const StepsSection = ({ steps }) => (
  <motion.div 
    className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-100 dark:border-blue-800"
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <div className="flex items-center space-x-2 mb-3">
      <List className="w-5 h-5 text-blue-600" />
      <h4 className="font-semibold text-blue-800 dark:text-blue-300">Solution Steps</h4>
    </div>
    <div className="prose prose-sm dark:prose-invert max-w-none">
      <MarkdownParagraph content={steps} />
    </div>
  </motion.div>
);

const ExampleSection = ({ example }) => (
  <motion.div 
    className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 border border-green-100 dark:border-green-800"
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <div className="flex items-center space-x-2 mb-3">
      <Lightbulb className="w-5 h-5 text-green-600" />
      <h4 className="font-semibold text-green-800 dark:text-green-300">Example</h4>
    </div>
    <div className="prose prose-sm dark:prose-invert max-w-none">
      <MarkdownParagraph content={example} />
    </div>
  </motion.div>
);

const VisualSection = ({ visualSketch, question }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <VisualSketchViewer 
      svg={visualSketch?.svg}
      metaphors={visualSketch?.metaphors}
      estimatedMarks={visualSketch?.estimated_marks}
      question={question}
      embedded={true}
    />
  </motion.div>
);

const FormulaSection = ({ formula }) => (
  <motion.div 
    className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border border-purple-100 dark:border-purple-800"
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <div className="flex items-center space-x-2 mb-3">
      <Calculator className="w-5 h-5 text-purple-600" />
      <h4 className="font-semibold text-purple-800 dark:text-purple-300">Formula</h4>
    </div>
    <div className="font-mono text-lg text-center py-2 bg-white dark:bg-gray-800 rounded-lg">
      {formula}
    </div>
  </motion.div>
);

const MemoryHookSection = ({ hook }) => (
  <motion.div 
    className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-4 border border-yellow-100 dark:border-yellow-800"
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <div className="flex items-center space-x-2 mb-3">
      <Brain className="w-5 h-5 text-yellow-600" />
      <h4 className="font-semibold text-yellow-800 dark:text-yellow-300">Memory Trick</h4>
    </div>
    <p className="text-yellow-900 dark:text-yellow-200">{hook}</p>
  </motion.div>
);

const MistakesSection = ({ mistakes }) => (
  <motion.div 
    className="bg-red-50 dark:bg-red-900/20 rounded-xl p-4 border border-red-100 dark:border-red-800"
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <div className="flex items-center space-x-2 mb-3">
      <AlertTriangle className="w-5 h-5 text-red-600" />
      <h4 className="font-semibold text-red-800 dark:text-red-300">Common Mistakes</h4>
    </div>
    <div className="prose prose-sm dark:prose-invert max-w-none text-red-900 dark:text-red-200">
      <MarkdownParagraph content={mistakes} />
    </div>
  </motion.div>
);

const FollowUpSection = ({ suggestions, onFollowUp }) => {
  const followUps = Array.isArray(suggestions) ? suggestions : [suggestions];
  
  return (
    <motion.div 
      className="pt-3 border-t border-gray-100 dark:border-gray-700"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.3 }}
    >
      <p className="text-sm text-gray-500 mb-2">Related questions:</p>
      <div className="flex flex-wrap gap-2">
        {followUps.slice(0, 3).map((suggestion, i) => (
          <button
            key={i}
            onClick={() => onFollowUp?.(suggestion)}
            className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center space-x-1"
          >
            <span>{suggestion}</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        ))}
      </div>
    </motion.div>
  );
};

export default AdaptiveResponse;












