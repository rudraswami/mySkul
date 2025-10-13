import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  ChevronLeft, 
  ChevronRight, 
  Flag, 
  Clock, 
  AlertCircle,
  CheckCircle,
  Circle,
  X,
  Maximize2,
  Minimize2
} from 'lucide-react';

export default function ExamMode({ 
  test, 
  questions, 
  onSubmit, 
  onExit,
  timerDuration = null // in seconds, null for no timer
}) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [markedForReview, setMarkedForReview] = useState(new Set());
  const [timeRemaining, setTimeRemaining] = useState(timerDuration);
  const [showPalette, setShowPalette] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);
  
  const timerRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  // Lock body scroll when exam mode is active
  useEffect(() => {
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    document.body.style.position = 'fixed';
    document.body.style.width = '100%';
    document.body.style.height = '100%';
    
    return () => {
      // Restore body scroll on unmount
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
      document.body.style.height = '';
    };
  }, []);

  // Timer countdown
  useEffect(() => {
    if (timerDuration && timeRemaining !== null) {
      timerRef.current = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleAutoSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
      };
    }
  }, [timerDuration]);

  const handleAutoSubmit = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    const timeTaken = Math.floor((Date.now() - startTimeRef.current) / 1000);
    onSubmit({
      answers,
      timeTaken,
      markedForReview: Array.from(markedForReview)
    });
  };

  const handleSubmitConfirm = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    const timeTaken = Math.floor((Date.now() - startTimeRef.current) / 1000);
    onSubmit({
      answers,
      timeTaken,
      markedForReview: Array.from(markedForReview)
    });
  };

  const selectAnswer = (questionId, option) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: option
    }));
  };

  const toggleMarkForReview = (questionId) => {
    setMarkedForReview(prev => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });
  };

  const goToQuestion = (index) => {
    setCurrentQuestion(index);
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const previousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const formatTime = (seconds) => {
    if (seconds === null) return 'No Timer';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimerColor = () => {
    if (!timeRemaining) return 'text-gray-600';
    const percentage = (timeRemaining / timerDuration) * 100;
    if (percentage <= 10) return 'text-red-600';
    if (percentage <= 25) return 'text-orange-600';
    return 'text-green-600';
  };

  const getQuestionStatus = (index) => {
    const questionId = questions[index]?.question_id;
    if (answers[questionId]) return 'answered';
    if (markedForReview.has(questionId)) return 'marked';
    return 'unanswered';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'answered':
        return 'bg-green-500 text-white border-green-500';
      case 'marked':
        return 'bg-orange-500 text-white border-orange-500';
      default:
        return 'bg-white text-gray-700 border-gray-300';
    }
  };

  const currentQ = questions[currentQuestion];
  const currentQuestionId = currentQ?.question_id;
  const currentAnswer = answers[currentQuestionId];
  const isMarked = markedForReview.has(currentQuestionId);

  // Stats for palette
  const answeredCount = Object.keys(answers).length;
  const markedCount = markedForReview.size;
  const unansweredCount = questions.length - answeredCount;

  if (!currentQ) {
    return <div className="p-8 text-center">Loading question...</div>;
  }

  // Render exam mode using React Portal for true full-screen isolation
  const examContent = (
    <div className="fixed inset-0 z-[9999] bg-gray-50 overflow-y-auto" style={{ margin: 0, padding: 0 }}>
      {/* Top Bar */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Left: Test Info */}
            <div className="flex items-center gap-4">
              <h2 className="font-semibold text-gray-800">{test.title || 'Mock Test'}</h2>
              <Badge variant="outline" className="text-xs">
                Question {currentQuestion + 1} / {questions.length}
              </Badge>
            </div>

            {/* Center: Timer */}
            {timerDuration && (
              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-50 ${getTimerColor()}`}>
                <Clock className="w-5 h-5" />
                <span className="font-mono font-bold text-lg">
                  {formatTime(timeRemaining)}
                </span>
              </div>
            )}

            {/* Right: Actions */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowPalette(!showPalette)}
                className="hidden md:flex"
              >
                {showPalette ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSubmitConfirm(true)}
                className="text-green-600 border-green-300 hover:bg-green-50"
              >
                Submit Test
              </Button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-3">
            <Progress value={(answeredCount / questions.length) * 100} className="h-1" />
          </div>
        </div>
      </div>

      <div className="flex flex-col md:flex-row max-w-7xl mx-auto">
        {/* Main Question Area */}
        <div className="flex-1 p-4 md:p-6">
          <Card className="shadow-lg border-0">
            <CardContent className="p-8">
              {/* Question Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <Badge className="bg-blue-500 text-white">
                      Question {currentQuestion + 1}
                    </Badge>
                    {currentQ.subject && (
                      <Badge variant="outline">{currentQ.subject}</Badge>
                    )}
                    {currentQ.difficulty_level && (
                      <Badge variant="secondary">
                        Level {currentQ.difficulty_level}
                      </Badge>
                    )}
                  </div>
                </div>
                <Button
                  variant={isMarked ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => toggleMarkForReview(currentQuestionId)}
                  className={isMarked ? 'bg-orange-500 hover:bg-orange-600' : ''}
                >
                  <Flag className="w-4 h-4 mr-2" />
                  {isMarked ? 'Marked' : 'Mark'}
                </Button>
              </div>

              {/* Question Text */}
              <div className="mb-8">
                <p className="text-lg text-gray-800 leading-relaxed">
                  {currentQ.question_text}
                </p>
              </div>

              {/* Options */}
              <div className="space-y-3">
                {currentQ.options?.map((option, idx) => {
                  const optionLabel = String.fromCharCode(65 + idx); // A, B, C, D
                  const isSelected = currentAnswer === option;

                  return (
                    <button
                      key={idx}
                      onClick={() => selectAnswer(currentQuestionId, option)}
                      className={`w-full p-4 rounded-lg border-2 text-left transition-all hover:shadow-md ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300'
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold ${
                          isSelected
                            ? 'bg-blue-500 border-blue-500 text-white'
                            : 'border-gray-300 text-gray-600'
                        }`}>
                          {optionLabel}
                        </div>
                        <span className="text-gray-800">{option}</span>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Navigation Buttons */}
              <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
                <Button
                  variant="outline"
                  onClick={previousQuestion}
                  disabled={currentQuestion === 0}
                  className="flex items-center gap-2"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </Button>

                <div className="text-sm text-gray-600">
                  {currentAnswer ? (
                    <span className="text-green-600 font-medium">✓ Answered</span>
                  ) : (
                    <span className="text-gray-500">Not answered</span>
                  )}
                </div>

                {currentQuestion === questions.length - 1 ? (
                  <Button
                    onClick={() => setShowSubmitConfirm(true)}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
                  >
                    Submit Test
                    <CheckCircle className="w-4 h-4" />
                  </Button>
                ) : (
                  <Button
                    onClick={nextQuestion}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
                  >
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Question Palette Sidebar - Mobile and Desktop */}
        {showPalette && (
          <div className="w-full md:w-80 p-4 md:p-6 bg-white md:border-l border-gray-200 md:border-t-0 border-t">
            <div className="sticky top-24">
              <h3 className="font-bold text-gray-800 mb-4">Question Palette</h3>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-2 mb-6">
                <div className="text-center p-2 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{answeredCount}</p>
                  <p className="text-xs text-gray-600">Answered</p>
                </div>
                <div className="text-center p-2 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-600">{unansweredCount}</p>
                  <p className="text-xs text-gray-600">Not Answered</p>
                </div>
                <div className="text-center p-2 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">{markedCount}</p>
                  <p className="text-xs text-gray-600">Marked</p>
                </div>
              </div>

              {/* Question Grid - Responsive */}
              <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-2">
                {questions.map((_, idx) => {
                  const status = getQuestionStatus(idx);
                  return (
                    <button
                      key={idx}
                      onClick={() => goToQuestion(idx)}
                      className={`aspect-square rounded-lg border-2 font-semibold text-sm transition-all hover:scale-105 ${
                        getStatusColor(status)
                      } ${
                        idx === currentQuestion
                          ? 'ring-2 ring-blue-400 ring-offset-2'
                          : ''
                      }`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>

              {/* Legend */}
              <div className="mt-6 space-y-2 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-green-500"></div>
                  <span className="text-gray-600">Answered</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-white border-2 border-gray-300"></div>
                  <span className="text-gray-600">Not Answered</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-orange-500"></div>
                  <span className="text-gray-600">Marked for Review</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Submit Confirmation Modal */}
      {showSubmitConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full">
            <CardContent className="p-6">
              <div className="flex items-start gap-4 mb-6">
                <AlertCircle className="w-12 h-12 text-orange-500 flex-shrink-0" />
                <div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">Submit Test?</h3>
                  <p className="text-gray-600 text-sm mb-4">
                    Are you sure you want to submit? You won't be able to change your answers after submission.
                  </p>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Answered:</span>
                      <span className="font-semibold text-green-600">{answeredCount} / {questions.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Not Answered:</span>
                      <span className="font-semibold text-gray-600">{unansweredCount}</span>
                    </div>
                    {markedCount > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Marked for Review:</span>
                        <span className="font-semibold text-orange-600">{markedCount}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setShowSubmitConfirm(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSubmitConfirm}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  Submit Test
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );

  // Use React Portal to render at document body level for true full-screen isolation
  return ReactDOM.createPortal(examContent, document.body);
}
