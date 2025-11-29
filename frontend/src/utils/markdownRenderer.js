/**
 * Simple Markdown Renderer for Student-Friendly Content
 * Handles: **bold**, *italic*, `code`, LaTeX math (inline & block), and preserves structure
 * ENHANCED: Now supports \(...\), $...$, \[...\], and $$...$$ LaTeX formulas!
 */

import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * Pre-process text to extract block math before line-by-line parsing
 */
const extractBlockMath = (text) => {
  if (!text) return { processedText: text, blockMathMap: {} };
  
  const blockMathMap = {};
  let counter = 0;
  
  // Handle \[...\] block math (including multi-line)
  let processedText = text.replace(/\\\[([\s\S]*?)\\\]/g, (match, content) => {
    const placeholder = `__BLOCK_MATH_${counter}__`;
    blockMathMap[placeholder] = content.trim();
    counter++;
    return placeholder;
  });
  
  // Handle $$...$$ block math (including multi-line)
  processedText = processedText.replace(/\$\$([\s\S]*?)\$\$/g, (match, content) => {
    const placeholder = `__BLOCK_MATH_${counter}__`;
    blockMathMap[placeholder] = content.trim();
    counter++;
    return placeholder;
  });
  
  return { processedText, blockMathMap };
};

/**
 * Parse markdown text and return React elements with proper formatting
 * @param {string} text - Text with markdown formatting
 * @returns {React.ReactElement[]} - Array of React elements
 */
export function parseMarkdown(text) {
  if (!text) return [];
  
  // Extract block math first
  const { processedText, blockMathMap } = extractBlockMath(text);
  
  const elements = [];
  // ENHANCED: Added LaTeX patterns - use non-greedy matching for nested parens
  const patterns = [
    { regex: /__BLOCK_MATH_(\d+)__/g, type: 'block-math' },  // Block math placeholders
    { regex: /\\\((.+?)\\\)/g, type: 'math' },      // \(...\) - LaTeX inline
    { regex: /\$([^\$\n]+)\$/g, type: 'math' },     // $...$ - LaTeX inline  
    { regex: /\*\*(.+?)\*\*/g, type: 'bold' },      // **bold**
    { regex: /\*(.+?)\*/g, type: 'italic' },         // *italic*
    { regex: /`(.+?)`/g, type: 'code' },             // `code`
    { regex: /\n/g, type: 'newline' }                // Line breaks
  ];
  
  // Find all matches for all patterns
  const matches = [];
  patterns.forEach(pattern => {
    let match;
    const regex = new RegExp(pattern.regex.source, 'g');
    while ((match = regex.exec(processedText)) !== null) {
      matches.push({
        type: pattern.type,
        start: match.index,
        end: match.index + match[0].length,
        content: match[1] || match[0],
        fullMatch: match[0]
      });
    }
  });
  
  // Sort by position
  matches.sort((a, b) => a.start - b.start);
  
  // Remove overlapping matches
  const filteredMatches = [];
  let lastEnd = 0;
  matches.forEach(m => {
    if (m.start >= lastEnd) {
      filteredMatches.push(m);
      lastEnd = m.end;
    }
  });
  
  // Build elements
  lastEnd = 0;
  filteredMatches.forEach((match, idx) => {
    // Add text before this match
    if (match.start > lastEnd) {
      const beforeText = processedText.substring(lastEnd, match.start);
      if (beforeText) {
        elements.push(<span key={`text-${idx}`}>{beforeText}</span>);
      }
    }
    
    // Add formatted element
    switch (match.type) {
      case 'block-math':
        // Render block LaTeX math
        const blockLatex = blockMathMap[match.fullMatch];
        if (blockLatex) {
          try {
            elements.push(
              <div key={`block-math-${idx}`} className="my-3 py-2 overflow-x-auto">
                <BlockMath math={blockLatex} />
              </div>
            );
          } catch (e) {
            elements.push(
              <div key={`block-math-err-${idx}`} className="my-3 bg-red-50 text-red-600 p-2 rounded font-mono text-sm">
                {blockLatex}
              </div>
            );
          }
        }
        break;
      case 'math':
        // Render inline LaTeX math
        try {
          elements.push(
            <InlineMath key={`math-${idx}`} math={match.content.trim()} />
          );
        } catch (e) {
          elements.push(
            <code 
              key={`math-err-${idx}`} 
              className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-sm font-mono"
            >
              {match.content}
            </code>
          );
        }
        break;
      case 'bold':
        elements.push(
          <strong key={`bold-${idx}`} className="font-bold text-gray-900">
            {match.content}
          </strong>
        );
        break;
      case 'italic':
        elements.push(
          <em key={`italic-${idx}`} className="italic text-gray-800">
            {match.content}
          </em>
        );
        break;
      case 'code':
        elements.push(
          <code 
            key={`code-${idx}`} 
            className="bg-gray-100 text-purple-600 px-2 py-1 rounded text-sm font-mono"
          >
            {match.content}
          </code>
        );
        break;
      case 'newline':
        elements.push(<br key={`br-${idx}`} />);
        break;
      default:
        break;
    }
    
    lastEnd = match.end;
  });
  
  // Add remaining text
  if (lastEnd < processedText.length) {
    const remainingText = processedText.substring(lastEnd);
    if (remainingText) {
      elements.push(<span key="text-end">{remainingText}</span>);
    }
  }
  
  return elements.length > 0 ? elements : [text];
}

/**
 * Component that renders markdown-formatted text
 */
export function MarkdownText({ children, className = '' }) {
  if (!children) return null;
  
  const text = typeof children === 'string' ? children : String(children);
  const elements = parseMarkdown(text);
  
  return (
    <span className={className}>
      {elements}
    </span>
  );
}

/**
 * Render paragraph with markdown support
 */
export function MarkdownParagraph({ children, className = '' }) {
  if (!children) return null;
  
  const text = typeof children === 'string' ? children : String(children);
  const elements = parseMarkdown(text);
  
  return (
    <p className={className}>
      {elements}
    </p>
  );
}

export default { parseMarkdown, MarkdownText, MarkdownParagraph };

