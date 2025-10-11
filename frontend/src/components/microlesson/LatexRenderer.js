import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * LatexRenderer - Intelligently detects and renders LaTeX math in text
 * Handles: \[...\], \(...\), $$...$$, $...$
 * AI Tutor 2.4 - Fix for raw LaTeX display issue
 */
const LatexRenderer = ({ text }) => {
  if (!text) return null;

  // Clean text first - remove special chars and markdown
  let cleanedText = text
    .replace(/\*\*(.+?)\*\*/g, '$1')  // Remove bold markers
    .replace(/\*(.+?)\*/g, '$1')      // Remove italic markers
    .replace(/\\n/g, '\n')
    .replace(/\\"/g, '"')
    .replace(/\\'/g, "'")
    .replace(/\\\\/g, '')
    .trim();

  // Pattern to match LaTeX expressions
  // Handles: \[...\], \(...\), $$...$$, $...$
  const latexPattern = /(\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$\$[\s\S]*?\$\$|\$[^\$\n]+?\$)/g;
  
  const parts = [];
  let lastIndex = 0;
  let match;

  // Split text into regular text and LaTeX parts
  while ((match = latexPattern.exec(cleanedText)) !== null) {
    // Add text before this LaTeX expression
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: cleanedText.substring(lastIndex, match.index)
      });
    }

    // Extract LaTeX content and determine if block or inline
    let latexContent = match[1];
    let isBlock = false;

    if (latexContent.startsWith('\\[') && latexContent.endsWith('\\]')) {
      isBlock = true;
      latexContent = latexContent.slice(2, -2);
    } else if (latexContent.startsWith('\\(') && latexContent.endsWith('\\)')) {
      isBlock = false;
      latexContent = latexContent.slice(2, -2);
    } else if (latexContent.startsWith('$$') && latexContent.endsWith('$$')) {
      isBlock = true;
      latexContent = latexContent.slice(2, -2);
    } else if (latexContent.startsWith('$') && latexContent.endsWith('$')) {
      isBlock = false;
      latexContent = latexContent.slice(1, -1);
    }

    parts.push({
      type: isBlock ? 'block-math' : 'inline-math',
      content: latexContent.trim()
    });

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < cleanedText.length) {
    parts.push({
      type: 'text',
      content: cleanedText.substring(lastIndex)
    });
  }

  // If no LaTeX found, just return cleaned text
  if (parts.length === 0) {
    return <span>{cleanedText}</span>;
  }

  // Render parts with proper LaTeX rendering
  return (
    <>
      {parts.map((part, index) => {
        if (part.type === 'text') {
          return <span key={index}>{part.content}</span>;
        } else if (part.type === 'inline-math') {
          try {
            return <InlineMath key={index} math={part.content} />;
          } catch (error) {
            console.error('KaTeX inline render error:', error);
            return <span key={index} className="text-red-600">{part.content}</span>;
          }
        } else if (part.type === 'block-math') {
          try {
            return (
              <div key={index} className="my-4 text-center">
                <BlockMath math={part.content} />
              </div>
            );
          } catch (error) {
            console.error('KaTeX block render error:', error);
            return <div key={index} className="text-red-600 text-center">{part.content}</div>;
          }
        }
        return null;
      })}
    </>
  );
};

export default LatexRenderer;
