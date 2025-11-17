/**
 * Simple Markdown Renderer for Student-Friendly Content
 * Handles: **bold**, *italic*, `code`, and preserves structure
 */

import React from 'react';

/**
 * Parse markdown text and return React elements with proper formatting
 * @param {string} text - Text with markdown formatting
 * @returns {React.ReactElement[]} - Array of React elements
 */
export function parseMarkdown(text) {
  if (!text) return [];
  
  const elements = [];
  let currentIndex = 0;
  const patterns = [
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
    while ((match = regex.exec(text)) !== null) {
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
  
  // Build elements
  let lastEnd = 0;
  matches.forEach((match, idx) => {
    // Add text before this match
    if (match.start > lastEnd) {
      const beforeText = text.substring(lastEnd, match.start);
      if (beforeText) {
        elements.push(<span key={`text-${idx}`}>{beforeText}</span>);
      }
    }
    
    // Add formatted element
    switch (match.type) {
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
  if (lastEnd < text.length) {
    const remainingText = text.substring(lastEnd);
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

