import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Crown, Zap, TrendingUp, Star, ArrowRight } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { useNavigate } from 'react-router-dom';

/**
 * UpgradeModal - Shows when user reaches AI Tutor session limit
 * Displays motivational copy and upgrade options
 */
const UpgradeModal = ({ 
  isOpen, 
  onClose, 
  upgradeHint, 
  accessInfo,
  currentTier = "FREE"
}) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  const limitReached = upgradeHint?.type === "limit_reached";
  const approachingLimit = upgradeHint?.type === "approaching_limit";

  const handleUpgrade = () => {
    onClose();
    navigate('/subscription');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onClick={(e) => e.stopPropagation()}
          >
            <Card className="max-w-2xl w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
              {/* Header with gradient */}
              <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6 text-white relative">
                <button
                  onClick={onClose}
                  className="absolute top-4 right-4 text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>

                <div className="flex items-center space-x-3 mb-2">
                  {limitReached ? (
                    <Zap className="w-8 h-8" />
                  ) : (
                    <TrendingUp className="w-8 h-8" />
                  )}
                  <h2 className="text-2xl font-bold">
                    {limitReached ? "Limit Reached!" : "You're Doing Great!"}
                  </h2>
                </div>

                <p className="text-white text-opacity-90">
                  {limitReached 
                    ? "Upgrade to continue your learning journey"
                    : "Consider upgrading to unlock more sessions"
                  }
                </p>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                {/* Usage Stats */}
                {accessInfo && (
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 border border-blue-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-700 font-semibold">Your Usage</span>
                      <span className="text-lg font-bold text-blue-600">
                        {accessInfo.current_usage || 0}/{accessInfo.total} sessions
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${accessInfo.usage_percent || 0}%` }}
                        transition={{ duration: 0.5 }}
                        className={`h-full rounded-full ${
                          accessInfo.usage_percent >= 100 
                            ? 'bg-red-500'
                            : accessInfo.usage_percent >= 80
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                        }`}
                      />
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                      {accessInfo.usage_percent >= 100 
                        ? "You've reached your limit for this month"
                        : `${accessInfo.usage_percent}% used`
                      }
                    </p>
                  </div>
                )}

                {/* Mentor Message */}
                {upgradeHint?.mentor_message && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl p-5 border-l-4 border-pink-400"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="bg-pink-500 rounded-full p-2">
                        <Crown className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-semibold text-pink-900 mb-1">💙 Your Mentor Says:</p>
                        <p className="text-gray-800 leading-relaxed">
                          {upgradeHint.mentor_message}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Professor Message */}
                {upgradeHint?.professor_message && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-5 border-l-4 border-blue-400"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="bg-blue-500 rounded-full p-2">
                        <Star className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-semibold text-blue-900 mb-1">📚 Professor's Insight:</p>
                        <p className="text-gray-800 leading-relaxed">
                          {upgradeHint.professor_message}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Simple message fallback */}
                {upgradeHint?.message && !upgradeHint?.mentor_message && (
                  <div className="bg-yellow-50 rounded-xl p-5 border border-yellow-200">
                    <p className="text-gray-800 leading-relaxed">
                      {upgradeHint.message}
                    </p>
                  </div>
                )}

                {/* Upgrade Benefits */}
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-5">
                  <h3 className="font-bold text-gray-900 mb-3 flex items-center">
                    <Zap className="w-5 h-5 text-yellow-500 mr-2" />
                    Upgrade to {upgradeHint?.target_plan || "Premium"} and Get:
                  </h3>
                  <ul className="space-y-2">
                    {upgradeHint?.target_plan === "STARTER" && (
                      <>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          20 AI sessions per month
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Weekly AI insights
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Export your notes
                        </li>
                      </>
                    )}
                    {upgradeHint?.target_plan === "SCHOLAR" && (
                      <>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          100 AI sessions per month
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          5 mentor tips daily
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Advanced analytics
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Adaptive AI guidance
                        </li>
                      </>
                    )}
                    {upgradeHint?.target_plan === "ACHIEVER" && (
                      <>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          300 AI sessions per month
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          30 mentor tips daily
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Unlimited mock tests
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Emotion-aware AI
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Priority support
                        </li>
                      </>
                    )}
                    {upgradeHint?.target_plan === "LEGEND" && (
                      <>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Unlimited everything!
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Priority AI models
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Dedicated mentor support
                        </li>
                        <li className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          Custom study plans
                        </li>
                      </>
                    )}
                  </ul>
                </div>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    onClick={handleUpgrade}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
                  >
                    <span className="flex items-center justify-center">
                      {upgradeHint?.cta || "Upgrade Now"}
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </span>
                  </Button>

                  {!limitReached && (
                    <Button
                      onClick={onClose}
                      variant="outline"
                      className="flex-1 py-3 rounded-xl font-semibold"
                    >
                      Maybe Later
                    </Button>
                  )}
                </div>

                {/* Trust Badge */}
                <p className="text-center text-sm text-gray-500">
                  ✨ Join 10,000+ students who upgraded to accelerate their learning
                </p>
              </div>
            </Card>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default UpgradeModal;
