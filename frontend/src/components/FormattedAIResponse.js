import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  ChevronDown, 
  ChevronUp, 
  CheckCircle, 
  ArrowRight, 
  Star,
  Lightbulb,
  Target,
  BookOpen,
  Heart,
  GraduationCap
} from 'lucide-react';

export default function FormattedAIResponse({ content, persona, isLeading = false }) {
  const [expandedSections, setExpandedSections] = useState({});

  const toggleSection = (sectionIndex) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionIndex]: !prev[sectionIndex]
    }));
  };

  // Comprehensive math formatting function
  const formatMathText = (text) => {
    if (!text) return text;
    
    // First handle LaTeX delimiters and convert them to proper math
    let formattedText = text
      // Remove LaTeX inline math delimiters \( and \)
      .replace(/\\?\\\(/g, '')
      .replace(/\\?\\\)/g, '')
      // Remove LaTeX display math delimiters \[ and \]
      .replace(/\\?\\\[/g, '')
      .replace(/\\?\\\]/g, '')
      // Handle escaped backslashes
      .replace(/\\\\/g, '')
      
      // Mathematical expressions
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic text
      
      // Powers and superscripts
      .replace(/([a-zA-Z0-9])\^(-?\d+)/g, (match, base, exp) => {
        const superscripts = {
          '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', 
          '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
          '-': '⁻', '+': '⁺'
        };
        let formattedExp = exp.split('').map(char => superscripts[char] || char).join('');
        return base + formattedExp;
      })
      
      // Common mathematical expressions
      .replace(/x\^2/g, 'x²')
      .replace(/x\^3/g, 'x³')
      .replace(/([a-zA-Z])\^2/g, '$1²')
      .replace(/([a-zA-Z])\^3/g, '$1³')
      
      // Fractions - simple cases
      .replace(/(\d+)\/(\d+)/g, '$1/$2')
      .replace(/\(([^)]+)\)\/\(([^)]+)\)/g, '($1)/($2)')
      
      // Mathematical functions
      .replace(/sqrt\((.*?)\)/g, '√($1)')
      .replace(/\\sqrt\{(.*?)\}/g, '√($1)')
      .replace(/cbrt\((.*?)\)/g, '∛($1)')
      
      // Mathematical symbols
      .replace(/\+\-/g, '±').replace(/\+-/g, '±')
      .replace(/\\pm/g, '±')
      .replace(/\\mp/g, '∓')
      .replace(/->/g, '→').replace(/\\to/g, '→')
      .replace(/<->/g, '↔').replace(/\\leftrightarrow/g, '↔')
      .replace(/<=/g, '≤').replace(/\\leq/g, '≤')
      .replace(/>=/g, '≥').replace(/\\geq/g, '≥')
      .replace(/!=/g, '≠').replace(/\\neq/g, '≠')
      .replace(/\\approx/g, '≈')
      .replace(/\\equiv/g, '≡')
      .replace(/\\propto/g, '∝')
      .replace(/\\infty/g, '∞').replace(/infinity/gi, '∞')
      
      // Greek letters (both uppercase and lowercase)
      .replace(/\\alpha/g, 'α').replace(/alpha/gi, 'α')
      .replace(/\\beta/g, 'β').replace(/beta/gi, 'β')
      .replace(/\\gamma/g, 'γ').replace(/gamma/gi, 'γ')
      .replace(/\\delta/g, 'δ').replace(/delta/gi, 'δ')
      .replace(/\\Delta/g, 'Δ')
      .replace(/\\epsilon/g, 'ε').replace(/epsilon/gi, 'ε')
      .replace(/\\theta/g, 'θ').replace(/theta/gi, 'θ')
      .replace(/\\Theta/g, 'Θ')
      .replace(/\\lambda/g, 'λ').replace(/lambda/gi, 'λ')
      .replace(/\\mu/g, 'μ').replace(/mu/gi, 'μ')
      .replace(/\\pi/g, 'π').replace(/\\Pi/g, 'Π').replace(/\bpi\b/gi, 'π')
      .replace(/\\rho/g, 'ρ').replace(/rho/gi, 'ρ')
      .replace(/\\sigma/g, 'σ').replace(/\\Sigma/g, 'Σ')
      .replace(/\\phi/g, 'φ').replace(/\\Phi/g, 'Φ')
      .replace(/\\omega/g, 'ω').replace(/\\Omega/g, 'Ω')
      
      // Set theory and logic
      .replace(/\\in/g, '∈')
      .replace(/\\notin/g, '∉')
      .replace(/\\subset/g, '⊂')
      .replace(/\\supset/g, '⊃')
      .replace(/\\subseteq/g, '⊆')
      .replace(/\\supseteq/g, '⊇')
      .replace(/\\cup/g, '∪')
      .replace(/\\cap/g, '∩')
      .replace(/\\emptyset/g, '∅')
      .replace(/\\forall/g, '∀')
      .replace(/\\exists/g, '∃')
      
      // Calculus
      .replace(/\\partial/g, '∂')
      .replace(/\\nabla/g, '∇')
      .replace(/\\int/g, '∫')
      
      // Clean up any remaining LaTeX artifacts
      .replace(/\\\w+\{([^}]*)\}/g, '$1') // Remove LaTeX commands with braces
      .replace(/\\\w+/g, '') // Remove remaining LaTeX commands
      .replace(/\s+/g, ' ') // Normalize spaces
      .trim();
    
    return formattedText;
  };

  const parseContent = (text) => {
    if (!text) return [];

    const sections = [];
    const lines = text.split('\n').filter(line => line.trim());
    
    let currentSection = null;
    let currentList = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Handle headers (### Header)
      if (line.startsWith('###')) {
        // Save previous section if exists
        if (currentSection) {
          if (currentList.length > 0) {
            currentSection.content.push({ type: 'list', items: [...currentList] });
            currentList = [];
          }
          sections.push(currentSection);
        }
        
        // Start new section
        currentSection = {
          type: 'section',
          title: line.replace(/^###\s*/, '').replace(/\*\*/g, ''),
          content: [],
          collapsible: true
        };
      }
      // Handle numbered items (1. Item or - Item)
      else if (line.match(/^\d+\.\s/) || line.startsWith('- ')) {
        const item = line.replace(/^\d+\.\s*/, '').replace(/^-\s*/, '').replace(/\*\*/g, '');
        currentList.push(item);
      }
      // Handle bold text (**text**)
      else if (line.includes('**')) {
        const boldText = line.replace(/\*\*/g, '');
        if (currentSection) {
          if (currentList.length > 0) {
            currentSection.content.push({ type: 'list', items: [...currentList] });
            currentList = [];
          }
          currentSection.content.push({ type: 'highlight', text: boldText });
        } else {
          sections.push({ type: 'highlight', text: boldText });
        }
      }
      // Regular paragraph
      else if (line.length > 0) {
        if (currentSection) {
          if (currentList.length > 0) {
            currentSection.content.push({ type: 'list', items: [...currentList] });
            currentList = [];
          }
          currentSection.content.push({ type: 'text', text: line });
        } else {
          sections.push({ type: 'text', text: line });
        }
      }
    }
    
    // Add final section
    if (currentSection) {
      if (currentList.length > 0) {
        currentSection.content.push({ type: 'list', items: [...currentList] });
      }
      sections.push(currentSection);
    }
    
    return sections;
  };

  const renderIcon = (persona, isLeading) => {
    if (persona === 'professor') {
      return <GraduationCap className="h-5 w-5 text-purple-600" />;
    } else {
      return <Heart className="h-5 w-5 text-green-600" />;
    }
  };

  const getPersonaColors = (persona) => {
    if (persona === 'professor') {
      return {
        bg: 'bg-purple-50',
        border: 'border-purple-200',
        text: 'text-purple-700',
        accent: 'bg-purple-500'
      };
    } else {
      return {
        bg: 'bg-green-50',
        border: 'border-green-200',
        text: 'text-green-700',
        accent: 'bg-green-500'
      };
    }
  };

  const colors = getPersonaColors(persona);
  const sections = parseContent(content);

  return (
    <Card className={`${colors.border} shadow-sm hover:shadow-md transition-shadow`}>
      {/* Header */}
      <div className={`${colors.bg} px-4 py-3 border-b ${colors.border}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {renderIcon(persona, isLeading)}
            <div>
              <h3 className={`font-semibold ${colors.text} capitalize`}>
                {persona} {isLeading ? 'Analysis' : 'Insights'}
              </h3>
              <p className="text-xs text-gray-600">
                {persona === 'professor' 
                  ? 'Academic accuracy & structured reasoning' 
                  : 'Personalized guidance & motivation'
                }
              </p>
            </div>
          </div>
          
          <Badge 
            variant={isLeading ? 'default' : 'outline'} 
            className={`text-xs ${isLeading ? colors.text : 'text-gray-600'}`}
          >
            {isLeading ? 'Primary' : 'Supporting'}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <CardContent className="p-0">
        <div className="space-y-4 p-4">
          {sections.map((section, sectionIndex) => {
            if (section.type === 'section') {
              const isExpanded = expandedSections[sectionIndex] !== false; // Default to expanded
              
              return (
                <div key={sectionIndex} className="border rounded-lg overflow-hidden">
                  {/* Section Header */}
                  <div 
                    className={`${colors.bg} px-4 py-3 cursor-pointer hover:bg-opacity-80 transition-colors`}
                    onClick={() => toggleSection(sectionIndex)}
                  >
                    <div className="flex items-center justify-between">
                      <h4 className={`font-medium ${colors.text} flex items-center`}>
                        <Star className="h-4 w-4 mr-2" />
                        {section.title}
                      </h4>
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-gray-500" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-gray-500" />
                      )}
                    </div>
                  </div>

                  {/* Section Content */}
                  {isExpanded && (
                    <div className="p-4 space-y-3">
                      {section.content.map((item, itemIndex) => (
                        <div key={itemIndex}>
                          {item.type === 'text' && (
                            <p className="text-gray-700 leading-relaxed" dangerouslySetInnerHTML={{__html: formatMathText(item.text)}}></p>
                          )}
                          
                          {item.type === 'highlight' && (
                            <div className={`${colors.bg} rounded-lg p-3 border-l-4 ${colors.accent}`}>
                              <div className="flex items-start">
                                <Lightbulb className={`h-4 w-4 ${colors.text} mr-2 mt-0.5 flex-shrink-0`} />
                                <p className={`font-medium ${colors.text}`} dangerouslySetInnerHTML={{__html: formatMathText(item.text)}}></p>
                              </div>
                            </div>
                          )}
                          
                          {item.type === 'list' && (
                            <div className="space-y-2">
                              {item.items.map((listItem, listIndex) => (
                                <div key={listIndex} className="flex items-start">
                                  <CheckCircle className="h-4 w-4 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                                  <p className="text-gray-700 text-sm leading-relaxed" dangerouslySetInnerHTML={{__html: formatMathText(listItem)}}></p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            }
            
            // Handle standalone items (not in sections)
            return (
              <div key={sectionIndex}>
                {section.type === 'text' && (
                  <p className="text-gray-700 leading-relaxed" dangerouslySetInnerHTML={{__html: formatMathText(section.text)}}></p>
                )}
                
                {section.type === 'highlight' && (
                  <div className={`${colors.bg} rounded-lg p-3 border-l-4 ${colors.accent}`}>
                    <div className="flex items-start">
                      <Target className={`h-4 w-4 ${colors.text} mr-2 mt-0.5`} />
                      <p className={`font-medium ${colors.text}`} dangerouslySetInnerHTML={{__html: formatMathText(section.text)}}></p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

// Helper component for dual response container
export function DualResponseContainer({ 
  primaryResponse, 
  secondaryResponse, 
  scenarioType, 
  confidence,
  timestamp 
}) {
  return (
    <div className="space-y-6 max-w-5xl">
      {/* Scenario Indicator */}
      <div className="flex items-center justify-center">
        <Badge variant="outline" className="text-xs px-3 py-1">
          <Target className="h-3 w-3 mr-1" />
          {scenarioType.replace('_', ' ')} scenario • {Math.round(confidence * 100)}% confidence
        </Badge>
      </div>

      {/* Primary Response */}
      <FormattedAIResponse
        content={primaryResponse.response}
        persona={primaryResponse.persona}
        isLeading={true}
      />

      {/* Secondary Response (if exists) */}
      {secondaryResponse.response && (
        <FormattedAIResponse
          content={secondaryResponse.response}
          persona={secondaryResponse.persona}
          isLeading={false}
        />
      )}

      {/* Action Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="flex items-center space-x-4 text-xs text-gray-500">
          <span>Dual Intelligence Response</span>
          <span>•</span>
          <span>{timestamp}</span>
        </div>
        
        <div className="flex space-x-2">
          <Button 
            variant="ghost" 
            size="sm" 
            className="text-xs hover:text-blue-600"
            onClick={() => navigator.clipboard.writeText(`Professor: ${primaryResponse.response}\n\nMentor: ${secondaryResponse.reasoning || secondaryResponse.response}`)}
            title="Copy full response"
          >
            <BookOpen className="h-3 w-3 mr-1" />
            Copy Response
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            className="text-xs hover:text-yellow-600"
            title="Bookmark this response"
          >
            <Star className="h-3 w-3 mr-1" />
            Bookmark
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            className="text-xs hover:text-green-600"
            title="Ask follow-up question"
          >
            <ArrowRight className="h-3 w-3 mr-1" />
            Follow Up
          </Button>
        </div>
      </div>
    </div>
  );
}