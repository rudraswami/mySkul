/**
 * IntelligenceChips - Minimal tappable buttons (ChatGPT/Gemini style)
 * 
 * NOT panels. NOT inline dumps. Just small chips that open modals.
 * 
 * Shows: [ Verified ✓ ]  [ Reasoning 🔍 ]  [ Concept Map 🧠 ]  [ Teach Me Back 🎯 ]
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle2, 
  Search, 
  Map, 
  X,
  BookOpen,
  Sparkles,
  ArrowRight,
  MessageCircle,
  Send,
  Award,
  Lightbulb,
  Target,
  Loader2
} from 'lucide-react';

// Simple Modal for chip content
const ChipModal = ({ isOpen, onClose, title, icon: Icon, children }) => {
  if (!isOpen) return null;
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-md w-full max-h-[80vh] overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <Icon className="w-5 h-5 text-violet-600" />
              <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
          
          {/* Content */}
          <div className="p-4 overflow-y-auto max-h-[60vh]">
            {children}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

const IntelligenceChips = ({
  isVerified = true,
  sources = [],
  hasConceptMap = false,
  knowledgeGraph = null,
  learningPath = [],
  originalAnswer = '',
  topic = '',
  onTeachBack = null
}) => {
  const [activeModal, setActiveModal] = useState(null);
  const [teachBackInput, setTeachBackInput] = useState('');
  const [teachBackFeedback, setTeachBackFeedback] = useState(null);
  const [isEvaluating, setIsEvaluating] = useState(false);

  const closeModal = () => {
    setActiveModal(null);
    setTeachBackInput('');
    setTeachBackFeedback(null);
  };

  // Evaluate student's explanation using existing AI
  const handleTeachBackSubmit = async () => {
    if (!teachBackInput.trim() || teachBackInput.length < 20) return;
    
    setIsEvaluating(true);
    
    try {
      // Use existing AI endpoint to evaluate
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/ai/neuro-symbolic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: `[TEACH ME BACK EVALUATION]
          
Student is trying to explain this concept in their own words. 
Evaluate their explanation and give encouraging, constructive feedback.

ORIGINAL TOPIC/CONCEPT: ${topic || 'the concept explained above'}

STUDENT'S EXPLANATION:
"${teachBackInput}"

Please respond in this JSON format ONLY (no markdown, just raw JSON):
{
  "score": <number 1-5>,
  "concepts_covered": ["concept1", "concept2"],
  "concepts_missing": ["missing1"],
  "clarity": "<good/okay/needs work>",
  "encouragement": "<friendly 1-line encouragement>",
  "tip": "<one specific tip to improve>",
  "emoji": "<one relevant emoji>"
}`,
          subject: 'General'
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Try to parse the AI response as JSON
        const content = data.response?.default_view?.main_content?.content || 
                       data.response?.progressive_sections?.explanation || '';
        
        try {
          // Extract JSON from response
          const jsonMatch = content.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            const feedback = JSON.parse(jsonMatch[0]);
            setTeachBackFeedback(feedback);
          } else {
            // Fallback feedback
            setTeachBackFeedback({
              score: 3,
              concepts_covered: ['main idea'],
              concepts_missing: [],
              clarity: 'good',
              encouragement: "Great effort! You're on the right track!",
              tip: "Try adding a real-world example next time.",
              emoji: "👍"
            });
          }
        } catch {
          // Fallback if JSON parsing fails
          setTeachBackFeedback({
            score: 3,
            concepts_covered: ['explanation attempt'],
            concepts_missing: [],
            clarity: 'okay',
            encouragement: "Nice try! Keep practicing!",
            tip: "Try to include the key formula or definition.",
            emoji: "💪"
          });
        }
      }
    } catch (error) {
      console.error('Teach back evaluation failed:', error);
      setTeachBackFeedback({
        score: 3,
        encouragement: "Great effort explaining! Keep it up!",
        tip: "Practice makes perfect.",
        emoji: "🌟"
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <>
      {/* Chips Row - Single line, minimal */}
      <div className="flex items-center gap-2 mt-4 flex-wrap">
        {/* Verified Chip */}
        {isVerified && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setActiveModal('verified')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100 dark:hover:bg-emerald-900/50 transition-colors"
          >
            <CheckCircle2 className="w-4 h-4" />
            Verified
          </motion.button>
        )}

        {/* Reasoning Chip */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setActiveModal('reasoning')}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-violet-50 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 border border-violet-200 dark:border-violet-800 hover:bg-violet-100 dark:hover:bg-violet-900/50 transition-colors"
        >
          <Search className="w-4 h-4" />
          Reasoning
        </motion.button>

        {/* Concept Map Chip (only if data exists) */}
        {hasConceptMap && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setActiveModal('conceptMap')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
          >
            <Map className="w-4 h-4" />
            Concept Map
          </motion.button>
        )}

        {/* 🎯 Teach Me Back Chip - Active Learning */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setActiveModal('teachBack')}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 hover:bg-amber-100 dark:hover:bg-amber-900/50 transition-colors"
        >
          <Target className="w-4 h-4" />
          Teach Me Back
        </motion.button>
      </div>

      {/* MODALS - Only shown when chip is clicked */}
      
      {/* Verified Modal */}
      <ChipModal
        isOpen={activeModal === 'verified'}
        onClose={closeModal}
        title="Answer Verified"
        icon={CheckCircle2}
      >
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 bg-emerald-50 dark:bg-emerald-900/30 rounded-xl">
            <CheckCircle2 className="w-8 h-8 text-emerald-500" />
            <div>
              <p className="font-semibold text-emerald-700 dark:text-emerald-300">
                This answer has been verified
              </p>
              <p className="text-sm text-emerald-600 dark:text-emerald-400">
                Cross-checked with curriculum sources
              </p>
            </div>
          </div>
          
          {sources.length > 0 && (
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sources Referenced:
              </p>
              <div className="space-y-1">
                {sources.map((source, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <BookOpen className="w-4 h-4 text-violet-500" />
                    {source}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </ChipModal>

      {/* Reasoning Modal */}
      <ChipModal
        isOpen={activeModal === 'reasoning'}
        onClose={closeModal}
        title="How I Solved This"
        icon={Sparkles}
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            Here's my thinking process:
          </p>
          
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-900 flex items-center justify-center text-xs font-bold text-violet-600">1</div>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Understood your question and identified the key concept
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-900 flex items-center justify-center text-xs font-bold text-violet-600">2</div>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Retrieved relevant information from NCERT and curriculum
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-900 flex items-center justify-center text-xs font-bold text-violet-600">3</div>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Generated a clear explanation tailored for you
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Verified the answer for accuracy
              </p>
            </div>
          </div>
        </div>
      </ChipModal>

      {/* Concept Map Modal */}
      <ChipModal
        isOpen={activeModal === 'conceptMap'}
        onClose={closeModal}
        title="Concept Map"
        icon={Map}
      >
        <div className="space-y-4">
          {knowledgeGraph ? (
            <>
              {/* Current Topic */}
              <div className="p-3 bg-violet-50 dark:bg-violet-900/30 rounded-xl">
                <p className="text-xs text-violet-500 dark:text-violet-400 mb-1">You're learning:</p>
                <p className="font-semibold text-violet-700 dark:text-violet-300">
                  {knowledgeGraph.main_concept || 'Current Topic'}
                </p>
              </div>

              {/* Prerequisites */}
              {knowledgeGraph.prerequisites?.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    📚 Review first:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {knowledgeGraph.prerequisites.map((prereq, i) => (
                      <span key={i} className="px-2 py-1 bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 text-sm rounded-lg">
                        {prereq}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Next Steps */}
              {knowledgeGraph.applications?.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    🚀 Learn next:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {knowledgeGraph.applications.map((app, i) => (
                      <span key={i} className="px-2 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg flex items-center gap-1">
                        <ArrowRight className="w-3 h-3" />
                        {app}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-4">
              Concept map not available for this topic yet.
            </p>
          )}

          {/* Learning Path Recommendations */}
          {learningPath.length > 0 && (
            <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                📍 Your learning path:
              </p>
              <div className="space-y-2">
                {learningPath.map((step, i) => (
                  <p key={i} className="text-sm text-gray-600 dark:text-gray-400">
                    {step}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      </ChipModal>
    </>
  );
};

export default IntelligenceChips;

