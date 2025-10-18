import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageCircle, FileText, BookOpen } from 'lucide-react';

/**
 * Bottom Fixed Quick Actions Toolbar
 * Provides persistent access to key features
 */
const QuickActionsToolbar = () => {
  const navigate = useNavigate();

  const quickActions = [
    {
      id: 'ai-tutor',
      icon: MessageCircle,
      label: 'AI Tutor',
      color: 'from-blue-500 to-purple-500',
      action: () => navigate('/tutor')
    },
    {
      id: 'mock-test',
      icon: FileText,
      label: 'Mock Test',
      color: 'from-green-500 to-emerald-500',
      action: () => navigate('/tests')
    },
    {
      id: 'notes',
      icon: BookOpen,
      label: 'Auto Notes',
      color: 'from-orange-500 to-pink-500',
      action: () => navigate('/auto-notes')
    }
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 shadow-lg md:hidden">
      <div className="flex items-center justify-around p-2">
        {quickActions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.id}
              onClick={action.action}
              className={`flex flex-col items-center space-y-1 px-4 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex-1`}
            >
              <div className={`p-2 bg-gradient-to-br ${action.color} rounded-lg`}>
                <Icon className="h-5 w-5 text-white" />
              </div>
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{action.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default QuickActionsToolbar;
