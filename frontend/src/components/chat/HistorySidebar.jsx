/**
 * History Sidebar - Premium Learning Library
 * ==========================================
 * Modern, vibrant design with color-coded topics and intelligent displays
 * 
 * FIXES APPLIED:
 * - Solid gradient New Chat button (not text-only)
 * - Borderless search input with proper resets
 * - Emoji icons with fallbacks
 * - Better active states with elevation
 * - All sections open by default
 */

import React, { useState, useMemo, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import {
  X,
  Search,
  MessageCircle,
  MoreHorizontal,
  Edit2,
  Trash2,
  Pin,
  Clock,
  Plus,
  Sparkles,
  History,
  ChevronDown,
  ChevronUp,
  BookOpen,
  LayoutDashboard,
  User,
  Crown,
  LogOut,
  Moon,
  Sun
} from 'lucide-react';

// ============================================
// COLOR-CODED TOPIC STYLING
// ============================================
const getTopicStyle = (title, subject) => {
  const text = (title || subject || '').toLowerCase();
  
  // Physics - Blue
  if (text.includes('physics') || text.includes('motion') || text.includes('force') || 
      text.includes('velocity') || text.includes('newton') || text.includes('energy') ||
      text.includes('momentum') || text.includes('gravity') || text.includes('wave')) {
    return { 
      emoji: '⚛️',
      bg: '#DBEAFE',      // blue-100
      color: '#2563EB',   // blue-600
      label: 'Physics'
    };
  }
  
  // Biology - Green
  if (text.includes('bio') || text.includes('cell') || text.includes('dna') || 
      text.includes('plant') || text.includes('animal') || text.includes('photosynthesis') ||
      text.includes('organ') || text.includes('evolution') || text.includes('genetic')) {
    return { 
      emoji: '🧬',
      bg: '#D1FAE5',      // green-100
      color: '#059669',   // green-600
      label: 'Biology'
    };
  }
  
  // Math - Red/Rose
  if (text.includes('math') || text.includes('calcul') || text.includes('algebra') || 
      text.includes('equation') || text.includes('quadratic') || text.includes('theorem') ||
      text.includes('fundamental') || text.includes('solve') || text.includes('integral') ||
      text.includes('derivative') || text.includes('trigonometr') || text.includes('geometry')) {
    return { 
      emoji: '📐',
      bg: '#FEE2E2',      // red-100
      color: '#DC2626',   // red-600
      label: 'Math'
    };
  }
  
  // Chemistry - Orange
  if (text.includes('chem') || text.includes('reaction') || text.includes('molecule') || 
      text.includes('bonding') || text.includes('element') || text.includes('compound') ||
      text.includes('acid') || text.includes('periodic') || text.includes('atom')) {
    return { 
      emoji: '🧪',
      bg: '#FFEDD5',      // orange-100
      color: '#EA580C',   // orange-600
      label: 'Chemistry'
    };
  }
  
  // Default - Purple/Gray
  return { 
    emoji: '📚',
    bg: '#F3E8FF',        // purple-100
    color: '#7C3AED',     // purple-600
    label: 'General'
  };
};

// Smart title formatter - Fixes the "Hi" problem
const formatTitle = (title) => {
  if (!title) return { text: 'New Session', isPlaceholder: true };
  const cleaned = title.trim().toLowerCase();
  
  // Generic greetings and short messages show "New Session"
  const genericTitles = ['hi', 'hello', 'hey', 'hii', 'hiii', 'yo', 'good', 'ok', 'okay', 'test', 'yes', 'no', 'sure', 'thanks', 'new chat', 'untitled'];
  if (genericTitles.includes(cleaned) || cleaned.length < 3) {
    return { text: 'New Session', isPlaceholder: true };
  }
  
  // Capitalize first letter and truncate
  const formatted = title.charAt(0).toUpperCase() + title.slice(1);
  return { 
    text: formatted.length > 28 ? formatted.substring(0, 28) + '...' : formatted, 
    isPlaceholder: false 
  };
};

// Format time for display
const formatTime = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return date.toLocaleDateString('en-US', { weekday: 'short' });
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
};

// Group chats by date
const groupChatsByDate = (chats) => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today); yesterday.setDate(yesterday.getDate() - 1);
  const weekAgo = new Date(today); weekAgo.setDate(weekAgo.getDate() - 7);

  const groups = { today: [], yesterday: [], thisWeek: [], older: [] };
  chats.forEach(chat => {
    const d = new Date(chat.updatedAt || chat.createdAt || Date.now());
    d.setHours(0, 0, 0, 0);
    if (d.getTime() === today.getTime()) groups.today.push(chat);
    else if (d.getTime() === yesterday.getTime()) groups.yesterday.push(chat);
    else if (d >= weekAgo) groups.thisWeek.push(chat);
    else groups.older.push(chat);
  });
  return groups;
};

// ============================================
// CHAT ITEM COMPONENT
// ============================================
const ChatItem = ({ chat, isActive, onClick, onRename, onDelete, onPin }) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(chat.title);
  
  const topicStyle = getTopicStyle(chat.title, chat.subject);
  const { text: displayTitle, isPlaceholder } = formatTitle(chat.title);

  const handleSaveEdit = () => {
    if (editTitle.trim() && editTitle !== chat.title) {
      onRename?.(chat.id, editTitle);
    }
    setIsEditing(false);
  };

  // Inline styles for reliability
  const iconBoxStyle = {
    width: '42px',
    height: '42px',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: topicStyle.bg,
    flexShrink: 0,
    fontSize: '18px',
    transition: 'transform 0.2s ease'
  };

  const itemStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '10px 12px',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    backgroundColor: isActive ? 'rgba(139, 92, 246, 0.15)' : 'transparent',
    borderLeft: isActive ? '4px solid #8b5cf6' : '4px solid transparent',
    boxShadow: isActive ? '0 2px 8px rgba(139, 92, 246, 0.25)' : 'none',
    marginLeft: '8px',
    marginRight: '8px',
    marginBottom: '4px'
  };

  return (
    <div style={{ position: 'relative' }}>
      <div
        onClick={() => !isEditing && onClick?.(chat)}
        style={itemStyle}
        className="group hover:bg-slate-800/50"
        onMouseEnter={(e) => {
          if (!isActive) e.currentTarget.style.backgroundColor = 'rgba(28, 28, 42, 0.5)';
        }}
        onMouseLeave={(e) => {
          if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
        }}
      >
        {/* Color-coded Icon Box */}
        <div style={iconBoxStyle}>
          <span role="img" aria-label={topicStyle.label}>
            {topicStyle.emoji}
          </span>
        </div>

        {/* Content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {isEditing ? (
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onBlur={handleSaveEdit}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSaveEdit();
                if (e.key === 'Escape') setIsEditing(false);
              }}
              style={{
                width: '100%',
                padding: '6px 10px',
                fontSize: '14px',
                border: '2px solid #7C3AED',
                borderRadius: '8px',
                outline: 'none',
                backgroundColor: '#1c1c2a',
                color: '#f1f5f9'
              }}
              autoFocus
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            <>
              <p style={{
                fontSize: '14px',
                lineHeight: '1.3',
                margin: 0,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                fontWeight: isActive ? '600' : isPlaceholder ? '400' : '500',
                fontStyle: isPlaceholder ? 'italic' : 'normal',
                color: isActive ? '#e879a9' : isPlaceholder ? '#6b6b80' : '#f1f5f9'
              }}>
                {displayTitle}
                {chat.isPinned && (
                  <Pin 
                    style={{ 
                      display: 'inline', 
                      width: '12px', 
                      height: '12px', 
                      marginLeft: '6px',
                      color: '#F59E0B',
                      fill: '#F59E0B'
                    }} 
                  />
                )}
              </p>
              <p style={{
                fontSize: '12px',
                color: '#6b6b80',
                margin: '2px 0 0 0'
              }}>
                {formatTime(chat.date || chat.updatedAt || chat.createdAt)}
              </p>
            </>
          )}
        </div>

        {/* Menu Button - Touch-friendly */}
        {!isEditing && (
          <button
            onClick={(e) => { 
              e.stopPropagation(); 
              setShowMenu(!showMenu); 
            }}
            style={{
              padding: '8px',
              borderRadius: '8px',
              border: 'none',
              background: showMenu ? 'rgba(28, 28, 42, 0.85)' : 'transparent',
              cursor: 'pointer',
              opacity: showMenu ? 1 : 0.7,
              transition: 'opacity 0.15s, background 0.15s',
              minWidth: '40px',
              minHeight: '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            className="group-hover:!opacity-100 hover:!bg-slate-800/50"
            aria-label="Chat options"
          >
            <MoreHorizontal style={{ width: '18px', height: '18px', color: '#a1a1b5' }} />
          </button>
        )}
      </div>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {showMenu && (
          <>
            <div 
              style={{ position: 'fixed', inset: 0, zIndex: 1160 }}
              onClick={() => setShowMenu(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -5 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -5 }}
              transition={{ duration: 0.15 }}
              style={{
                position: 'absolute',
                right: '12px',
                top: '100%',
                marginTop: '4px',
                /* FIXED: Higher z-index to ensure dropdown appears above all sidebar content */
                zIndex: 1170,
                width: '140px',
                backgroundColor: '#1c1c2a',
                borderRadius: '12px',
                boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: '4px 0',
                overflow: 'hidden',
                /* FIXED: Prevent dropdown from being cut off at bottom of viewport */
                maxHeight: 'calc(100vh - 100px)'
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <button 
                onClick={() => { setIsEditing(true); setShowMenu(false); }} 
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px 14px',
                  fontSize: '14px',
                  color: '#f1f5f9',
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  textAlign: 'left',
                  minHeight: '44px'
                }}
                className="hover:bg-slate-800/50"
              >
                <Edit2 style={{ width: '16px', height: '16px', color: '#a1a1b5' }} /> 
                Rename
              </button>
              <button 
                onClick={() => { onPin?.(chat.id); setShowMenu(false); }} 
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px 14px',
                  fontSize: '14px',
                  color: '#f1f5f9',
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  textAlign: 'left',
                  minHeight: '44px'
                }}
                className="hover:bg-slate-800/50"
              >
                <Pin style={{ width: '16px', height: '16px', color: '#a1a1b5' }} /> 
                {chat.isPinned ? 'Unpin' : 'Pin'}
              </button>
              <div style={{ height: '1px', backgroundColor: 'rgba(255, 255, 255, 0.08)', margin: '4px 0' }} />
              <button 
                onClick={() => { onDelete?.(chat.id); setShowMenu(false); }} 
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px 14px',
                  fontSize: '14px',
                  color: '#DC2626',
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  textAlign: 'left',
                  minHeight: '44px'
                }}
                className="hover:bg-red-900/20"
              >
                <Trash2 style={{ width: '16px', height: '16px' }} /> 
                Delete
              </button>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

// ============================================
// SECTION COMPONENT (Always open by default now)
// ============================================
const Section = ({ title, icon, count, children, defaultOpen = true }) => {
  const [open, setOpen] = useState(defaultOpen);
  if (count === 0) return null;
  
  return (
    <div style={{ marginBottom: '8px' }}>
      <button 
        onClick={() => setOpen(!open)} 
        style={{
          width: 'calc(100% - 16px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 12px',
          margin: '0 8px',
          border: 'none',
          background: 'transparent',
          cursor: 'pointer',
          borderRadius: '8px',
          transition: 'background 0.15s'
        }}
        className="hover:bg-slate-800/50"
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {icon}
          <span style={{
            fontSize: '11px',
            fontWeight: '700',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: '#6b6b80'
          }}>
            {title}
          </span>
          <span style={{
            padding: '2px 8px',
            backgroundColor: 'rgba(28, 28, 42, 0.85)',
            borderRadius: '10px',
            fontSize: '11px',
            fontWeight: '600',
            color: '#a1a1b5'
          }}>
            {count}
          </span>
        </span>
        {open 
          ? <ChevronUp style={{ width: '16px', height: '16px', color: '#6b6b80' }} /> 
          : <ChevronDown style={{ width: '16px', height: '16px', color: '#6b6b80' }} />
        }
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            style={{ overflow: 'hidden' }}
          >
            <div style={{ marginTop: '4px', paddingBottom: '4px' }}>{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ============================================
// USER PROFILE DROPDOWN COMPONENT
// ============================================
const UserProfileDropdown = ({ onClose }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { isDarkMode, toggleDarkMode } = useTheme();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsExpanded(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Get user initials
  const getInitials = () => {
    if (!user?.name && !user?.full_name) return '?';
    const name = user?.full_name || user?.name || '';
    const names = name.split(' ');
    if (names.length >= 2) {
      return `${names[0][0]}${names[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  // Handle navigation
  const handleNavigate = (path) => {
    setIsExpanded(false);
    onClose?.();
    navigate(path);
  };

  // Handle logout
  const handleLogout = async () => {
    setIsExpanded(false);
    onClose?.();
    await logout();
    navigate('/');
  };

  // Get subscription tier
  const subscriptionTier = user?.subscription_type || 'FREE';
  const isPro = subscriptionTier === 'PRO';

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      {/* User Profile Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 16px',
          backgroundColor: isExpanded ? 'rgba(28, 28, 42, 0.85)' : 'rgba(20, 20, 32, 0.8)',
          border: 'none',
          borderRadius: '14px',
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}
        className="hover:bg-slate-800/50"
      >
        {/* Avatar */}
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #7C3AED 0%, #EC4899 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: '700',
          fontSize: '15px',
          flexShrink: 0,
          boxShadow: '0 2px 8px rgba(124, 58, 237, 0.3)'
        }}>
          {getInitials()}
        </div>
        
        {/* User Info */}
        <div style={{ flex: 1, textAlign: 'left', minWidth: 0 }}>
          <p style={{
            margin: 0,
            fontSize: '14px',
            fontWeight: '600',
            color: '#f1f5f9',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {user?.full_name || user?.name || 'Student'}
          </p>
          <p style={{
            margin: '2px 0 0 0',
            fontSize: '12px',
            color: isPro ? '#e879a9' : '#6b6b80',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            {isPro && <Crown style={{ width: '12px', height: '12px' }} />}
            {subscriptionTier === 'FREE' ? 'Free Plan' : `${subscriptionTier} Plan`}
          </p>
        </div>

        {/* Chevron */}
        <ChevronUp 
          style={{ 
            width: '18px', 
            height: '18px', 
            color: '#6b6b80',
            transition: 'transform 0.2s ease',
            transform: isExpanded ? 'rotate(0deg)' : 'rotate(180deg)'
          }} 
        />
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            style={{
              position: 'absolute',
              bottom: '100%',
              left: 0,
              right: 0,
              marginBottom: '8px',
              backgroundColor: '#1c1c2a',
              borderRadius: '16px',
              boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              overflow: 'hidden',
              zIndex: 1200,
              /* FIXED: Ensure dropdown doesn't overflow viewport */
              maxHeight: 'calc(100vh - 180px)',
              overflowY: 'auto'
            }}
          >
            {/* Navigation Items */}
            <div style={{ padding: '8px' }}>
              {/* Home / Dashboard */}
              <button
                onClick={() => handleNavigate('/dashboard')}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  border: 'none',
                  background: 'transparent',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'background 0.15s'
                }}
                className="hover:bg-slate-800/50"
              >
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(99, 102, 241, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <LayoutDashboard style={{ width: '18px', height: '18px', color: '#6366f1' }} />
                </div>
                <div>
                  <p style={{ margin: 0, fontSize: '14px', fontWeight: '500', color: '#f1f5f9' }}>
                    Home
                  </p>
                  <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: '#6b6b80' }}>
                    Go to dashboard
                  </p>
                </div>
              </button>

              {/* Profile */}
              <button
                onClick={() => handleNavigate('/profile')}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  border: 'none',
                  background: 'transparent',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'background 0.15s'
                }}
                className="hover:bg-slate-800/50"
              >
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(139, 92, 246, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <User style={{ width: '18px', height: '18px', color: '#8b5cf6' }} />
                </div>
                <div>
                  <p style={{ margin: 0, fontSize: '14px', fontWeight: '500', color: '#f1f5f9' }}>
                    Profile
                  </p>
                  <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: '#6b6b80' }}>
                    Edit your details
                  </p>
                </div>
              </button>

              {/* Upgrade Plan - Only show if not PRO */}
              {!isPro && (
                <button
                  onClick={() => handleNavigate('/subscription')}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 14px',
                    border: 'none',
                    background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, rgba(236, 72, 153, 0.08) 100%)',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s'
                  }}
                  className="hover:opacity-90"
                >
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '10px',
                    background: 'linear-gradient(135deg, #7C3AED 0%, #EC4899 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <Crown style={{ width: '18px', height: '18px', color: 'white' }} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <p style={{ margin: 0, fontSize: '14px', fontWeight: '600', color: '#7C3AED' }}>
                      Go Premium
                    </p>
                    <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: '#9333EA' }}>
                      Unlock all features
                    </p>
                  </div>
                  <Sparkles style={{ width: '16px', height: '16px', color: '#EC4899' }} />
                </button>
              )}
            </div>

            {/* Divider */}
            <div style={{ height: '1px', backgroundColor: '#E5E7EB' }} />

            {/* Theme Toggle */}
            <div style={{ padding: '8px' }}>
              <button
                onClick={toggleDarkMode}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '12px',
                  padding: '12px 14px',
                  border: 'none',
                  background: 'transparent',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  transition: 'background 0.15s'
                }}
                className="hover:bg-slate-800/50"
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '10px',
                    backgroundColor: isDarkMode ? 'rgba(251, 191, 36, 0.2)' : 'rgba(28, 28, 42, 0.85)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {isDarkMode 
                      ? <Sun style={{ width: '18px', height: '18px', color: '#fbbf24' }} />
                      : <Moon style={{ width: '18px', height: '18px', color: '#a1a1b5' }} />
                    }
                  </div>
                  <p style={{ margin: 0, fontSize: '14px', fontWeight: '500', color: '#f1f5f9' }}>
                    {isDarkMode ? 'Light Mode' : 'Dark Mode'}
                  </p>
                </div>
                {/* Toggle Switch */}
                <div style={{
                  width: '44px',
                  height: '24px',
                  borderRadius: '12px',
                  backgroundColor: isDarkMode ? '#7C3AED' : '#D1D5DB',
                  position: 'relative',
                  transition: 'background-color 0.2s ease'
                }}>
                  <div style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '10px',
                    backgroundColor: 'white',
                    position: 'absolute',
                    top: '2px',
                    left: isDarkMode ? '22px' : '2px',
                    transition: 'left 0.2s ease',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
                  }} />
                </div>
              </button>
            </div>

            {/* Divider */}
            <div style={{ height: '1px', backgroundColor: '#E5E7EB' }} />

            {/* Logout */}
            <div style={{ padding: '8px' }}>
              <button
                onClick={handleLogout}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  border: 'none',
                  background: 'transparent',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'background 0.15s'
                }}
                className="hover:bg-red-900/20"
              >
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(239, 68, 68, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <LogOut style={{ width: '18px', height: '18px', color: '#ef4444' }} />
                </div>
                <p style={{ margin: 0, fontSize: '14px', fontWeight: '500', color: '#ef4444' }}>
                  Sign Out
                </p>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ============================================
// MAIN SIDEBAR COMPONENT
// ============================================
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
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => 
    chats.filter(c => 
      c.title?.toLowerCase().includes(search.toLowerCase()) ||
      c.subject?.toLowerCase().includes(search.toLowerCase())
    ), 
    [chats, search]
  );

  const grouped = useMemo(() => {
    const pinned = filtered.filter(c => c.isPinned);
    const unpinned = filtered.filter(c => !c.isPinned);
    return { pinned, ...groupChatsByDate(unpinned) };
  }, [filtered]);

  const renderItems = (list) => list.map(c => (
    <ChatItem 
      key={c.id} 
      chat={c} 
      isActive={c.id === activeSessionId} 
      onClick={onChatSelect} 
      onRename={onRenameChat} 
      onDelete={onDeleteChat} 
      onPin={onPinChat} 
    />
  ));

  // Button gradient style (inline for reliability)
  const newChatButtonStyle = {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '14px 20px',
    background: 'linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%)',
    color: 'white',
    fontWeight: '600',
    fontSize: '15px',
    border: 'none',
    borderRadius: '14px',
    cursor: 'pointer',
    boxShadow: '0 4px 20px rgba(124, 58, 237, 0.35)',
    transition: 'all 0.2s ease',
    transform: 'translateY(0)'
  };

  // Search input style (inline for reliability) - Dark theme
  const searchInputStyle = {
    width: '100%',
    paddingLeft: '40px',
    paddingRight: '16px',
    paddingTop: '12px',
    paddingBottom: '12px',
    backgroundColor: 'rgba(28, 28, 42, 0.85)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: '12px',
    fontSize: '14px',
    outline: 'none',
    color: '#f1f5f9',
    transition: 'all 0.2s ease'
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
            style={{
              position: 'fixed',
              inset: 0,
              backgroundColor: 'rgba(0,0,0,0.3)',
              backdropFilter: 'blur(4px)',
              zIndex: 1100
            }}
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      {/* Sidebar Drawer - Responsive width */}
      {/* FIXED: Better width calculation for small phones - leaves backdrop visible */}
      <motion.div
        initial={false}
        animate={{ x: isOpen ? 0 : '-100%' }}
        transition={{ type: 'spring', stiffness: 400, damping: 40 }}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          bottom: 0,
          /* FIXED: On phones < 375px, use 80vw (leaves 20% for backdrop)
             On phones >= 375px, cap at 300px for better UX */
          width: 'min(300px, 80vw)',
          maxWidth: '300px',
          backgroundColor: '#0f0f16',
          boxShadow: '4px 0 30px rgba(0,0,0,0.5)',
          zIndex: 1150,
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* === HEADER === */}
        <div style={{
          padding: '20px',
          backgroundColor: '#141420',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)'
        }}>
          {/* Title Row */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '16px'
          }}>
            <h2 style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '22px',
              fontWeight: '700',
              color: '#f1f5f9',
              margin: 0
            }}>
              <BookOpen style={{ width: '24px', height: '24px', color: '#8b5cf6' }} />
              Library
            </h2>
            <button 
              onClick={onClose}
              style={{
                padding: '10px',
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                borderRadius: '12px',
                transition: 'background 0.15s',
                minWidth: '44px',
                minHeight: '44px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              className="hover:bg-slate-800/50"
              aria-label="Close"
            >
              <X style={{ width: '20px', height: '20px', color: '#a1a1b5' }} />
            </button>
          </div>
          
          {/* Search Bar - Clean, borderless */}
          <div style={{ position: 'relative' }}>
            <Search style={{
              position: 'absolute',
              left: '14px',
              top: '50%',
              transform: 'translateY(-50%)',
              width: '16px',
              height: '16px',
              color: '#6b6b80'
            }} />
            <input
              placeholder="Search sessions..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={searchInputStyle}
              onFocus={(e) => {
                e.target.style.backgroundColor = 'rgba(38, 38, 55, 0.9)';
                e.target.style.borderColor = 'rgba(139, 92, 246, 0.5)';
                e.target.style.boxShadow = '0 0 0 2px rgba(139, 92, 246, 0.2)';
              }}
              onBlur={(e) => {
                e.target.style.backgroundColor = 'rgba(28, 28, 42, 0.85)';
                e.target.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>
        </div>

        {/* === CHAT LIST === */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          paddingTop: '12px',
          paddingBottom: '12px'
        }}>
          {isLoading ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '80px 0'
            }}>
              <div style={{
                width: '32px',
                height: '32px',
                border: '3px solid rgba(255, 255, 255, 0.08)',
                borderTopColor: '#8b5cf6',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
            </div>
          ) : filtered.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '80px 24px'
            }}>
              <div style={{
                width: '64px',
                height: '64px',
                margin: '0 auto 16px',
                backgroundColor: 'rgba(28, 28, 42, 0.85)',
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <MessageCircle style={{ width: '32px', height: '32px', color: '#6b6b80' }} />
              </div>
              <p style={{ fontWeight: '500', color: '#a1a1b5', margin: '0 0 4px 0' }}>No sessions yet</p>
              <p style={{ fontSize: '14px', color: '#6b6b80', margin: 0 }}>Start a conversation to begin</p>
            </div>
          ) : (
            <>
              {/* Pinned */}
              {grouped.pinned.length > 0 && (
                <Section 
                  title="Pinned" 
                  icon={<Pin style={{ width: '14px', height: '14px', color: '#F59E0B' }} />} 
                  count={grouped.pinned.length}
                  defaultOpen={true}
                >
                  {renderItems(grouped.pinned)}
                </Section>
              )}
              
              {/* Today */}
              <Section 
                title="Today" 
                icon={<Sparkles style={{ width: '14px', height: '14px', color: '#7C3AED' }} />} 
                count={grouped.today.length}
                defaultOpen={true}
              >
                {renderItems(grouped.today)}
              </Section>
              
              {/* This Week */}
              <Section 
                title="This Week" 
                icon={<Clock style={{ width: '14px', height: '14px', color: '#3B82F6' }} />} 
                count={grouped.thisWeek.length} 
                defaultOpen={true}
              >
                {renderItems(grouped.thisWeek)}
              </Section>
              
              {/* Earlier */}
              <Section 
                title="Earlier" 
                icon={<History style={{ width: '14px', height: '14px', color: '#9CA3AF' }} />} 
                count={grouped.older.length} 
                defaultOpen={true}
              >
                {renderItems(grouped.older)}
              </Section>
            </>
          )}
        </div>

        {/* === FOOTER: NEW CHAT + USER PROFILE === */}
        {/* Added safe-area padding for iOS devices */}
        {/* FIXED: Added padding-top to ensure dropdown has space to expand upward */}
        <div style={{
          backgroundColor: '#141420',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          paddingTop: '8px',
          paddingBottom: 'max(16px, env(safe-area-inset-bottom, 16px))'
        }}>
          {/* New Chat Button */}
          <div style={{ padding: '12px 16px 8px 16px' }}>
            <button
              onClick={() => { 
                onNewChat?.(); 
                onClose?.(); 
              }}
              style={newChatButtonStyle}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 8px 30px rgba(124, 58, 237, 0.45)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 20px rgba(124, 58, 237, 0.35)';
              }}
            >
              <Plus style={{ width: '20px', height: '20px', strokeWidth: 2.5 }} />
              New Conversation
            </button>
          </div>
          
          {/* Divider */}
          <div style={{ height: '1px', backgroundColor: 'rgba(255, 255, 255, 0.08)', margin: '0 16px' }} />
          
          {/* User Profile Dropdown */}
          <div style={{ padding: '12px 16px 16px 16px' }}>
            <UserProfileDropdown onClose={onClose} />
          </div>
        </div>
      </motion.div>

      {/* Spinner Animation Keyframe */}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
}

// ============================================
// VISUAL TOAST (Mobile notification)
// ============================================
export const VisualToast = ({ show, onClose }) => (
  <AnimatePresence>
    {show && (
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        style={{
          position: 'fixed',
          bottom: '96px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 50
        }}
        className="md:hidden"
      >
        <button 
          onClick={onClose}
          style={{
            padding: '12px 20px',
            background: 'linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%)',
            color: 'white',
            borderRadius: '9999px',
            border: 'none',
            boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            cursor: 'pointer'
          }}
        >
          <Sparkles style={{ width: '16px', height: '16px' }} />
          New visual ready!
        </button>
      </motion.div>
    )}
  </AnimatePresence>
);
