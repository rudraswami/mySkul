/**
 * SathiNavMenu - Compact Navigation for Sathi Screen
 * 
 * A sleek dropdown menu integrated into the Sathi header that provides
 * access to all navigation options without leaving the chat experience.
 * 
 * Senior Designer Approach: Keep users in context while providing full access.
 */
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import {
  LayoutDashboard,
  User,
  Settings,
  Crown,
  LogOut,
  Moon,
  Sun,
  ChevronDown,
  Grid3X3,
  Sparkles,
  BookOpen,
  FileText,
  HelpCircle,
  Menu
} from 'lucide-react';

const SathiNavMenu = ({ compact = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  const buttonRef = useRef(null);
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { isDarkMode, toggleDarkMode } = useTheme();

  // Toggle menu with explicit state management
  const toggleMenu = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsOpen(prev => !prev);
  }, []);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    // Close on escape key
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  // Handle navigation
  const handleNavigate = (path) => {
    setIsOpen(false);
    navigate(path);
  };

  // Handle logout
  const handleLogout = async () => {
    setIsOpen(false);
    await logout();
    navigate('/');
  };

  // Get user initials for avatar
  const getInitials = () => {
    if (!user?.name) return '?';
    const names = user.name.split(' ');
    if (names.length >= 2) {
      return `${names[0][0]}${names[1][0]}`.toUpperCase();
    }
    return user.name.substring(0, 2).toUpperCase();
  };

  const primaryNavItems = [
    { 
      icon: LayoutDashboard, 
      label: 'My Dashboard', 
      path: '/dashboard',
      description: 'Track your learning journey',
      color: 'text-blue-600'
    },
    { 
      icon: FileText, 
      label: 'Mock Tests', 
      path: '/mock-tests',
      description: 'Practice & ace your exams',
      color: 'text-green-600'
    },
    { 
      icon: BookOpen, 
      label: 'Smart Notes', 
      path: '/notes',
      description: 'AI notes from any topic',
      color: 'text-purple-600'
    },
  ];

  const userActions = [
    { 
      icon: User, 
      label: 'My Profile', 
      path: '/profile',
      description: 'Edit name, exam & goals'
    },
    { 
      icon: Crown, 
      label: 'Go Premium', 
      path: '/subscription',
      description: 'Unlock unlimited access',
      highlight: true
    },
  ];

  return (
    <div className="relative z-50" ref={menuRef}>
      {/* Menu Trigger Button - Student-friendly label */}
      <motion.button
        ref={buttonRef}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={toggleMenu}
        type="button"
        aria-expanded={isOpen}
        aria-haspopup="true"
        className={`
          flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all duration-200 cursor-pointer select-none
          ${isOpen 
            ? 'bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 shadow-md' 
            : 'bg-gray-100 dark:bg-gray-800 hover:bg-violet-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-violet-600'
          }
        `}
        title="Open menu to explore features"
      >
        <Grid3X3 className="w-4 h-4" />
        {!compact && (
          <>
            <span className="text-sm font-semibold hidden sm:inline">Explore</span>
            <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
          </>
        )}
      </motion.button>

      {/* Dropdown Menu - High z-index to appear above everything */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.96 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute left-0 top-full mt-2 w-80 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden"
            style={{ zIndex: 9999 }}
          >
            {/* User Profile Section */}
            <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                  {getInitials()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 dark:text-white truncate">
                    {user?.name || 'Student'}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                    {user?.email || 'Welcome back!'}
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Navigation - Student Tools */}
            <div className="p-2">
              <p className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                📚 Study Tools
              </p>
              {primaryNavItems.map((item) => (
                <motion.button
                  key={item.path}
                  whileHover={{ x: 4 }}
                  onClick={() => handleNavigate(item.path)}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
                >
                  <div className={`p-2 rounded-lg bg-gray-100 dark:bg-gray-800 group-hover:bg-white dark:group-hover:bg-gray-700 ${item.color}`}>
                    <item.icon className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {item.label}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {item.description}
                    </p>
                  </div>
                </motion.button>
              ))}
            </div>

            {/* Divider */}
            <div className="h-px bg-gray-200 dark:bg-gray-700 mx-4" />

            {/* User Actions */}
            <div className="p-2">
              <p className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                ⚙️ Settings
              </p>
              
              {userActions.map((item) => (
                <motion.button
                  key={item.path}
                  whileHover={{ x: 4 }}
                  onClick={() => handleNavigate(item.path)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors ${
                    item.highlight 
                      ? 'bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 hover:from-purple-100 hover:to-pink-100 dark:hover:from-purple-900/30 dark:hover:to-pink-900/30' 
                      : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                  } group`}
                >
                  <div className={`p-2 rounded-lg ${item.highlight ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>
                    <item.icon className="w-4 h-4" />
                  </div>
                  <div className="text-left flex-1">
                    <p className={`text-sm font-medium ${item.highlight ? 'text-purple-700 dark:text-purple-300' : 'text-gray-900 dark:text-white'}`}>
                      {item.label}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {item.description}
                    </p>
                  </div>
                  {item.highlight && (
                    <Sparkles className="w-4 h-4 text-purple-500" />
                  )}
                </motion.button>
              ))}

              {/* Theme Toggle */}
              <motion.button
                whileHover={{ x: 4 }}
                onClick={toggleDarkMode}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
              >
                <div className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                  {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                </div>
                <div className="text-left flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {isDarkMode ? 'Light Mode' : 'Dark Mode'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Switch appearance
                  </p>
                </div>
                <div className={`w-10 h-5 rounded-full transition-colors ${isDarkMode ? 'bg-purple-500' : 'bg-gray-300'} relative`}>
                  <motion.div
                    animate={{ x: isDarkMode ? 20 : 2 }}
                    className="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow"
                  />
                </div>
              </motion.button>
            </div>

            {/* Divider */}
            <div className="h-px bg-gray-200 dark:bg-gray-700 mx-4" />

            {/* Logout */}
            <div className="p-2">
              <motion.button
                whileHover={{ x: 4 }}
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors group"
              >
                <div className="p-2 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400">
                  <LogOut className="w-4 h-4" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-red-600 dark:text-red-400">
                    Sign Out
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    See you soon!
                  </p>
                </div>
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SathiNavMenu;


