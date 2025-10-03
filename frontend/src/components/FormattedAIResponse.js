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
  GraduationCap,
  FileText,
  Plus,
  ThumbsUp,
  TrendingDown,
  TrendingUp,
  AlertCircle,
  Calculator,
  Link2,
  Zap,
  CreditCard,
  Clock,
  Shield,
  Award,
  Activity
} from 'lucide-react';

export default function FormattedAIResponse({ 
  content, 
  persona, 
  isLeading = false, 
  onPracticMore, 
  onAddToNotes, 
  onFeedback 
}) {
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

      {/* Enhanced Action Buttons with Personalization Feedback */}
      <div className="border-t p-4 bg-gray-50">
        <div className="space-y-3">
          {/* Traditional Actions */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                navigator.clipboard.writeText(content);
                alert('Response copied to clipboard!');
              }}
              className="text-gray-600 hover:text-gray-800"
            >
              <FileText className="h-3 w-3 mr-1" />
              Copy
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                // TODO: Implement bookmarking
                alert('Bookmarked for future reference!');
              }}
              className="text-gray-600 hover:text-gray-800"
            >
              <BookOpen className="h-3 w-3 mr-1" />
              Bookmark
            </Button>

            {onPracticMore && (
              <Button
                variant="outline"
                size="sm"
                onClick={onPracticMore}
                className="text-blue-600 hover:text-blue-800 border-blue-300 hover:border-blue-400"
              >
                <Target className="h-3 w-3 mr-1" />
                Practice More
              </Button>
            )}

            {onAddToNotes && (
              <Button
                variant="outline"
                size="sm"
                onClick={onAddToNotes}
                className="text-green-600 hover:text-green-800 border-green-300 hover:border-green-400"
              >
                <Plus className="h-3 w-3 mr-1" />
                Add to Notes
              </Button>
            )}
          </div>

          {/* Personalization Feedback */}
          {onFeedback && (
            <div className="border-t pt-3">
              <p className="text-xs text-gray-600 mb-2">💡 Help us personalize your learning:</p>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onFeedback('perfect')}
                  className="text-green-600 hover:text-green-800 border-green-300 hover:border-green-400 hover:bg-green-50"
                >
                  <ThumbsUp className="h-3 w-3 mr-1" />
                  Perfect! 🎯
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onFeedback('helpful')}
                  className="text-blue-600 hover:text-blue-800 border-blue-300 hover:border-blue-400 hover:bg-blue-50"
                >
                  <Heart className="h-3 w-3 mr-1" />
                  Helpful ✨
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onFeedback('too_easy')}
                  className="text-yellow-600 hover:text-yellow-800 border-yellow-300 hover:border-yellow-400 hover:bg-yellow-50"
                >
                  <TrendingDown className="h-3 w-3 mr-1" />
                  Too Easy 😴
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onFeedback('too_hard')}
                  className="text-orange-600 hover:text-orange-800 border-orange-300 hover:border-orange-400 hover:bg-orange-50"
                >
                  <TrendingUp className="h-3 w-3 mr-1" />
                  Too Hard 🤯
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onFeedback('confusing')}
                  className="text-red-600 hover:text-red-800 border-red-300 hover:border-red-400 hover:bg-red-50"
                >
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Confusing 😕
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

// Helper component for dual response container with progressive disclosure
export function DualResponseContainer({ 
  primaryResponse, 
  secondaryResponse, 
  scenarioType, 
  confidence,
  timestamp,
  guardrails,
  disagreementAlert,
  actionButtons,
  analytics,
  onFeedback,
  onPracticMore,
  onAddToNotes,
  onCreateFlashcards,
  onScheduleRevision
}) {
  const [expandedSections, setExpandedSections] = useState({
    references: false,
    actions: false,
    progress: false,
    insights: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <div className="space-y-4 max-w-4xl">
      {/* Clean Primary Answer */}
      <div className="bg-white rounded-lg border border-gray-100 shadow-sm">
        {/* Main Answer Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-100">
          <div className="flex items-center space-x-3">
            {primaryResponse.persona === 'professor' ? (
              <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center">
                <GraduationCap className="h-4 w-4 text-teal-600" />
              </div>
            ) : (
              <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center">
                <Heart className="h-4 w-4 text-teal-600" />
              </div>
            )}
            <div>
              <h3 className="font-medium text-gray-900 capitalize">
                {primaryResponse.persona} Answer
              </h3>
              <p className="text-xs text-gray-500">
                {primaryResponse.persona === 'professor' ? 'Academic & Structured' : 'Adaptive & Motivational'}
              </p>
            </div>
          </div>
          
          <Badge variant="outline" className="text-xs text-gray-600">
            {Math.round(confidence * 100)}% confident
          </Badge>
        </div>

        {/* Main Answer Content */}
        <div className="p-4">
          <div className="prose prose-sm max-w-none">
            <div 
              className="text-gray-800 leading-relaxed"
              dangerouslySetInnerHTML={{
                __html: formatMathExpressions(primaryResponse.response)
              }}
            />
          </div>

          {/* Basic Feedback */}
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
            <div className="flex items-center space-x-2">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => onFeedback && onFeedback('helpful')}
                className="text-gray-500 hover:text-teal-600"
              >
                <ThumbsUp className="h-4 w-4 mr-1" />
                Helpful
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigator.clipboard.writeText(primaryResponse.response)}
                className="text-gray-500 hover:text-teal-600"
              >
                <BookOpen className="h-4 w-4 mr-1" />
                Copy
              </Button>
            </div>
            <span className="text-xs text-gray-400">{timestamp}</span>
          </div>
        </div>
      </div>

      {/* Progressive Disclosure Sections */}
      <div className="space-y-2">
        
        {/* Additional Insights (Secondary Response) */}
        {secondaryResponse.response && (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <Button
              variant="ghost"
              onClick={() => toggleSection('insights')}
              className="w-full flex items-center justify-between p-3 hover:bg-gray-50"
            >
              <div className="flex items-center space-x-2">
                <Heart className="h-4 w-4 text-teal-600" />
                <span className="font-medium text-gray-700">Additional Perspective</span>
                <Badge variant="outline" className="text-xs">
                  {secondaryResponse.persona}
                </Badge>
              </div>
              {expandedSections.insights ? (
                <ChevronUp className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              )}
            </Button>
            
            {expandedSections.insights && (
              <div className="p-4 border-t border-gray-100 bg-gray-50">
                <div 
                  className="text-gray-700 text-sm leading-relaxed"
                  dangerouslySetInnerHTML={{
                    __html: formatMathExpressions(secondaryResponse.response)
                  }}
                />
              </div>
            )}
          </div>
        )}

        {/* References & Sources */}
        {(guardrails?.citations?.length > 0 || guardrails?.math_validation) && (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <Button
              variant="ghost"
              onClick={() => toggleSection('references')}
              className="w-full flex items-center justify-between p-3 hover:bg-gray-50"
            >
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4 text-teal-600" />
                <span className="font-medium text-gray-700">References & Verification</span>
                {guardrails?.math_validation?.is_valid && (
                  <Badge variant="default" className="text-xs bg-green-100 text-green-700">
                    Verified
                  </Badge>
                )}
              </div>
              {expandedSections.references ? (
                <ChevronUp className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              )}
            </Button>
            
            {expandedSections.references && (
              <div className="p-4 border-t border-gray-100 bg-gray-50 space-y-3">
                {/* Math Validation */}
                {guardrails?.math_validation && (
                  <div className="bg-white rounded p-3 border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Math Validation</span>
                      <Badge variant={guardrails.math_validation.is_valid ? "default" : "destructive"}>
                        {guardrails.math_validation.is_valid ? "Valid" : "Check Required"}
                      </Badge>
                    </div>
                    {guardrails.math_validation.result && (
                      <p className="text-xs text-gray-600">Result: {guardrails.math_validation.result}</p>
                    )}
                  </div>
                )}
                
                {/* Citations */}
                {guardrails?.citations?.length > 0 && (
                  <div className="bg-white rounded p-3 border">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Academic References</h5>
                    <div className="space-y-1">
                      {guardrails.citations.slice(0, 3).map((citation, idx) => (
                        <div key={idx} className="text-xs text-gray-600">
                          <span className="font-medium">{idx + 1}.</span> {citation.source_title}
                          {citation.chapter_section && (
                            <span className="text-gray-500"> ({citation.chapter_section})</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        {actionButtons && (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <Button
              variant="ghost"
              onClick={() => toggleSection('actions')}
              className="w-full flex items-center justify-between p-3 hover:bg-gray-50"
            >
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4 text-teal-600" />
                <span className="font-medium text-gray-700">Study Actions</span>
                <Badge variant="outline" className="text-xs">
                  Enhance Learning
                </Badge>
              </div>
              {expandedSections.actions ? (
                <ChevronUp className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              )}
            </Button>
            
            {expandedSections.actions && (
              <div className="p-4 border-t border-gray-100 bg-gray-50">
                <div className="grid grid-cols-2 gap-3">
                  {actionButtons.practice_more_available && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={onPracticMore}
                      className="flex items-center justify-center p-3 text-center hover:bg-teal-50 border-teal-200"
                    >
                      <Target className="h-4 w-4 mr-2 text-teal-600" />
                      <div>
                        <div className="text-xs font-medium">Practice More</div>
                        <div className="text-xs text-gray-500">Similar problems</div>
                      </div>
                    </Button>
                  )}
                  
                  {actionButtons.add_to_notes_available && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={onAddToNotes}
                      className="flex items-center justify-center p-3 text-center hover:bg-teal-50 border-teal-200"
                    >
                      <BookOpen className="h-4 w-4 mr-2 text-teal-600" />
                      <div>
                        <div className="text-xs font-medium">Add to Notes</div>
                        <div className="text-xs text-gray-500">Save for later</div>
                      </div>
                    </Button>
                  )}
                  
                  {actionButtons.create_flashcards_available && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={onCreateFlashcards}
                      className="flex items-center justify-center p-3 text-center hover:bg-teal-50 border-teal-200"
                    >
                      <CreditCard className="h-4 w-4 mr-2 text-teal-600" />
                      <div>
                        <div className="text-xs font-medium">Turn into Deck</div>
                        <div className="text-xs text-gray-500">Make flashcards</div>
                      </div>
                    </Button>
                  )}
                  
                  {actionButtons.schedule_revision_available && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={onScheduleRevision}
                      className="flex items-center justify-center p-3 text-center hover:bg-teal-50 border-teal-200"
                    >
                      <Clock className="h-4 w-4 mr-2 text-teal-600" />
                      <div>
                        <div className="text-xs font-medium">Schedule Revision</div>
                        <div className="text-xs text-gray-500">Spaced learning</div>
                      </div>
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Learning Progress */}
        {analytics?.performance_stats && (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <Button
              variant="ghost"
              onClick={() => toggleSection('progress')}
              className="w-full flex items-center justify-between p-3 hover:bg-gray-50"
            >
              <div className="flex items-center space-x-2">
                <Activity className="h-4 w-4 text-teal-600" />
                <span className="font-medium text-gray-700">Learning Progress</span>
                <Badge variant="outline" className="text-xs">
                  Your Stats
                </Badge>
              </div>
              {expandedSections.progress ? (
                <ChevronUp className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              )}
            </Button>
            
            {expandedSections.progress && (
              <div className="p-4 border-t border-gray-100 bg-gray-50">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-lg font-bold text-teal-600">
                      {analytics.performance_stats.study_streak}
                    </div>
                    <div className="text-xs text-gray-600">Day Streak</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-teal-600">
                      {analytics.performance_stats.total_interactions}
                    </div>
                    <div className="text-xs text-gray-600">Questions Asked</div>
                  </div>
                </div>
                
                {analytics.performance_stats.recommendations?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-medium text-gray-700 mb-2">💡 Recommendations:</p>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {analytics.performance_stats.recommendations.slice(0, 2).map((rec, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-teal-500 mr-1">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Disagreement Alert */}
        {disagreementAlert && (
          <div className="border border-yellow-200 bg-yellow-50 rounded-lg p-3">
            <div className="flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-yellow-800">
                  Our AI tutors have slightly different approaches to this problem. 
                  This provides richer learning perspectives!
                </p>
                <Badge variant="outline" className="text-xs text-yellow-700 mt-2">
                  {disagreementAlert.conflict_type}
                </Badge>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Export the math formatting function for use in other components
export function formatMathExpressions(text) {
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
}