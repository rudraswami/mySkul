import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  BookOpen, 
  Target, 
  Clock, 
  Zap, 
  ChevronRight, 
  ChevronLeft,
  CheckCircle,
  Circle,
  Settings,
  Play,
  Brain,
  Timer,
  BarChart3
} from 'lucide-react';

const EXAM_TYPES = [
  { 
    id: 'JEE', 
    name: 'JEE Main/Advanced', 
    icon: '🎓',
    color: 'bg-blue-500',
    subjects: ['Mathematics', 'Physics', 'Chemistry']
  },
  { 
    id: 'NEET', 
    name: 'NEET', 
    icon: '🏥',
    color: 'bg-green-500',
    subjects: ['Physics', 'Chemistry', 'Biology']
  },
  { 
    id: 'UPSC', 
    name: 'UPSC', 
    icon: '⚖️',
    color: 'bg-purple-500',
    subjects: ['General Studies', 'History', 'Geography', 'Polity', 'Economics']
  }
];

export default function TestGenerationWizard({ onGenerate, onCancel, defaultExamType = 'JEE' }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [config, setConfig] = useState({
    examType: defaultExamType,
    subjects: [],
    difficulty: 3,
    numQuestions: 25,
    timerEnabled: true,
    timerDuration: 30 // minutes
  });

  const totalSteps = 4;
  const progress = (currentStep / totalSteps) * 100;

  // Get available subjects for selected exam type
  const availableSubjects = EXAM_TYPES.find(e => e.id === config.examType)?.subjects || [];

  const updateConfig = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const toggleSubject = (subject) => {
    setConfig(prev => ({
      ...prev,
      subjects: prev.subjects.includes(subject)
        ? prev.subjects.filter(s => s !== subject)
        : [...prev.subjects, subject]
    }));
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return config.examType !== '';
      case 2:
        return config.subjects.length > 0;
      case 3:
        return true;
      case 4:
        return true;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (canProceed() && currentStep < totalSteps) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleGenerate = () => {
    onGenerate(config);
  };

  const getDifficultyLabel = (level) => {
    const labels = {
      1: 'Very Easy',
      2: 'Easy',
      3: 'Medium',
      4: 'Hard',
      5: 'Very Hard'
    };
    return labels[level] || 'Medium';
  };

  const getDifficultyColor = (level) => {
    const colors = {
      1: 'text-green-600 bg-green-50',
      2: 'text-blue-600 bg-blue-50',
      3: 'text-yellow-600 bg-yellow-50',
      4: 'text-orange-600 bg-orange-50',
      5: 'text-red-600 bg-red-50'
    };
    return colors[level] || 'text-gray-600 bg-gray-50';
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Create Your Mock Test</h2>
            <p className="text-gray-600">Step {currentStep} of {totalSteps}</p>
          </div>
          <Button variant="outline" onClick={onCancel} size="sm">
            Cancel
          </Button>
        </div>
        <Progress value={progress} className="h-2" />
        
        {/* Step Indicators */}
        <div className="flex justify-between mt-4">
          {[1, 2, 3, 4].map((step) => (
            <div
              key={step}
              className={`flex items-center gap-2 ${
                step <= currentStep ? 'text-blue-600' : 'text-gray-400'
              }`}
            >
              {step < currentStep ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <Circle className={`w-5 h-5 ${step === currentStep ? 'fill-current' : ''}`} />
              )}
              <span className="text-sm font-medium hidden md:inline">
                {step === 1 && 'Exam Type'}
                {step === 2 && 'Subjects'}
                {step === 3 && 'Configure'}
                {step === 4 && 'Review'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <Card className="border-0 shadow-xl">
        <CardContent className="p-8">
          {/* Step 1: Exam Type Selection */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <BookOpen className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-800 mb-2">Select Your Exam</h3>
                <p className="text-gray-600">Choose the exam you're preparing for</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {EXAM_TYPES.map((exam) => (
                  <button
                    key={exam.id}
                    onClick={() => updateConfig('examType', exam.id)}
                    className={`p-6 rounded-xl border-2 transition-all hover:shadow-lg ${
                      config.examType === exam.id
                        ? 'border-blue-500 bg-blue-50 shadow-md'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="text-4xl mb-3">{exam.icon}</div>
                    <h4 className="font-semibold text-gray-800 mb-2">{exam.name}</h4>
                    <div className="flex flex-wrap gap-1 justify-center">
                      {exam.subjects.slice(0, 3).map((subject, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {subject}
                        </Badge>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Subject Selection */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <Target className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-800 mb-2">Choose Subjects</h3>
                <p className="text-gray-600">Select one or more subjects to include in your test</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {availableSubjects.map((subject) => (
                  <button
                    key={subject}
                    onClick={() => toggleSubject(subject)}
                    className={`p-4 rounded-lg border-2 transition-all hover:shadow-md flex items-center gap-3 ${
                      config.subjects.includes(subject)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div className={`w-6 h-6 rounded border-2 flex items-center justify-center ${
                      config.subjects.includes(subject)
                        ? 'bg-blue-500 border-blue-500'
                        : 'border-gray-300'
                    }`}>
                      {config.subjects.includes(subject) && (
                        <CheckCircle className="w-4 h-4 text-white" />
                      )}
                    </div>
                    <span className="font-medium text-gray-800">{subject}</span>
                  </button>
                ))}
              </div>

              {config.subjects.length > 0 && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800">
                    ✓ {config.subjects.length} subject{config.subjects.length > 1 ? 's' : ''} selected
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Configuration */}
          {currentStep === 3 && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <Settings className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-800 mb-2">Configure Your Test</h3>
                <p className="text-gray-600">Customize difficulty, questions, and timing</p>
              </div>

              {/* Difficulty Slider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Difficulty Level
                </label>
                <div className="space-y-3">
                  <input
                    type="range"
                    min="1"
                    max="5"
                    value={config.difficulty}
                    onChange={(e) => updateConfig('difficulty', parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Very Easy</span>
                    <span>Easy</span>
                    <span>Medium</span>
                    <span>Hard</span>
                    <span>Very Hard</span>
                  </div>
                  <div className={`inline-block px-4 py-2 rounded-full ${getDifficultyColor(config.difficulty)}`}>
                    <span className="font-semibold">{getDifficultyLabel(config.difficulty)}</span>
                  </div>
                </div>
              </div>

              {/* Number of Questions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Number of Questions
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="5"
                    max="50"
                    step="5"
                    value={config.numQuestions}
                    onChange={(e) => updateConfig('numQuestions', parseInt(e.target.value))}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="w-20 text-center">
                    <span className="text-2xl font-bold text-blue-600">{config.numQuestions}</span>
                  </div>
                </div>
              </div>

              {/* Timer Configuration */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Test Timer
                </label>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      id="timer-enabled"
                      checked={config.timerEnabled}
                      onChange={(e) => updateConfig('timerEnabled', e.target.checked)}
                      className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="timer-enabled" className="text-gray-700">
                      Enable timer for realistic exam practice
                    </label>
                  </div>

                  {config.timerEnabled && (
                    <div className="ml-8 flex gap-3">
                      {[15, 30, 45, 60].map((duration) => (
                        <button
                          key={duration}
                          onClick={() => updateConfig('timerDuration', duration)}
                          className={`px-4 py-2 rounded-lg border-2 transition-all ${
                            config.timerDuration === duration
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-200 hover:border-blue-300'
                          }`}
                        >
                          {duration} min
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Review & Generate */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <Brain className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-800 mb-2">Review Your Test</h3>
                <p className="text-gray-600">Everything looks good? Let's generate your test!</p>
              </div>

              <div className="space-y-4">
                {/* Summary Card */}
                <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
                  <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Exam Type</p>
                        <p className="text-lg font-bold text-gray-800">
                          {EXAM_TYPES.find(e => e.id === config.examType)?.name}
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-gray-600 mb-1">Subjects</p>
                        <div className="flex flex-wrap gap-2">
                          {config.subjects.map((subject, idx) => (
                            <Badge key={idx} className="bg-blue-500 text-white">
                              {subject}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-sm text-gray-600 mb-1">Difficulty</p>
                        <div className={`inline-block px-3 py-1 rounded-full ${getDifficultyColor(config.difficulty)}`}>
                          <span className="font-semibold text-sm">{getDifficultyLabel(config.difficulty)}</span>
                        </div>
                      </div>

                      <div>
                        <p className="text-sm text-gray-600 mb-1">Questions</p>
                        <p className="text-lg font-bold text-gray-800">{config.numQuestions}</p>
                      </div>

                      <div>
                        <p className="text-sm text-gray-600 mb-1">Timer</p>
                        <p className="text-lg font-bold text-gray-800">
                          {config.timerEnabled ? `${config.timerDuration} minutes` : 'No timer'}
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-gray-600 mb-1">Estimated Time</p>
                        <p className="text-lg font-bold text-gray-800">
                          {Math.ceil(config.numQuestions * 2)} - {Math.ceil(config.numQuestions * 3)} min
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Tips */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Zap className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                      <p className="font-semibold text-yellow-800 mb-1">Pro Tips:</p>
                      <ul className="text-sm text-yellow-700 space-y-1">
                        <li>• Find a quiet place to simulate real exam conditions</li>
                        <li>• Keep pen and paper handy for calculations</li>
                        <li>• Don't refresh the page during the test</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between mt-6">
        <Button
          variant="outline"
          onClick={handleBack}
          disabled={currentStep === 1}
          className="flex items-center gap-2"
        >
          <ChevronLeft className="w-4 h-4" />
          Back
        </Button>

        {currentStep < totalSteps ? (
          <Button
            onClick={handleNext}
            disabled={!canProceed()}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </Button>
        ) : (
          <Button
            onClick={handleGenerate}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-8"
          >
            <Play className="w-5 h-5" />
            Generate Test
          </Button>
        )}
      </div>
    </div>
  );
}
