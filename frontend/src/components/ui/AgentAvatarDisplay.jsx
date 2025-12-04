/**
 * AgentAvatarDisplay - Shows which AI agent is helping
 * 
 * COGNITO-OS v4.0 - Makes agent personas visible to students
 * Each agent has distinct personality and specialty
 */
import React from 'react';
import { motion } from 'framer-motion';
import { 
  GraduationCap, 
  Heart, 
  Palette, 
  Trophy, 
  Users, 
  Search,
  MessageCircle,
  Sparkles
} from 'lucide-react';

// Agent configurations with personalities
const AGENT_CONFIGS = {
  mentor: {
    name: 'Sathi',
    title: 'Your Study Buddy',
    icon: Heart,
    emoji: '🤝',
    color: 'from-emerald-400 to-teal-500',
    bgColor: 'bg-emerald-50 dark:bg-emerald-900/30',
    borderColor: 'border-emerald-200 dark:border-emerald-700',
    textColor: 'text-emerald-700 dark:text-emerald-300',
    specialty: 'Emotional support & simple explanations',
    greeting: 'Let me explain this in a way that clicks...'
  },
  professor: {
    name: 'Prof. Verma',
    title: 'Math & Physics Expert',
    icon: GraduationCap,
    emoji: '🎓',
    color: 'from-blue-500 to-indigo-600',
    bgColor: 'bg-blue-50 dark:bg-blue-900/30',
    borderColor: 'border-blue-200 dark:border-blue-700',
    textColor: 'text-blue-700 dark:text-blue-300',
    specialty: 'Formal derivations & proofs',
    greeting: 'Let me derive this step-by-step...'
  },
  doubt_resolver: {
    name: 'Clarity Coach',
    title: 'Doubt Specialist',
    icon: Search,
    emoji: '🔍',
    color: 'from-purple-500 to-pink-500',
    bgColor: 'bg-purple-50 dark:bg-purple-900/30',
    borderColor: 'border-purple-200 dark:border-purple-700',
    textColor: 'text-purple-700 dark:text-purple-300',
    specialty: 'Breaking down confusing concepts',
    greeting: 'I understand your confusion. Let\'s clear this up...'
  },
  visualise: {
    name: 'Visual Artist',
    title: 'Diagram Expert',
    icon: Palette,
    emoji: '🎨',
    color: 'from-orange-400 to-pink-500',
    bgColor: 'bg-orange-50 dark:bg-orange-900/30',
    borderColor: 'border-orange-200 dark:border-orange-700',
    textColor: 'text-orange-700 dark:text-orange-300',
    specialty: 'Visual explanations & diagrams',
    greeting: 'A picture is worth 1000 words...'
  },
  exam_coach: {
    name: 'Strategy Pro',
    title: 'Exam Coach',
    icon: Trophy,
    emoji: '🏆',
    color: 'from-amber-400 to-orange-500',
    bgColor: 'bg-amber-50 dark:bg-amber-900/30',
    borderColor: 'border-amber-200 dark:border-amber-700',
    textColor: 'text-amber-700 dark:text-amber-300',
    specialty: 'JEE/NEET exam strategies',
    greeting: 'Here\'s how to approach this in the exam...'
  },
  study_buddy: {
    name: 'Priya',
    title: 'Peer Learner',
    icon: Users,
    emoji: '👩‍🎓',
    color: 'from-pink-400 to-rose-500',
    bgColor: 'bg-pink-50 dark:bg-pink-900/30',
    borderColor: 'border-pink-200 dark:border-pink-700',
    textColor: 'text-pink-700 dark:text-pink-300',
    specialty: 'Learning together, like a friend',
    greeting: 'Hey! I remember learning this too...'
  }
};

const AgentAvatarDisplay = ({ 
  agentType = 'mentor', 
  showGreeting = false,
  compact = false,
  agentsUsed = []
}) => {
  const config = AGENT_CONFIGS[agentType] || AGENT_CONFIGS.mentor;
  const Icon = config.icon;

  // Compact mode - just icon and name
  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex items-center gap-2"
      >
        <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${config.color} flex items-center justify-center shadow-md`}>
          <span className="text-lg">{config.emoji}</span>
        </div>
        <div>
          <p className={`font-semibold text-sm ${config.textColor}`}>{config.name}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{config.title}</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl border ${config.bgColor} ${config.borderColor} p-4 mb-4`}
    >
      <div className="flex items-start gap-4">
        {/* Avatar */}
        <motion.div
          whileHover={{ scale: 1.05, rotate: 5 }}
          className={`w-12 h-12 rounded-xl bg-gradient-to-br ${config.color} flex items-center justify-center shadow-lg flex-shrink-0`}
        >
          <span className="text-2xl">{config.emoji}</span>
        </motion.div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className={`font-bold ${config.textColor}`}>{config.name}</h4>
            <span className="text-xs px-2 py-0.5 bg-white/50 dark:bg-black/20 rounded-full text-gray-600 dark:text-gray-300">
              {config.title}
            </span>
          </div>
          
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 flex items-center gap-1">
            <Icon className="w-3 h-3" />
            {config.specialty}
          </p>

          {/* Greeting */}
          {showGreeting && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="mt-2 text-sm text-gray-600 dark:text-gray-300 italic"
            >
              "{config.greeting}"
            </motion.p>
          )}
        </div>
      </div>

      {/* Multiple agents indicator */}
      {agentsUsed.length > 1 && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1">
            <Sparkles className="w-3 h-3" />
            Team effort from:
          </p>
          <div className="flex flex-wrap gap-2">
            {agentsUsed.map((agent, i) => {
              const agentConfig = AGENT_CONFIGS[agent] || AGENT_CONFIGS.mentor;
              return (
                <span
                  key={i}
                  className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs ${agentConfig.bgColor} ${agentConfig.textColor}`}
                >
                  <span>{agentConfig.emoji}</span>
                  {agentConfig.name}
                </span>
              );
            })}
          </div>
        </div>
      )}
    </motion.div>
  );
};

// Mini version for inline use
export const AgentMiniAvatar = ({ agentType = 'mentor' }) => {
  const config = AGENT_CONFIGS[agentType] || AGENT_CONFIGS.mentor;
  
  return (
    <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full ${config.bgColor} ${config.textColor} text-xs`}>
      <span>{config.emoji}</span>
      <span className="font-medium">{config.name}</span>
    </div>
  );
};

export default AgentAvatarDisplay;




