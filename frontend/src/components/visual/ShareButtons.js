/**
 * Share Buttons Component
 * WhatsApp share and copy functionality for AI responses
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Share2, MessageCircle, Copy, Check } from 'lucide-react';

const ShareButtons = ({ response, question, visualSvg, onToast }) => {
  const [copied, setCopied] = useState(false);
  
  // Use provided toast function or fallback
  const showToast = onToast || ((msg, type) => {
    // Fallback: show browser notification or console log
    if (type === 'success') {
      console.log(`✅ ${msg}`);
    } else {
      console.log(`❌ ${msg}`);
    }
  });

  const shareToWhatsApp = () => {
    const responsePreview = response.substring(0, 200).replace(/\n/g, ' ');
    const text = `Check out this amazing AI explanation I got on Druv AI! 🚀\n\n❓ Q: ${question}\n\n💡 A: ${responsePreview}...\n\n✨ Try Druv AI: ${window.location.origin}\n\n#DruvAI #AITutor #Learning`;
    const url = `https://wa.me/?text=${encodeURIComponent(text)}`;
    window.open(url, '_blank');
    
    // Track share event
    if (window.gtag) {
      window.gtag('event', 'share', {
        method: 'WhatsApp',
        content_type: 'ai_response'
      });
    }
  };

  const copyToClipboard = async () => {
    try {
      const textToCopy = `Q: ${question}\n\nA: ${response}`;
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      showToast('Copied to clipboard!', 'success');
      
      setTimeout(() => setCopied(false), 2000);
      
      // Track copy event
      if (window.gtag) {
        window.gtag('event', 'copy', {
          content_type: 'ai_response'
        });
      }
    } catch (err) {
      showToast('Failed to copy', 'error');
    }
  };

  const shareVisual = () => {
    if (!visualSvg) return;
    
    // Convert SVG to data URL for sharing
    const svgBlob = new Blob([visualSvg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(svgBlob);
    
    // For now, just copy SVG code
    navigator.clipboard.writeText(visualSvg).then(() => {
      showToast('Visual diagram copied!', 'success');
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2 }}
      className="flex items-center space-x-2 mt-4"
    >
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={shareToWhatsApp}
        className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors shadow-md"
      >
        <MessageCircle className="h-4 w-4" />
        <span className="text-sm font-medium">Share on WhatsApp</span>
      </motion.button>
      
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={copyToClipboard}
        className="flex items-center space-x-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
      >
        {copied ? (
          <>
            <Check className="h-4 w-4 text-green-500" />
            <span className="text-sm font-medium">Copied!</span>
          </>
        ) : (
          <>
            <Copy className="h-4 w-4" />
            <span className="text-sm font-medium">Copy</span>
          </>
        )}
      </motion.button>
      
      {visualSvg && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={shareVisual}
          className="flex items-center space-x-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
          title="Share visual diagram"
        >
          <Share2 className="h-4 w-4" />
          <span className="text-sm font-medium">Share Visual</span>
        </motion.button>
      )}
    </motion.div>
  );
};

export default ShareButtons;

