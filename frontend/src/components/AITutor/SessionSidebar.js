/**
 * SessionSidebar Component
 * 
 * Displays list of chat sessions with search, create, and delete functionality
 * Collapsible on mobile, always visible on desktop
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageSquare, 
  Plus, 
  Trash2, 
  Search,
  ChevronLeft,
  ChevronRight,
  Clock
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';

const SessionSidebar = ({ 
  sessions = [],
  currentSession = null,
  onSessionSelect,
  onNewSession,
  onDeleteSession,
  loading = false,
  collapsed = false,
  onToggleCollapse
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  /**
   * Filter sessions based on search query
   */
  const filteredSessions = sessions.filter(session => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      session.title?.toLowerCase().includes(query) ||
      session.subject?.toLowerCase().includes(query) ||
      session.topic?.toLowerCase().includes(query)
    );
  });

  /**
   * Format session date
   */
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else if (diffInHours < 48) {
      return 'Yesterday';
    } else if (diffInHours < 168) {
      return date.toLocaleDateString('en-US', { weekday: 'short' });
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  /**
   * Handle delete with confirmation
   */
  const handleDelete = (e, sessionId) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this session?')) {
      onDeleteSession(sessionId);
    }
  };

  if (collapsed) {
    return (
      <div className="w-16 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col items-center py-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleCollapse}
          className="mb-4"
          title="Expand sidebar"
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
        
        <Button
          variant="ghost"
          size="icon"
          onClick={onNewSession}
          className="mb-2"
          title="New session"
        >
          <Plus className="h-5 w-5" />
        </Button>

        <div className="flex-1 overflow-y-auto w-full">
          {sessions.map(session => (
            <button
              key={session.session_id || session.id}
              onClick={() => onSessionSelect(session.session_id || session.id)}
              className={`w-full p-3 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                currentSession === (session.session_id || session.id)
                  ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-600'
                  : ''
              }`}
              title={session.title}
            >
              <MessageSquare className={`h-5 w-5 mx-auto ${
                currentSession === (session.session_id || session.id)
                  ? 'text-blue-600'
                  : 'text-gray-600 dark:text-gray-400'
              }`} />
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ width: 0 }}
      animate={{ width: 320 }}
      exit={{ width: 0 }}
      className="bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-full"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <MessageSquare className="h-5 w-5 mr-2" />
            Sessions
          </h2>
          
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={onNewSession}
              disabled={loading}
              title="New session"
            >
              <Plus className="h-5 w-5" />
            </Button>
            
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggleCollapse}
              title="Collapse sidebar"
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search sessions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="text-center py-8 px-4">
            <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-2" />
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {searchQuery ? 'No sessions found' : 'No sessions yet'}
            </p>
            {!searchQuery && (
              <Button
                variant="link"
                onClick={onNewSession}
                className="mt-2"
              >
                Start a conversation
              </Button>
            )}
          </div>
        ) : (
          <AnimatePresence>
            {filteredSessions.map((session) => {
              const sessionId = session.session_id || session.id;
              const isActive = currentSession === sessionId;

              return (
                <motion.div
                  key={sessionId}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  whileHover={{ backgroundColor: 'rgba(0,0,0,0.02)' }}
                  onClick={() => onSessionSelect(sessionId)}
                  className={`p-3 border-b border-gray-100 dark:border-gray-700 cursor-pointer transition-colors ${
                    isActive 
                      ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-l-blue-600' 
                      : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      {/* Session Title */}
                      <h3 className={`text-sm font-medium truncate ${
                        isActive 
                          ? 'text-blue-900 dark:text-blue-100' 
                          : 'text-gray-900 dark:text-gray-100'
                      }`}>
                        {session.title || 'Untitled Session'}
                      </h3>

                      {/* Session Meta */}
                      <div className="flex items-center space-x-2 mt-1">
                        {session.subject && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                            {session.subject}
                          </span>
                        )}
                        {session.created_at && (
                          <span className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                            <Clock className="h-3 w-3 mr-1" />
                            {formatDate(session.created_at)}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Delete Button */}
                    <button
                      onClick={(e) => handleDelete(e, sessionId)}
                      className="ml-2 p-1 text-gray-400 hover:text-red-600 transition-colors"
                      title="Delete session"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        )}
      </div>
    </motion.div>
  );
};

export default React.memo(SessionSidebar);
