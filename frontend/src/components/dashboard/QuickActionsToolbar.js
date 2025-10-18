import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageCircle, FileText, BookOpen, Zap } from 'lucide-react';

/**
 * Floating Quick Actions Toolbar
 * Provides one-tap access to key features
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
      label: 'Notes',
      color: 'from-orange-500 to-pink-500',
      action: () => navigate('/auto-notes')
    }
  ];

  return (
    <div className="quick-actions-toolbar">
      {quickActions.map((action) => {
        const Icon = action.icon;
        return (
          <div
            key={action.id}
            onClick={action.action}
            className={`quick-action-button bg-gradient-to-br ${action.color} hover:shadow-lg group relative`}
            title={action.label}
          >
            <Icon className="h-6 w-6 text-white" />
            
            {/* Tooltip */}
            <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
              <div className="bg-gray-900 text-white text-xs rounded-lg py-1 px-2 whitespace-nowrap">
                {action.label}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default QuickActionsToolbar;
