import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Book, Lightbulb, TrendingUp, Zap, CheckCircle, Brain, ChevronDown, ChevronUp, Heart } from 'lucide-react';
import AdaptiveMarkdown from './AdaptiveMarkdown';
import 'katex/dist/katex.min.css';

/**
 * SemanticAIResponse - Phase 2/3 Enhanced Rendering
 * Renders AI responses with color-coded sections, rich text emphasis, and semantic structure
 */
const SemanticAIResponse = ({ content, type = 'professor' }) => {
  const [isMentorExpanded, setIsMentorExpanded] = useState(false);
  
  if (!content) return null;
  
  // Strip any remaining visible tags that weren't properly closed
  const stripUnparsedTags = (text) => {
    if (!text) return text;
    // Remove any visible [SECTION:*] or [MICROCARD:*] tags that weren't parsed
    return text
      .replace(/\[SECTION:\w+\]/g, '')
      .replace(/\[\/SECTION:\w+\]/g, '')
      .replace(/\[MICROCARD:\w+\]/g, '')
      .replace(/\[\/MICROCARD:\w+\]/g, '');
  };

  // Parse section tags from backend with enhanced fallback logic
  const parseSections = (text) => {
    const sections = {};
    const sectionRegex = /\[SECTION:(\w+)\]([\s\S]*?)\[\/SECTION:\1\]/gi;
    const microcardRegex = /\[MICROCARD:(\w+)\]([\s\S]*?)\[\/MICROCARD:\1\]/gi;
    
    let match;
    let foundSections = false;
    
    // Parse Professor sections
    sectionRegex.lastIndex = 0; // Reset regex state
    while ((match = sectionRegex.exec(text)) !== null) {
      sections[match[1].toLowerCase()] = stripUnparsedTags(match[2].trim());
      foundSections = true;
    }
    
    // Parse Mentor microcards
    microcardRegex.lastIndex = 0; // Reset regex state
    while ((match = microcardRegex.exec(text)) !== null) {
      sections[match[1].toLowerCase()] = stripUnparsedTags(match[2].trim());
      foundSections = true;
    }
    
    // Enhanced fallback: If no sections found, use intelligent content splitting
    if (!foundSections) {
      // Strip any unparsed tags from the entire text first
      const cleanedText = stripUnparsedTags(text);
      
      // For Professor: Try to detect natural sections by paragraph structure
      if (type === 'professor') {
        const paragraphs = cleanedText.split('\n\n').filter(p => p.trim());
        if (paragraphs.length >= 3) {
          // First paragraph as concept
          sections['concept'] = paragraphs[0];
          // Middle paragraphs as steps
          if (paragraphs.length > 3) {
            sections['steps'] = paragraphs.slice(1, -1).join('\n\n');
          }
          // Last paragraph as pro tip
          sections['protip'] = paragraphs[paragraphs.length - 1];
        } else {
          sections['content'] = cleanedText;
        }
      } else {
        // For Mentor: Treat as motivation message
        sections['motivation'] = cleanedText;
      }
    }
    
    return sections;
  };

  // Use AdaptiveMarkdown for rich text rendering with full LaTeX support
  const renderRichText = (text) => {
    if (!text) return null;
    return <AdaptiveMarkdown content={text} animate={false} />;
  };

  const sections = parseSections(content);

  // Color scheme for sections
  const sectionColors = {
    concept: { bg: 'bg-blue-50', border: 'border-blue-300', badge: 'bg-blue-500', text: 'text-blue-700' },
    formulas: { bg: 'bg-orange-50', border: 'border-orange-300', badge: 'bg-orange-500', text: 'text-orange-700' },
    steps: { bg: 'bg-teal-50', border: 'border-teal-300', badge: 'bg-teal-500', text: 'text-teal-700' },
    realworld: { bg: 'bg-green-50', border: 'border-green-300', badge: 'bg-green-500', text: 'text-green-700' },
    protip: { bg: 'bg-purple-50', border: 'border-purple-300', badge: 'bg-purple-500', text: 'text-purple-700' }
  };

  const mentorColors = {
    motivation: { bg: 'bg-pink-50', border: 'border-pink-300', badge: 'bg-pink-500', icon: Brain },
    recap: { bg: 'bg-blue-50', border: 'border-blue-300', badge: 'bg-blue-500', icon: CheckCircle },
    examboost: { bg: 'bg-yellow-50', border: 'border-yellow-300', badge: 'bg-yellow-500', icon: Zap },
    encouragement: { bg: 'bg-green-50', border: 'border-green-300', badge: 'bg-green-500', icon: TrendingUp }
  };

  // Render Professor sections
  if (type === 'professor') {
    return (
      <div className="space-y-4">
        {/* Concept Overview Section */}
        {sections.concept && (
          <div className={`${sectionColors.concept.bg} border-l-4 ${sectionColors.concept.border} rounded-lg p-4`}>
            <div className="flex items-center mb-3">
              <Badge className={`${sectionColors.concept.badge} text-white mr-2 px-3 py-1`}>
                <Book className="h-4 w-4 mr-1 inline" />
                Concept
              </Badge>
              <span className={`text-sm font-semibold ${sectionColors.concept.text}`}>Core Understanding</span>
            </div>
            <div className="text-gray-800 leading-relaxed">
              {renderRichText(sections.concept)}
            </div>
          </div>
        )}

        {/* Formulas Section */}
        {sections.formulas && (
          <div className={`${sectionColors.formulas.bg} border-l-4 ${sectionColors.formulas.border} rounded-lg p-4`}>
            <div className="flex items-center mb-3">
              <Badge className={`${sectionColors.formulas.badge} text-white mr-2 px-3 py-1`}>
                <span className="mr-1">📐</span>
                Formulas
              </Badge>
              <span className={`text-sm font-semibold ${sectionColors.formulas.text}`}>Key Equations</span>
            </div>
            <div className="text-gray-800 leading-relaxed font-mono text-sm bg-white p-3 rounded border border-orange-200">
              {renderRichText(sections.formulas)}
            </div>
          </div>
        )}

        {/* Step-by-Step Section */}
        {sections.steps && (
          <div className={`${sectionColors.steps.bg} border-l-4 ${sectionColors.steps.border} rounded-lg p-4`}>
            <div className="flex items-center mb-3">
              <Badge className={`${sectionColors.steps.badge} text-white mr-2 px-3 py-1`}>
                <Lightbulb className="h-4 w-4 mr-1 inline" />
                Steps
              </Badge>
              <span className={`text-sm font-semibold ${sectionColors.steps.text}`}>Deep Explanation</span>
            </div>
            <div className="text-gray-800 leading-relaxed space-y-2">
              {renderRichText(sections.steps)}
            </div>
          </div>
        )}

        {/* Real-World Section */}
        {sections.realworld && (
          <div className={`${sectionColors.realworld.bg} border-l-4 ${sectionColors.realworld.border} rounded-lg p-4`}>
            <div className="flex items-center mb-3">
              <Badge className={`${sectionColors.realworld.badge} text-white mr-2 px-3 py-1`}>
                <span className="mr-1">🌍</span>
                Real-World
              </Badge>
              <span className={`text-sm font-semibold ${sectionColors.realworld.text}`}>Practical Application</span>
            </div>
            <div className="text-gray-800 leading-relaxed">
              {renderRichText(sections.realworld)}
            </div>
          </div>
        )}

        {/* Pro Tip Section */}
        {sections.protip && (
          <div className={`${sectionColors.protip.bg} border-l-4 ${sectionColors.protip.border} rounded-lg p-4`}>
            <div className="flex items-center mb-3">
              <Badge className={`${sectionColors.protip.badge} text-white mr-2 px-3 py-1`}>
                <Zap className="h-4 w-4 mr-1 inline" />
                Pro Tip
              </Badge>
              <span className={`text-sm font-semibold ${sectionColors.protip.text}`}>Exam Strategy</span>
            </div>
            <div className="text-gray-800 leading-relaxed font-medium">
              {renderRichText(sections.protip)}
            </div>
          </div>
        )}

        {/* Fallback: render unsectioned content */}
        {sections.content && !sections.concept && (
          <div className="text-gray-800 leading-relaxed">
            {renderRichText(sections.content)}
          </div>
        )}
      </div>
    );
  }

  // Render Mentor microcards with collapsible container
  if (type === 'mentor') {
    return (
      <div className="space-y-2">
        {/* Collapsible Header */}
        <button
          onClick={() => setIsMentorExpanded(!isMentorExpanded)}
          className="w-full flex items-center justify-between p-3 bg-gradient-to-r from-green-100 to-blue-100 hover:from-green-200 hover:to-blue-200 rounded-lg transition-colors duration-200 border-2 border-green-300"
        >
          <div className="flex items-center space-x-2">
            <Heart className="h-5 w-5 text-green-600" />
            <span className="font-semibold text-gray-900">Mentor's Strategic Guidance</span>
            <Badge variant="outline" className="text-xs">Click to {isMentorExpanded ? 'collapse' : 'expand'}</Badge>
          </div>
          {isMentorExpanded ? (
            <ChevronUp className="h-5 w-5 text-gray-600" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-600" />
          )}
        </button>
        
        {/* Collapsible Content */}
        {isMentorExpanded && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        {/* Motivation Microcard */}
        {sections.motivation && (
          <Card className={`${mentorColors.motivation.bg} border-2 ${mentorColors.motivation.border}`}>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center text-base">
                <Badge className={`${mentorColors.motivation.badge} text-white mr-2`}>
                  {React.createElement(mentorColors.motivation.icon, { className: "h-4 w-4" })}
                </Badge>
                <span className="text-pink-900">Motivation</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-800 leading-relaxed text-sm">
                {renderRichText(sections.motivation)}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Recap Microcard */}
        {sections.recap && (
          <Card className={`${mentorColors.recap.bg} border-2 ${mentorColors.recap.border}`}>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center text-base">
                <Badge className={`${mentorColors.recap.badge} text-white mr-2`}>
                  {React.createElement(mentorColors.recap.icon, { className: "h-4 w-4" })}
                </Badge>
                <span className="text-blue-900">Key Takeaways</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-gray-800 leading-relaxed text-sm space-y-1">
                {renderRichText(sections.recap)}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Exam Booster Microcard */}
        {sections.examboost && (
          <Card className={`${mentorColors.examboost.bg} border-2 ${mentorColors.examboost.border}`}>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center text-base">
                <Badge className={`${mentorColors.examboost.badge} text-white mr-2`}>
                  {React.createElement(mentorColors.examboost.icon, { className: "h-4 w-4" })}
                </Badge>
                <span className="text-yellow-900">Exam Booster</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-gray-800 leading-relaxed text-sm">
                {renderRichText(sections.examboost)}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Encouragement Microcard */}
        {sections.encouragement && (
          <Card className={`${mentorColors.encouragement.bg} border-2 ${mentorColors.encouragement.border}`}>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center text-base">
                <Badge className={`${mentorColors.encouragement.badge} text-white mr-2`}>
                  {React.createElement(mentorColors.encouragement.icon, { className: "h-4 w-4" })}
                </Badge>
                <span className="text-green-900">You Got This!</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-800 leading-relaxed text-sm font-medium">
                {renderRichText(sections.encouragement)}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Fallback: render unsectioned content */}
        {sections.content && !sections.motivation && (
          <div className="col-span-2 text-gray-800 leading-relaxed">
            {renderRichText(sections.content)}
          </div>
        )}
          </div>
        )}
      </div>
    );
  }

  return null;
};

export default SemanticAIResponse;
