import React, { useEffect } from 'react';
import { useAnimation } from 'framer-motion';

/**
 * SketchAnimator - Component to animate sketches and metaphors in real-time
 */
const SketchAnimator = ({ explanation }) => {
  const controls = useAnimation();

  useEffect(() => {
    // Start the animation when the explanation changes
    controls.start({ opacity: 1, transition: { duration: 0.5 } });
  }, [explanation, controls]);

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="font-semibold text-gray-900">Real-Time Sketch Animation</h3>
      <motion.div
        initial={{ opacity: 0 }}
        animate={controls}
        className="text-gray-800 leading-relaxed whitespace-pre-wrap"
      >
        {explanation}
      </motion.div>
    </div>
  );
};

export default SketchAnimator;
