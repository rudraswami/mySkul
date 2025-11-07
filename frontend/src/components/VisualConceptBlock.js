import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Image as ImageIcon, X } from 'lucide-react';

/**
 * VisualConceptBlock - Renders SVG or Gemini-generated visuals
 * Supports both inline SVG and base64 images with expand/collapse
 */
const VisualConceptBlock = ({ visualData }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!visualData || !visualData.generated) {
    return null;
  }

  const renderVisual = () => {
    if (visualData.type === 'svg' && visualData.content) {
      return (
        <div 
          className="w-full max-w-xs mx-auto"
          dangerouslySetInnerHTML={{ __html: visualData.content }}
        />
      );
    } else if (visualData.type === 'gemini_image' && visualData.content) {
      return (
        <img
          src={`data:${visualData.mime_type || 'image/png'};base64,${visualData.content}`}
          alt="AI Generated Concept Visual"
          className="w-full max-w-md mx-auto rounded-lg"
        />
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="my-4"
    >
      {/* Compact View */}
      {!isExpanded && (
        <button
          onClick={() => setIsExpanded(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-lg transition-colors w-full"
        >
          <ImageIcon className="w-4 h-4" />
          <span className="text-sm font-medium">View Concept Visual</span>
        </button>
      )}

      {/* Expanded View */}
      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="p-4 bg-gray-50 rounded-lg border border-gray-200"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <ImageIcon className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-gray-700">Concept Visualization</span>
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="bg-white p-4 rounded-lg">
            {renderVisual()}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default VisualConceptBlock;