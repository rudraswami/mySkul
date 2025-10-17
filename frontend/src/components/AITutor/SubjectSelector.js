/**
 * SubjectSelector Component
 * 
 * Allows users to select subject, AI mode, depth level, and exam mode
 * Compact UI with tooltips for mode explanations
 */

import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Brain, Sparkles, GraduationCap, Zap, Target } from 'lucide-react';

const SubjectSelector = ({ 
  subject = 'Mathematics',
  aiMode = 'dual',
  depthLevel = 'standard',
  examMode = 'JEE',
  onSubjectChange,
  onAIModeChange,
  onDepthLevelChange,
  onExamModeChange,
  disabled = false
}) => {
  const subjects = [
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'Computer Science',
    'English',
    'History',
    'Geography',
    'Economics',
    'General'
  ];

  const aiModes = [
    { 
      value: 'dual', 
      label: 'Dual (Mentor + Professor)', 
      icon: Brain,
      description: 'Get both friendly and technical explanations'
    },
    { 
      value: 'mentor', 
      label: 'Mentor Only', 
      icon: Sparkles,
      description: 'Friendly, encouraging, relatable'
    },
    { 
      value: 'professor', 
      label: 'Professor Only', 
      icon: GraduationCap,
      description: 'Technical, detailed, academic'
    }
  ];

  const depthLevels = [
    { value: 'quick', label: 'Quick', icon: Zap, color: 'green' },
    { value: 'standard', label: 'Standard', icon: Target, color: 'blue' },
    { value: 'deep', label: 'Deep Dive', icon: Brain, color: 'purple' }
  ];

  const examModes = [
    'JEE',
    'NEET',
    'CBSE',
    'ICSE',
    'State Board',
    'SAT',
    'General'
  ];

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-3">
      <div className="flex flex-wrap items-center gap-3">
        {/* Subject Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Subject:
          </span>
          <Select 
            value={subject} 
            onValueChange={onSubjectChange}
            disabled={disabled}
          >
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {subjects.map(subj => (
                <SelectItem key={subj} value={subj}>
                  {subj}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* AI Mode Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Mode:
          </span>
          <Select 
            value={aiMode} 
            onValueChange={onAIModeChange}
            disabled={disabled}
          >
            <SelectTrigger className="w-52">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {aiModes.map(mode => {
                const Icon = mode.icon;
                return (
                  <SelectItem key={mode.value} value={mode.value}>
                    <div className="flex items-center space-x-2">
                      <Icon className="h-4 w-4" />
                      <div>
                        <div className="font-medium">{mode.label}</div>
                        <div className="text-xs text-gray-500">{mode.description}</div>
                      </div>
                    </div>
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        </div>

        {/* Depth Level */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Depth:
          </span>
          <div className="flex space-x-1">
            {depthLevels.map(level => {
              const Icon = level.icon;
              const isActive = depthLevel === level.value;
              return (
                <button
                  key={level.value}
                  onClick={() => onDepthLevelChange(level.value)}
                  disabled={disabled}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center space-x-1 ${
                    isActive
                      ? `bg-${level.color}-600 text-white`
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                  title={level.label}
                  style={isActive ? {
                    backgroundColor: 
                      level.color === 'green' ? '#10b981' :
                      level.color === 'blue' ? '#3b82f6' :
                      '#9333ea'
                  } : {}}
                >
                  <Icon className="h-4 w-4" />
                  <span>{level.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Exam Mode */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Exam:
          </span>
          <Select 
            value={examMode} 
            onValueChange={onExamModeChange}
            disabled={disabled}
          >
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {examModes.map(exam => (
                <SelectItem key={exam} value={exam}>
                  {exam}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Active Filters Badge */}
        {(aiMode !== 'dual' || depthLevel !== 'standard') && (
          <Badge variant="secondary" className="ml-auto">
            {aiMode !== 'dual' && (
              <span className="capitalize">{aiMode}</span>
            )}
            {aiMode !== 'dual' && depthLevel !== 'standard' && ' • '}
            {depthLevel !== 'standard' && (
              <span className="capitalize">{depthLevel}</span>
            )}
          </Badge>
        )}
      </div>
    </div>
  );
};

export default React.memo(SubjectSelector);
