/**
 * Chat History Sidebar - Shows in context panel
 * Clean list of conversations with search
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Search,
  MessageCircle,
  MoreHorizontal,
  Edit2,
  Trash2,
  Pin,
  Star,
  Clock
} from 'lucide-react';

// Single chat item
const ChatItem = ({ 
  chat, 
  isActive, 
  onClick, 
  onRename, 
  onDelete, 
  onPin 
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(chat.title);

  const handleRename = () => {
    if (editTitle.trim() && editTitle !== chat.title) {
      onRename?.(chat.id, editTitle);
    }
    setIsEditing(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`group relative px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200 ${
        isActive 
          ? 'bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800' 
          : 'hover:bg-gray-100 dark:hover:bg-gray-800'
      }`}
      onClick={() => !isEditing && onClick?.(chat)}
    >
      <div className="flex items-start gap-2.5">
        {/* Icon */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
          isActive 
            ? 'bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400' 
            : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'
        }`}>
          <MessageCircle className="w-4 h-4" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onBlur={handleRename}
              onKeyDown={(e) => e.key === 'Enter' && handleRename()}
              className="w-full px-2 py-1 text-sm bg-white dark:bg-gray-700 border border-purple-300 dark:border-purple-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              autoFocus
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            <>
              <p className={`text-sm font-medium truncate ${
                isActive ? 'text-purple-700 dark:text-purple-300' : 'text-gray-800 dark:text-gray-200'
              }`}>
                {chat.title || 'New Chat'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-0.5 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {chat.date || 'Today'}
                {chat.isPinned && <Pin className="w-3 h-3 text-purple-500 ml-1" />}
              </p>
            </>
          )}
        </div>

        {/* Menu Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(!showMenu);
          }}
          className={`flex-shrink-0 p-1 rounded-lg transition-all ${
            showMenu 
              ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300' 
              : 'opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          }`}
        >
          <MoreHorizontal className="w-4 h-4" />
        </button>
      </div>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {showMenu && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="absolute right-2 top-full mt-1 w-36 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-20"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => { setIsEditing(true); setShowMenu(false); }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <Edit2 className="w-3.5 h-3.5" />
              Rename
            </button>
            <button
              onClick={() => { onPin?.(chat.id); setShowMenu(false); }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <Pin className="w-3.5 h-3.5" />
              {chat.isPinned ? 'Unpin' : 'Pin'}
            </button>
            <button
              onClick={() => { onDelete?.(chat.id); setShowMenu(false); }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// Main Chat History Component
export default function ChatHistorySidebar({
  chats = [],
  activeSessionId,
  onChatSelect,
  onNewChat,
  onRenameChat,
  onDeleteChat,
  onPinChat,
  isLoading = false
}) {
  const [searchQuery, setSearchQuery] = useState('');

  // Filter chats by search
  const filteredChats = chats.filter(chat => 
    chat.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chat.subject?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Separate pinned and regular chats
  const pinnedChats = filteredChats.filter(c => c.isPinned);
  const regularChats = filteredChats.filter(c => !c.isPinned);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-gray-900 dark:text-white">Chats</h2>
          <button
            onClick={onNewChat}
            className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg flex items-center justify-center hover:shadow-lg hover:shadow-purple-500/30 transition-all"
            title="New Chat"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-gray-100 dark:bg-gray-800 border-0 rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
          />
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <div className="w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-sm">Loading chats...</p>
          </div>
        ) : filteredChats.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <MessageCircle className="w-10 h-10 mb-3 opacity-50" />
            <p className="text-sm font-medium">No chats yet</p>
            <p className="text-xs mt-1">Start a new conversation!</p>
          </div>
        ) : (
          <>
            {/* Pinned Chats */}
            {pinnedChats.length > 0 && (
              <div className="mb-3">
                <p className="px-3 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-1">
                  <Pin className="w-3 h-3" /> Pinned
                </p>
                {pinnedChats.map((chat) => (
                  <ChatItem
                    key={chat.id}
                    chat={chat}
                    isActive={chat.id === activeSessionId}
                    onClick={onChatSelect}
                    onRename={onRenameChat}
                    onDelete={onDeleteChat}
                    onPin={onPinChat}
                  />
                ))}
              </div>
            )}

            {/* Regular Chats */}
            {regularChats.length > 0 && (
              <div>
                {pinnedChats.length > 0 && (
                  <p className="px-3 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Recent
                  </p>
                )}
                {regularChats.map((chat) => (
                  <ChatItem
                    key={chat.id}
                    chat={chat}
                    isActive={chat.id === activeSessionId}
                    onClick={onChatSelect}
                    onRename={onRenameChat}
                    onDelete={onDeleteChat}
                    onPin={onPinChat}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Footer - Quick Tips */}
      <div className="flex-shrink-0 p-3 border-t border-gray-200 dark:border-gray-800">
        <p className="text-xs text-center text-gray-400">
          💡 Tip: Pin important chats for quick access
        </p>
      </div>
    </div>
  );
}


