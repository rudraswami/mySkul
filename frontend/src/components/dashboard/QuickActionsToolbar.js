import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageCircle, FileText, BookOpen } from 'lucide-react';

/**
 * Bottom Fixed Quick Actions Toolbar
 * Provides persistent access to key features
 */
const QuickActionsToolbar = () => {
  const navigate = useNavigate();

  // V1: Only AI Tutor available, Mock Tests and Auto Notes hidden for V2
  const quickActions = [
    {
      id: 'ai-tutor',
      icon: MessageCircle,
      label: 'AI Tutor',
      color: 'from-blue-500 to-purple-500',
      action: () => navigate('/tutor')
    }
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 shadow-lg md:hidden">
      <div className="flex items-center justify-center p-3">
        {quickActions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.id}
              onClick={action.action}
              className={`flex items-center space-x-3 px-6 py-3 bg-gradient-to-r ${action.color} text-white rounded-xl shadow-lg hover:shadow-xl transition-all hover:scale-105`}
            >
              <Icon className="h-5 w-5" />
              <span className="text-sm font-semibold">{action.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default QuickActionsToolbar;
