/**
 * History Sidebar - Glassmorphic Learning Path Drawer
 * ====================================================
 * 
 * A slide-out drawer for navigating past chat topics.
 * Premium glassmorphic design with "Druv Vibe" aesthetics.
 * 
 * Features:
 * - Glassmorphic design with backdrop blur
 * - Grouped by date (Today, Yesterday, This Week)
 * - Subject-based icons with emoji
 * - Active state highlighting (purple accent)
 * - Search functionality
 * - Smooth animations
 */

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Search,
  MessageCircle,
  MoreHorizontal,
  Edit2,
  Trash2,
  Pin,
  Clock,
  BookOpen,
  Plus,
  Sparkles,
  History,
  ChevronDown,
  ChevronUp,
  Atom, // Physics
  FlaskConical, // Chemistry  
  Dna, // Biology
  Calculator, // Math
  GraduationCap // General
} from 'lucide-react';

// Subject icon mapping
const getSubjectIcon = (subject) => {
  const subjectLower = (subject || '').toLowerCase();
  if (subjectLower.includes('physics')) return <Atom className="w-4 h-4" />;
  if (subjectLower.includes('chem')) return <FlaskConical className="w-4 h-4" />;
  if (subjectLower.includes('bio')) return <Dna className="w-4 h-4" />;
  if (subjectLower.includes('math')) return <Calculator className="w-4 h-4" />;
  return <GraduationCap className="w-4 h-4" />;
};

// Subject emoji mapping
const getSubjectEmoji = (subject) => {
  const subjectLower = (subject || '').toLowerCase();
  if (subjectLower.includes('physics')) return '⚛️';
  if (subjectLower.includes('chem')) return '🧪';
  if (subjectLower.includes('bio')) return '🧬';
  if (subjectLower.includes('math')) return '📐';
  return '📚';
};

// Subject color mapping
const getSubjectColor = (subject) => {
  const subjectLower = (subject || '').toLowerCase();
  if (subjectLower.includes('physics')) return { bg: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-200' };
  if (subjectLower.includes('chem')) return { bg: 'bg-orange-100', text: 'text-orange-600', border: 'border-orange-200' };
  if (subjectLower.includes('bio')) return { bg: 'bg-green-100', text: 'text-green-600', border: 'border-green-200' };
  if (subjectLower.includes('math')) return { bg: 'bg-purple-100', text: 'text-purple-600', border: 'border-purple-200' };
  return { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-200' };
};

// Group chats by date
const groupChatsByDate = (chats) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  const thisWeekStart = new Date(today);
  thisWeekStart.setDate(thisWeekStart.getDate() - 7);

  const groups = {
    today: [],
    yesterday: [],
    thisWeek: [],
    older: []
  };

  chats.forEach(chat => {
    const chatDate = new Date(chat.updatedAt || chat.createdAt || Date.now());
    chatDate.setHours(0, 0, 0, 0);

    if (chatDate.getTime() === today.getTime()) {
      groups.today.push(chat);
    } else if (chatDate.getTime() === yesterday.getTime()) {
      groups.yesterday.push(chat);
    } else if (chatDate >= thisWeekStart) {
      groups.thisWeek.push(chat);
    } else {
      groups.older.push(chat);
    }
  });

  return groups;
};

// Single Chat Item - Premium Design
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
  const subjectColors = getSubjectColor(chat.subject);

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
      whileHover={{ x: 4 }}
      transition={{ duration: 0.2 }}
      className={`group relative mx-2 mb-1 rounded-xl cursor-pointer transition-all duration-200 ${
        isActive 
          ? 'bg-gradient-to-r from-purple-50 to-purple-100/50 border-l-4 border-purple-500 shadow-sm' 
          : 'hover:bg-gray-50/80 border-l-4 border-transparent hover:border-purple-200'
      }`}
      onClick={() => !isEditing && onClick?.(chat)}
    >
      <div className="flex items-start gap-3 px-3 py-3">
        {/* Subject Emoji Icon */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-sm ${
          isActive 
            ? 'bg-purple-500 text-white shadow-purple-200' 
            : `${subjectColors.bg} ${subjectColors.text}`
        }`}>
          <span className="text-lg">{getSubjectEmoji(chat.subject)}</span>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0 py-0.5">
          {isEditing ? (
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onBlur={handleRename}
              onKeyDown={(e) => e.key === 'Enter' && handleRename()}
              className="w-full px-2 py-1 text-sm bg-white border border-purple-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              autoFocus
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            <>
              <div className="flex items-center gap-2 mb-1">
                <p 
                  className={`text-sm font-semibold truncate ${
                    isActive ? 'text-purple-800' : 'text-gray-800'
                  }`}
                  title={chat.title || 'New Chat'}
                >
                  {chat.title || 'New Chat'}
                </p>
                {chat.isPinned && (
                  <Pin className="w-3 h-3 text-amber-500 flex-shrink-0" />
                )}
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <span className={`px-1.5 py-0.5 rounded-md ${subjectColors.bg} ${subjectColors.text} font-medium`}>
                  {chat.subject || 'General'}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {chat.date || formatTime(chat.updatedAt || chat.createdAt)}
                </span>
              </div>
            </>
          )}
        </div>

        {/* Menu Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(!showMenu);
          }}
          className={`flex-shrink-0 p-1.5 rounded-lg transition-all ${
            showMenu 
              ? 'bg-gray-200 text-gray-700' 
              : 'opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600 hover:bg-gray-200'
          }`}
        >
          <MoreHorizontal className="w-4 h-4" />
        </button>
      </div>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {showMenu && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -5 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -5 }}
            transition={{ duration: 0.15 }}
            className="absolute right-3 top-full mt-1 w-40 bg-white rounded-xl shadow-xl border border-gray-200/80 py-1.5 z-30 overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => { setIsEditing(true); setShowMenu(false); }}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Edit2 className="w-3.5 h-3.5 text-gray-400" />
              Rename
            </button>
            <button
              onClick={() => { onPin?.(chat.id); setShowMenu(false); }}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Pin className="w-3.5 h-3.5 text-gray-400" />
              {chat.isPinned ? 'Unpin' : 'Pin to Top'}
            </button>
            <div className="my-1 h-px bg-gray-100" />
            <button
              onClick={() => { onDelete?.(chat.id); setShowMenu(false); }}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
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

// Format time helper
const formatTime = (dateString) => {
  if (!dateString) return 'Just now';
  try {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  } catch {
    return 'Just now';
  }
};

// Collapsible Section Component
const CollapsibleSection = ({ title, icon, count, children, defaultOpen = true }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  if (count === 0) return null;
  
  return (
    <div className="mb-3">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-2 text-xs font-bold text-gray-400 uppercase tracking-wider hover:text-gray-600 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <span>{title}</span>
          <span className="px-1.5 py-0.5 bg-gray-100 rounded-full text-[10px] font-semibold text-gray-500">
            {count}
          </span>
        </div>
        {isOpen ? (
          <ChevronUp className="w-3.5 h-3.5" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5" />
        )}
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Main History Sidebar Component
export default function HistorySidebar({
  isOpen,
  onClose,
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
  const filteredChats = useMemo(() => {
    return chats.filter(chat => 
      chat.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      chat.subject?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [chats, searchQuery]);

  // Group filtered chats by date
  const groupedChats = useMemo(() => {
    const pinned = filteredChats.filter(c => c.isPinned);
    const unpinned = filteredChats.filter(c => !c.isPinned);
    return {
      pinned,
      ...groupChatsByDate(unpinned)
    };
  }, [filteredChats]);

  const renderChatList = (chatList) => {
    return chatList.map((chat) => (
      <ChatItem
        key={chat.id}
        chat={chat}
        isActive={chat.id === activeSessionId}
        onClick={onChatSelect}
        onRename={onRenameChat}
        onDelete={onDeleteChat}
        onPin={onPinChat}
      />
    ));
  };

  return (
    <>
      {/* Backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      {/* Sidebar Drawer - Premium Glassmorphic Design */}
      <motion.div
        initial={false}
        animate={{ x: isOpen ? 0 : '-100%' }}
        transition={{ type: 'spring', stiffness: 400, damping: 40 }}
        className="fixed inset-y-0 left-0 z-50 w-80 bg-white/95 backdrop-blur-xl shadow-2xl"
        style={{
          boxShadow: isOpen ? '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 50px rgba(139, 92, 246, 0.1)' : 'none'
        }}
      >
        <div className="h-full flex flex-col">
          {/* Header - Premium Design */}
          <div className="flex-shrink-0 px-5 py-5 border-b border-gray-200/50 bg-gradient-to-r from-purple-50/50 to-orange-50/30">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 
                    className="text-lg font-bold text-gray-900"
                    style={{ fontFamily: "'Inter', 'Segoe UI', sans-serif" }}
                  >
                    My Learning Path
                  </h2>
                  <p className="text-xs text-gray-400 font-medium">
                    {chats.length} conversation{chats.length !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.05, rotate: 90 }}
                whileTap={{ scale: 0.95 }}
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
              >
                <X className="w-5 h-5" />
              </motion.button>
            </div>

            {/* New Chat Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => { onNewChat?.(); onClose?.(); }}
              className="w-full flex items-center justify-center gap-2.5 px-4 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white rounded-xl font-semibold transition-all duration-200 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40"
            >
              <Plus className="w-5 h-5" />
              New Conversation
            </motion.button>

            {/* Search */}
            <div className="relative mt-4">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search your learning path..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/30 focus:border-purple-300 transition-all shadow-sm"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Chat List */}
          <div className="flex-1 overflow-y-auto py-3 scrollbar-thin scrollbar-thumb-gray-200 scrollbar-track-transparent">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-16 text-gray-400">
                <div className="w-10 h-10 border-3 border-purple-500 border-t-transparent rounded-full animate-spin mb-4" />
                <p className="text-sm font-medium">Loading your journey...</p>
              </div>
            ) : filteredChats.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-gray-400 px-6">
                <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-50 rounded-2xl flex items-center justify-center mb-4 shadow-inner">
                  <MessageCircle className="w-10 h-10 text-gray-300" />
                </div>
                <p className="text-base font-semibold text-gray-500 mb-1">No conversations yet</p>
                <p className="text-sm text-gray-400 text-center">
                  Start your learning journey by asking a question!
                </p>
              </div>
            ) : (
              <>
                {/* Pinned Section */}
                {groupedChats.pinned.length > 0 && (
                  <CollapsibleSection 
                    title="Pinned" 
                    icon={<Pin className="w-3 h-3 text-amber-500" />}
                    count={groupedChats.pinned.length}
                    defaultOpen={true}
                  >
                    {renderChatList(groupedChats.pinned)}
                  </CollapsibleSection>
                )}

                {/* Today */}
                <CollapsibleSection 
                  title="Today" 
                  icon={<Sparkles className="w-3 h-3" />}
                  count={groupedChats.today.length}
                  defaultOpen={true}
                >
                  {renderChatList(groupedChats.today)}
                </CollapsibleSection>

                {/* Yesterday */}
                <CollapsibleSection 
                  title="Yesterday" 
                  icon={<Clock className="w-3 h-3" />}
                  count={groupedChats.yesterday.length}
                  defaultOpen={true}
                >
                  {renderChatList(groupedChats.yesterday)}
                </CollapsibleSection>

                {/* This Week */}
                <CollapsibleSection 
                  title="This Week" 
                  icon={<History className="w-3 h-3" />}
                  count={groupedChats.thisWeek.length}
                  defaultOpen={false}
                >
                  {renderChatList(groupedChats.thisWeek)}
                </CollapsibleSection>

                {/* Older */}
                <CollapsibleSection 
                  title="Earlier" 
                  icon={<BookOpen className="w-3 h-3" />}
                  count={groupedChats.older.length}
                  defaultOpen={false}
                >
                  {renderChatList(groupedChats.older)}
                </CollapsibleSection>
              </>
            )}
          </div>

          {/* Footer */}
          <div className="flex-shrink-0 px-5 py-4 border-t border-gray-200/50 bg-gradient-to-t from-gray-50/50 to-transparent">
            <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
              <Sparkles className="w-3.5 h-3.5 text-purple-400" />
              <span>Your learning journey is saved automatically</span>
            </div>
          </div>
        </div>
      </motion.div>
    </>
  );
}
