import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Lottie from 'lottie-react';

/**
 * MotivationalFooter - Dynamic footer with progress stats and Lottie animation
 * AI Tutor 2.1 micro-lesson component
 */
const MotivationalFooter = ({ motivationalData }) => {
  const [animationData, setAnimationData] = useState(null);

  useEffect(() => {
    if (motivationalData?.animation_type) {
      // Load Lottie animation
      const loadAnimation = async () => {
        try {
          const animationUrl = getLottieUrl(motivationalData.animation_type);
          const response = await fetch(animationUrl);
          const data = await response.json();
          setAnimationData(data);
        } catch (error) {
          console.error('Failed to load Lottie animation:', error);
        }
      };
      loadAnimation();
    }
  }, [motivationalData?.animation_type]);

  const getLottieUrl = (type) => {
    const urls = {
      celebration: 'https://assets5.lottiefiles.com/packages/lf20_touohxv0.json',
      fire: 'https://assets9.lottiefiles.com/packages/lf20_yfsxxxdp.json',
      trophy: 'https://assets10.lottiefiles.com/packages/lf20_jwjvhg3v.json',
      heart: 'https://assets4.lottiefiles.com/packages/lf20_lk80fpsm.json',
      rocket: 'https://assets8.lottiefiles.com/packages/lf20_jpcmikjb.json',
      star: 'https://assets2.lottiefiles.com/packages/lf20_s2lryxtd.json'
    };
    return urls[type] || urls.star;
  };

  if (!motivationalData) return null;

  const { message, stats } = motivationalData;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.4 }}
      className="mt-4 p-4 bg-gradient-to-r from-purple-50 via-pink-50 to-orange-50 rounded-xl border border-purple-100"
    >
      <div className="flex items-center space-x-4">
        {/* Lottie Animation */}
        {animationData && (
          <div className="flex-shrink-0">
            <Lottie
              animationData={animationData}
              loop={true}
              style={{ width: 60, height: 60 }}
            />
          </div>
        )}

        {/* Message and Stats */}
        <div className="flex-1">
          <p className="text-gray-800 font-medium mb-2 font-inter">
            {message}
          </p>
          
          {/* Progress Stats */}
          {stats && (
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              {stats.accuracy > 0 && (
                <div className="flex items-center space-x-1">
                  <span className="font-semibold text-blue-600">
                    {Math.round(stats.accuracy)}%
                  </span>
                  <span>accuracy</span>
                </div>
              )}
              {stats.streak > 0 && (
                <div className="flex items-center space-x-1">
                  <span className="font-semibold text-orange-600">
                    {stats.streak}
                  </span>
                  <span>day streak</span>
                </div>
              )}
              {stats.improvement > 0 && (
                <div className="flex items-center space-x-1">
                  <span className="font-semibold text-green-600">
                    +{Math.round(stats.improvement)}%
                  </span>
                  <span>this week</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {stats && stats.mastery > 0 && (
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 1, delay: 0.5 }}
          className="mt-3"
        >
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${stats.mastery}%` }}
              transition={{ duration: 1, delay: 0.7 }}
              className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
            />
          </div>
          <p className="text-xs text-gray-500 mt-1 text-right">
            {Math.round(stats.mastery)}% mastery
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default MotivationalFooter;