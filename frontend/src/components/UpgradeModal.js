import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Crown, Zap, TrendingUp, Star, ArrowRight } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { useNavigate } from 'react-router-dom';
import { PLANS_CONFIG, getPlanByTier } from '../config/plans';
import { 
  applyGlobalModalBehavior, 
  getModalAnimationProps, 
  getBackdropStyle,
  getModalContainerStyle,
  getModalContentStyle
} from '../utils/modalBehavior';
import { MODAL_BEHAVIOR } from '../config/modalConfig';

/**
 * UpgradeModal - Shows when user reaches AI Tutor session limit
 * Displays motivational copy and upgrade options
 * 
 * INTEGRATED: Global modal behavior (scroll lock, focus trap, ESC key, animations)
 */
const UpgradeModal = ({ 
  isOpen, 
  onClose, 
  upgradeHint, 
  accessInfo,
  currentTier = "FREE"
}) => {
  const navigate = useNavigate();
  const modalRef = useRef(null);

  // Apply global modal behavior
  useEffect(() => {
    if (isOpen && modalRef.current) {
      return applyGlobalModalBehavior(modalRef.current, {
        trapFocus: true,
        outsideClick: true, // Allow closing on backdrop click
        onClose,
        scrollLock: true,
        closeOnEsc: true
      });
    }
  }, [isOpen, onClose]);

  console.log('🎭 UpgradeModal render:', { isOpen, upgradeHint, accessInfo, currentTier });

  if (!isOpen) {
    console.log('🎭 Modal NOT open - returning null');
    return null;
  }

  console.log('🎭 Modal IS open - rendering...');

  const limitReached = upgradeHint?.type === "limit_reached";
  const approachingLimit = upgradeHint?.type === "approaching_limit";
  
  console.log('🎭 Modal state:', { limitReached, approachingLimit });

  const handleUpgrade = () => {
    onClose();
    navigate('/subscription');
  };

  // Get standardized animation props and styles
  const backdropAnimation = getModalAnimationProps('backdrop');
  const modalAnimation = getModalAnimationProps('modal');
  const backdropStyle = getBackdropStyle();
  const containerStyle = getModalContainerStyle();
  const contentStyle = getModalContentStyle({ maxWidth: '48rem' }); // max-w-2xl

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop - Using global z-index (9490) */}
          <motion.div
            {...backdropAnimation}
            style={backdropStyle}
            className="fixed inset-0"
            data-modal-backdrop="true"
            onClick={onClose}
          />

          {/* Modal Container - Using global z-index (9500) */}
          <motion.div
            {...modalAnimation}
            ref={modalRef}
            style={containerStyle}
            className="fixed inset-0 p-4 pointer-events-none"
          >
            <div 
              style={contentStyle}
              className="w-full pointer-events-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <Card className="bg-white rounded-2xl shadow-2xl overflow-hidden">
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

                {/* Target Plan & Pricing Info */}
                {upgradeHint?.target_plan && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 rounded-xl p-5 border-2 border-blue-200"
                  >
                    <div className="text-center mb-3">
                      <h3 className="text-lg font-bold text-gray-900 flex items-center justify-center">
                        <Crown className="w-5 h-5 text-yellow-500 mr-2" />
                        Recommended: {upgradeHint.target_plan} Plan
                      </h3>
                    </div>
                    
                    {/* Pricing Display */}
                    {(() => {
                      const targetPlan = getPlanByTier(upgradeHint.target_plan);
                      return (
                        <div className="bg-white rounded-lg p-4 mb-3 border border-blue-200">
                          <p className="text-center text-gray-600 text-sm mb-2">Starting at</p>
                          <div className="text-center">
                            <span className="text-3xl font-bold text-blue-600">
                              ₹{targetPlan.price_monthly}
                            </span>
                            <span className="text-gray-600 ml-1">/month</span>
                          </div>
                          {targetPlan.savings && (
                            <p className="text-center text-sm text-gray-600 mt-2">
                              Save with quarterly (₹{targetPlan.price_quarterly}) or yearly (₹{targetPlan.price_yearly})
                            </p>
                          )}
                        </div>
                      );
                    })()}
                    
                    {/* Key Benefits */}
                    {upgradeHint.benefits && upgradeHint.benefits.length > 0 && (
                      <div className="space-y-2">
                        {upgradeHint.benefits.slice(0, 3).map((benefit, idx) => (
                          <div key={idx} className="flex items-start text-sm">
                            <Zap className="w-4 h-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700">{benefit}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )}

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    onClick={handleUpgrade}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
                  >
                    <span className="flex items-center justify-center">
                      {upgradeHint?.cta || "View Plans & Upgrade"}
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </span>
                  </Button>

                  {!limitReached && (
                    <Button
                      onClick={onClose}
                      variant="outline"
                      className="flex-1 py-3 rounded-xl font-semibold hover:bg-gray-50"
                    >
                      Maybe Later
                    </Button>
                  )}
                </div>
              </div>
              </Card>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default UpgradeModal;
