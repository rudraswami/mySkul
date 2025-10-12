import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Book, Lightbulb, TrendingUp, Zap, CheckCircle, Brain } from 'lucide-react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * SemanticAIResponse - Phase 2/3 Enhanced Rendering
 * Renders AI responses with color-coded sections, rich text emphasis, and semantic structure
 */
const SemanticAIResponse = ({ content, type = 'professor' }) => {
  if (!content) return null;

  // Parse section tags from backend
  const parseSections = (text) => {
    const sections = {};
    const sectionRegex = /\[SECTION:(\w+)\]([\s\S]*?)\[\/SECTION:\1\]/g;
    const microcardRegex = /\[MICROCARD:(\w+)\]([\s\S]*?)\[\/MICROCARD:\1\]/g;
    
    let match;
    
    // Parse Professor sections
    while ((match = sectionRegex.exec(text)) !== null) {
      sections[match[1].toLowerCase()] = match[2].trim();
    }
    
    // Parse Mentor microcards
    while ((match = microcardRegex.exec(text)) !== null) {
      sections[match[1].toLowerCase()] = match[2].trim();
    }
    
    // If no sections found, treat entire content as generic
    if (Object.keys(sections).length === 0) {
      sections['content'] = text;
    }
    
    return sections;
  };

  // Render rich text with emphasis (key terms bolding, LaTeX)
  const renderRichText = (text) => {
    if (!text) return null;

    // Replace <key>term</key> with bold spans
    let processed = text.replace(/<key>(.*?)<\/key>/g, '<strong class="text-gray-900 font-semibold">$1</strong>');
    
    // LaTeX inline math: \( \) → stay as is for KaTeX
    // LaTeX display math: \[ \] → stay as is for KaTeX
    // No processing needed - KaTeX handles this
    
    // Split by LaTeX delimiters to preserve them
    const parts = processed.split(/(\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\))/);
    
    return (
      <span dangerouslySetInnerHTML={{ __html: processed }} />
    );
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

  // Render Mentor microcards
  if (type === 'mentor') {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
    );
  }

  return null;
};

export default SemanticAIResponse;
