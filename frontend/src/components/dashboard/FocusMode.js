import React, { useState, useEffect } from 'react';
import { X, Clock, Target, TrendingUp, CheckCircle } from 'lucide-react';

/**
 * Focus Mode Component
 * Minimal distraction-free view for studying
 */
const FocusMode = ({ isActive, onClose, focusPlan }) => {
  const [timer, setTimer] = useState(25 * 60); // 25 minutes default
  const [isRunning, setIsRunning] = useState(false);
  const [completedTasks, setCompletedTasks] = useState([]);

  useEffect(() => {
    let interval;
    if (isRunning && timer > 0) {
      interval = setInterval(() => {
        setTimer(prev => prev - 1);
      }, 1000);
    } else if (timer === 0) {
      // Timer complete
      setIsRunning(false);
      // Show completion notification
    }
    return () => clearInterval(interval);
  }, [isRunning, timer]);

  if (!isActive) return null;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);
  };

  const resetTimer = () => {
    setTimer(25 * 60);
    setIsRunning(false);
  };

  const markTaskComplete = (taskId) => {
    if (!completedTasks.includes(taskId)) {
      setCompletedTasks([...completedTasks, taskId]);
    }
  };

  const tasks = focusPlan?.tasks || [
    { id: 1, title: 'Review Quadratic Equations', duration: '25 min', priority: 'high' },
    { id: 2, title: 'Practice Integration Problems', duration: '30 min', priority: 'medium' },
    { id: 3, title: 'Read Chemistry Chapter 4', duration: '20 min', priority: 'low' }
  ];

  return (
    <div className="focus-mode-overlay animate-scale-in">
      <div className="focus-mode-content">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl">
              <Target className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Focus Mode</h2>
              <p className="text-sm text-gray-500">Distraction-free study session</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-6 w-6 text-gray-600" />
          </button>
        </div>

        {/* Pomodoro Timer */}
        <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-8 mb-8 text-center">
          <div className="inline-flex items-center justify-center w-48 h-48 rounded-full bg-white shadow-premium mb-4">
            <div className="text-center">
              <div className="text-5xl font-bold text-gray-900 mb-2">
                {formatTime(timer)}
              </div>
              <div className="text-sm text-gray-500">
                {isRunning ? 'Studying...' : 'Ready to focus'}
              </div>
            </div>
          </div>
          
          <div className="flex items-center justify-center space-x-4">
            <button
              onClick={toggleTimer}
              className="px-8 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
            >
              {isRunning ? 'Pause' : 'Start'}
            </button>
            <button
              onClick={resetTimer}
              className="px-8 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Today's Focus Tasks */}
        <div className="mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-purple-600" />
            Today's Focus
          </h3>
          <div className="space-y-3">
            {tasks.map((task) => {
              const isCompleted = completedTasks.includes(task.id);
              return (
                <div
                  key={task.id}
                  className={`flex items-center justify-between p-4 rounded-xl border-2 transition-all ${
                    isCompleted
                      ? 'bg-green-50 border-green-200'
                      : 'bg-white border-gray-200 hover:border-purple-300'
                  }`}
                >
                  <div className="flex items-center space-x-3 flex-1">
                    <button
                      onClick={() => markTaskComplete(task.id)}
                      className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                        isCompleted
                          ? 'bg-green-500 border-green-500'
                          : 'border-gray-300 hover:border-purple-500'
                      }`}
                    >
                      {isCompleted && <CheckCircle className="h-4 w-4 text-white" />}
                    </button>
                    <div className="flex-1">
                      <h4 className={`font-medium ${isCompleted ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
                        {task.title}
                      </h4>
                      <p className="text-sm text-gray-500 flex items-center mt-1">
                        <Clock className="h-3 w-3 mr-1" />
                        {task.duration}
                      </p>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    task.priority === 'high' ? 'bg-red-100 text-red-700' :
                    task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {task.priority}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Progress Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{completedTasks.length}</div>
            <div className="text-xs text-gray-600 mt-1">Tasks Done</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{Math.floor((25*60 - timer) / 60)}</div>
            <div className="text-xs text-gray-600 mt-1">Minutes Studied</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{Math.round((completedTasks.length / tasks.length) * 100)}%</div>
            <div className="text-xs text-gray-600 mt-1">Completion</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FocusMode;
