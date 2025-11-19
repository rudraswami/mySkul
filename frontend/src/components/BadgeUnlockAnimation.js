import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { X, Sparkles } from 'lucide-react';
import GlobalModal from './modals/GlobalModal';

export default function BadgeUnlockAnimation({ badges, onClose }) {
  const [currentBadgeIndex, setCurrentBadgeIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    // Auto-advance to next badge after 3 seconds
    if (currentBadgeIndex < badges.length - 1) {
      const timer = setTimeout(() => {
        setCurrentBadgeIndex(prev => prev + 1);
        setIsAnimating(true);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [currentBadgeIndex, badges.length]);

  if (!badges || badges.length === 0) return null;

  const currentBadge = badges[currentBadgeIndex];

  return (
    <GlobalModal isOpen onClose={onClose} closeOnBackdrop={false} trapFocus={false} maxWidth="28rem">
      <div className="relative">
      {/* Confetti effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="absolute animate-confetti"
            style={{
              left: `${Math.random() * 100}%`,
              top: '-10%',
              animationDelay: `${Math.random() * 2}s`,
              animationDuration: `${2 + Math.random() * 2}s`
            }}
          >
            {['🎉', '⭐', '🏆', '💫', '✨'][Math.floor(Math.random() * 5)]}
          </div>
        ))}
      </div>

      {/* Badge card */}
      <Card className="max-w-md w-full bg-gradient-to-br from-yellow-50 to-orange-50 border-4 border-yellow-400 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full bg-white shadow-lg hover:bg-gray-100 transition-colors z-10"
        >
          <X className="w-5 h-5 text-gray-600" />
        </button>

        <CardContent className="p-8 text-center">
          {/* Badge Icon with animation */}
          <div className={`relative mb-6 ${isAnimating ? 'animate-badge-bounce' : ''}`}>
            <div className="absolute inset-0 bg-yellow-300 rounded-full blur-2xl opacity-50 animate-pulse"></div>
            <div className="relative text-9xl">
              {currentBadge.badge_icon || '🏆'}
            </div>
            <Sparkles className="absolute -top-4 -right-4 w-8 h-8 text-yellow-500 animate-spin" />
            <Sparkles className="absolute -bottom-4 -left-4 w-8 h-8 text-yellow-500 animate-spin" style={{ animationDelay: '0.5s' }} />
          </div>

          {/* Badge info */}
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            Badge Unlocked!
          </h2>
          <h3 className="text-2xl font-semibold text-yellow-700 mb-3">
            {currentBadge.badge_name}
          </h3>
          <p className="text-gray-700 mb-6 text-lg">
            {currentBadge.description}
          </p>

          {/* Badge counter */}
          {badges.length > 1 && (
            <div className="flex items-center justify-center gap-2 mb-4">
              {badges.map((_, idx) => (
                <div
                  key={idx}
                  className={`h-2 rounded-full transition-all ${
                    idx === currentBadgeIndex
                      ? 'w-8 bg-yellow-500'
                      : idx < currentBadgeIndex
                      ? 'w-2 bg-yellow-300'
                      : 'w-2 bg-gray-300'
                  }`}
                />
              ))}
            </div>
          )}

          {/* Action buttons */}
          <div className="flex gap-3">
            {currentBadgeIndex < badges.length - 1 ? (
              <>
                <Button
                  variant="outline"
                  onClick={onClose}
                  className="flex-1"
                >
                  Skip All
                </Button>
                <Button
                  onClick={() => {
                    setCurrentBadgeIndex(prev => prev + 1);
                    setIsAnimating(true);
                  }}
                  className="flex-1 bg-yellow-500 hover:bg-yellow-600 text-white"
                >
                  Next Badge →
                </Button>
              </>
            ) : (
              <Button
                onClick={onClose}
                className="w-full bg-green-500 hover:bg-green-600 text-white text-lg py-6"
              >
                Awesome! 🎉
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <style jsx>{`
        @keyframes confetti {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(360deg);
            opacity: 0;
          }
        }

        @keyframes badgeBounce {
          0%, 100% {
            transform: scale(1) rotate(0deg);
          }
          25% {
            transform: scale(1.1) rotate(-5deg);
          }
          50% {
            transform: scale(1.2) rotate(5deg);
          }
          75% {
            transform: scale(1.1) rotate(-5deg);
          }
        }

        .animate-confetti {
          animation: confetti linear forwards;
        }

        .animate-badge-bounce {
          animation: badgeBounce 1s ease-in-out;
        }
      `}</style>
      </div>
    </GlobalModal>
  );
}
