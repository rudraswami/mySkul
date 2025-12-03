/**
 * Collapsible Section Component
 * For expandable response sections with smooth animation
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

const CollapsibleSection = ({
  title,
  icon,
  children,
  defaultOpen = false,
  variant = 'default', // 'default' | 'highlighted' | 'compact'
  badge,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const variants = {
    default: {
      header: 'bg-gray-50 hover:bg-gray-100',
      content: 'bg-white',
      border: 'border-gray-200'
    },
    highlighted: {
      header: 'bg-violet-50 hover:bg-violet-100',
      content: 'bg-violet-50/30',
      border: 'border-violet-200'
    },
    compact: {
      header: 'bg-transparent hover:bg-gray-50',
      content: 'bg-transparent',
      border: 'border-transparent'
    }
  };

  const style = variants[variant];

  return (
    <div className={`rounded-xl overflow-hidden border ${style.border} ${className}`}>
      {/* Header - Always visible */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full flex items-center justify-between gap-3 px-4 py-3 ${style.header} transition-colors`}
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-3">
          {icon && (
            <div className="flex-shrink-0 w-8 h-8 bg-violet-100 text-violet-600 rounded-lg flex items-center justify-center">
              {icon}
            </div>
          )}
          <span className="font-semibold text-gray-800 text-[15px] text-left">
            {title}
          </span>
          {badge && (
            <span className="px-2 py-0.5 bg-violet-100 text-violet-700 text-xs font-medium rounded-full">
              {badge}
            </span>
          )}
        </div>
        
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="flex-shrink-0"
        >
          <ChevronDown className="w-5 h-5 text-gray-500" />
        </motion.div>
      </button>

      {/* Content - Animated */}
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.04, 0.62, 0.23, 0.98] }}
            className="overflow-hidden"
          >
            <div className={`px-4 py-4 ${style.content} border-t ${style.border}`}>
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CollapsibleSection;

