/**
 * LearningPathVisualizer - Knowledge Graph Exposure
 * 
 * COGNITO-OS v4.0 - Shows concept connections to students
 * Displays: Current concept, Prerequisites, Applications, Next steps
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MapPin,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  BookOpen,
  Rocket,
  AlertCircle,
  CheckCircle2,
  Circle,
  Star,
  Zap
} from 'lucide-react';

// Concept node component
const ConceptNode = ({ 
  name, 
  type = 'current', // 'prerequisite', 'current', 'next', 'application'
  mastery = null,
  onClick
}) => {
  const getNodeStyle = () => {
    switch (type) {
      case 'prerequisite':
        return {
          bg: 'bg-amber-100 dark:bg-amber-900/40',
          border: 'border-amber-300 dark:border-amber-700',
          text: 'text-amber-800 dark:text-amber-200',
          icon: '📚'
        };
      case 'current':
        return {
          bg: 'bg-violet-100 dark:bg-violet-900/40',
          border: 'border-violet-400 dark:border-violet-600 ring-2 ring-violet-300 dark:ring-violet-700',
          text: 'text-violet-800 dark:text-violet-200',
          icon: '📍'
        };
      case 'next':
        return {
          bg: 'bg-emerald-100 dark:bg-emerald-900/40',
          border: 'border-emerald-300 dark:border-emerald-700',
          text: 'text-emerald-800 dark:text-emerald-200',
          icon: '🚀'
        };
      case 'application':
        return {
          bg: 'bg-blue-100 dark:bg-blue-900/40',
          border: 'border-blue-300 dark:border-blue-700',
          text: 'text-blue-800 dark:text-blue-200',
          icon: '💡'
        };
      default:
        return {
          bg: 'bg-gray-100 dark:bg-gray-800',
          border: 'border-gray-300 dark:border-gray-600',
          text: 'text-gray-700 dark:text-gray-300',
          icon: '•'
        };
    }
  };

  const style = getNodeStyle();

  const getMasteryIndicator = () => {
    if (mastery === null) return null;
    if (mastery >= 80) return <CheckCircle2 className="w-3 h-3 text-emerald-500" />;
    if (mastery >= 50) return <Circle className="w-3 h-3 text-amber-500" />;
    return <AlertCircle className="w-3 h-3 text-red-500" />;
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`px-3 py-2 rounded-xl border-2 ${style.bg} ${style.border} ${style.text} 
        transition-all duration-200 flex items-center gap-2 text-sm font-medium shadow-sm hover:shadow-md`}
    >
      <span>{style.icon}</span>
      <span className="truncate max-w-[120px]">{name}</span>
      {getMasteryIndicator()}
    </motion.button>
  );
};

// Connection line between concepts
const ConnectionLine = ({ direction = 'right' }) => (
  <div className={`flex items-center ${direction === 'down' ? 'flex-col h-6' : 'w-8'}`}>
    {direction === 'down' ? (
      <div className="w-0.5 h-full bg-gradient-to-b from-gray-300 to-gray-400 dark:from-gray-600 dark:to-gray-500" />
    ) : (
      <>
        <div className="flex-1 h-0.5 bg-gradient-to-r from-gray-300 to-gray-400 dark:from-gray-600 dark:to-gray-500" />
        <ArrowRight className="w-4 h-4 text-gray-400" />
      </>
    )}
  </div>
);

const LearningPathVisualizer = ({ 
  knowledgeGraph = null,
  currentConcept = null,
  prerequisites = [],
  applications = [],
  nextSteps = [],
  learningPath = [],
  userMastery = {}
}) => {
  const [expanded, setExpanded] = useState(false);

  // If no data provided, show placeholder
  if (!currentConcept && !knowledgeGraph) {
    return null;
  }

  // Extract data from knowledge graph if provided
  const concept = currentConcept || knowledgeGraph?.main_concept || 'Current Topic';
  const prereqs = prerequisites.length > 0 ? prerequisites : (knowledgeGraph?.prerequisites || []);
  const apps = applications.length > 0 ? applications : (knowledgeGraph?.applications || []);
  const nextTopics = nextSteps.length > 0 ? nextSteps : apps.slice(0, 2);

  return (
    <div className="mt-4 rounded-xl border border-indigo-200 dark:border-indigo-800 overflow-hidden bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-900/30 dark:to-blue-900/30">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-indigo-100/50 dark:hover:bg-indigo-800/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-indigo-100 dark:bg-indigo-800">
            <MapPin className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div className="text-left">
            <p className="font-semibold text-indigo-700 dark:text-indigo-300">
              📚 Your Learning Path
            </p>
            <p className="text-xs text-indigo-500 dark:text-indigo-400">
              See how this connects to other concepts
            </p>
          </div>
        </div>
        
        {expanded ? (
          <ChevronUp className="w-5 h-5 text-indigo-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-indigo-400" />
        )}
      </button>

      {/* Expanded Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 border-t border-indigo-200 dark:border-indigo-700 pt-4">
              {/* Visual Graph */}
              <div className="flex flex-col items-center gap-2 py-4">
                {/* Prerequisites Row */}
                {prereqs.length > 0 && (
                  <>
                    <div className="flex items-center gap-2 flex-wrap justify-center">
                      <span className="text-xs text-amber-600 dark:text-amber-400 font-medium">
                        📖 Review first:
                      </span>
                      {prereqs.slice(0, 3).map((prereq, i) => (
                        <ConceptNode
                          key={i}
                          name={typeof prereq === 'string' ? prereq : prereq.name}
                          type="prerequisite"
                          mastery={userMastery[prereq?.id || prereq]}
                        />
                      ))}
                    </div>
                    <ConnectionLine direction="down" />
                  </>
                )}

                {/* Current Concept */}
                <div className="flex items-center gap-2">
                  <span className="text-xs text-violet-600 dark:text-violet-400 font-medium">
                    You're here:
                  </span>
                  <ConceptNode
                    name={concept}
                    type="current"
                    mastery={userMastery[concept]}
                  />
                </div>

                {/* Next Steps Row */}
                {nextTopics.length > 0 && (
                  <>
                    <ConnectionLine direction="down" />
                    <div className="flex items-center gap-2 flex-wrap justify-center">
                      <span className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                        🚀 Next:
                      </span>
                      {nextTopics.slice(0, 3).map((next, i) => (
                        <ConceptNode
                          key={i}
                          name={typeof next === 'string' ? next : next.name}
                          type="next"
                          mastery={userMastery[next?.id || next]}
                        />
                      ))}
                    </div>
                  </>
                )}

                {/* Applications Row */}
                {apps.length > 0 && apps.length !== nextTopics.length && (
                  <div className="mt-3 pt-3 border-t border-indigo-200 dark:border-indigo-700 w-full">
                    <p className="text-xs text-blue-600 dark:text-blue-400 font-medium text-center mb-2">
                      💡 Real-world applications:
                    </p>
                    <div className="flex items-center gap-2 flex-wrap justify-center">
                      {apps.slice(0, 3).map((app, i) => (
                        <ConceptNode
                          key={i}
                          name={typeof app === 'string' ? app : app.name}
                          type="application"
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Quick Stats */}
              {knowledgeGraph && (
                <div className="mt-3 p-3 bg-white/50 dark:bg-black/20 rounded-lg flex flex-wrap items-center justify-center gap-4 text-xs">
                  {knowledgeGraph.domain && (
                    <div className="flex items-center gap-1">
                      <BookOpen className="w-3 h-3 text-indigo-500" />
                      <span className="text-gray-600 dark:text-gray-400">Domain:</span>
                      <span className="font-medium text-gray-800 dark:text-gray-200">
                        {knowledgeGraph.domain}
                      </span>
                    </div>
                  )}
                  {knowledgeGraph.difficulty && (
                    <div className="flex items-center gap-1">
                      <Zap className="w-3 h-3 text-amber-500" />
                      <span className="text-gray-600 dark:text-gray-400">Difficulty:</span>
                      <span className="font-medium text-gray-800 dark:text-gray-200 capitalize">
                        {knowledgeGraph.difficulty}
                      </span>
                    </div>
                  )}
                  {knowledgeGraph.key_points?.length > 0 && (
                    <div className="flex items-center gap-1">
                      <Star className="w-3 h-3 text-violet-500" />
                      <span className="text-gray-600 dark:text-gray-400">Key points:</span>
                      <span className="font-medium text-gray-800 dark:text-gray-200">
                        {knowledgeGraph.key_points.length}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Learning Recommendations */}
              {learningPath.length > 0 && (
                <div className="mt-3 space-y-2">
                  {learningPath.map((rec, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 p-2 bg-white/30 dark:bg-black/20 rounded-lg"
                    >
                      {rec.startsWith('📚') || rec.startsWith('🚀') ? (
                        <span>{rec}</span>
                      ) : (
                        <>
                          <ArrowRight className="w-4 h-4 text-indigo-500 flex-shrink-0" />
                          <span>{rec}</span>
                        </>
                      )}
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default LearningPathVisualizer;




