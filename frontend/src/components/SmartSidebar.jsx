/**
 * Smart Sidebar - Modern Space-Efficient Navigation
 * Combines navigation icons + context panel (chat history)
 * Similar to ChatGPT/Claude/Notion design
 */
import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { ThemeToggle } from '../contexts/ThemeContext';
import { Avatar, AvatarFallback } from './ui/avatar';
import {
  LayoutDashboard,
  Sparkles,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Moon,
  Sun,
  Crown,
  User,
  CreditCard,
  Menu,
  X,
  PanelLeftClose,
  PanelLeft
} from 'lucide-react';

// Icon Rail - Always visible, minimal navigation
const IconRail = ({ 
  activeRoute, 
  onNavigate, 
  onToggleSidebar, 
  sidebarOpen,
  user,
  onUserMenuOpen 
}) => {
  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard', route: '/dashboard' },
    { id: 'sathi', icon: Sparkles, label: 'Sathi', route: '/tutor', badge: 'AI' },
  ];

  return (
    <div className="w-14 h-full bg-gray-900 flex flex-col items-center py-3 border-r border-gray-800">
      {/* Logo */}
      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-6 shadow-lg shadow-purple-500/20">
        <span className="text-white font-bold text-lg">D</span>
      </div>

      {/* Toggle Sidebar Button */}
      <button
        onClick={onToggleSidebar}
        className="w-10 h-10 rounded-xl flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-800 transition-all mb-4"
        title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
      >
        {sidebarOpen ? <PanelLeftClose className="w-5 h-5" /> : <PanelLeft className="w-5 h-5" />}
      </button>

      {/* Main Navigation */}
      <nav className="flex-1 flex flex-col items-center gap-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeRoute === item.route || 
                          (item.route === '/tutor' && activeRoute?.startsWith('/tutor'));
          
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.route)}
              className={`relative w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 group ${
                isActive
                  ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
              title={item.label}
            >
              <Icon className="w-5 h-5" />
              
              {/* Badge */}
              {item.badge && (
                <span className="absolute -top-1 -right-1 px-1 text-[8px] font-bold bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded">
                  {item.badge}
                </span>
              )}

              {/* Tooltip */}
              <div className="absolute left-full ml-3 px-2 py-1 bg-gray-800 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50 shadow-lg">
                {item.label}
              </div>
            </button>
          );
        })}
      </nav>

      {/* Bottom Section - User Avatar */}
      <div className="mt-auto flex flex-col items-center gap-3">
        {/* Settings */}
        <button
          onClick={() => onNavigate('/subscription')}
          className="w-10 h-10 rounded-xl flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-800 transition-all group"
          title="Subscription"
        >
          <CreditCard className="w-5 h-5" />
          <div className="absolute left-full ml-3 px-2 py-1 bg-gray-800 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50">
            Subscription
          </div>
        </button>

        {/* User Avatar */}
        <button
          onClick={onUserMenuOpen}
          className="w-10 h-10 rounded-xl overflow-hidden ring-2 ring-gray-700 hover:ring-purple-500 transition-all"
          title="Account"
        >
          <Avatar className="w-full h-full">
            <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white text-sm font-semibold">
              {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
            </AvatarFallback>
          </Avatar>
        </button>
      </div>
    </div>
  );
};

// Context Panel - Chat History or Dashboard content
const ContextPanel = ({ 
  isOpen, 
  activeRoute, 
  children,
  onClose 
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 260, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          transition={{ duration: 0.2, ease: 'easeInOut' }}
          className="h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 overflow-hidden flex-shrink-0"
        >
          <div className="w-[260px] h-full overflow-y-auto">
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// User Menu Dropdown
const UserMenu = ({ isOpen, onClose, user, onLogout, onNavigate }) => {
  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        onClose();
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  const subscriptionTier = user?.subscription_type || 'FREE';

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={menuRef}
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="absolute bottom-16 left-16 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50"
        >
          {/* User Info */}
          <div className="p-4 border-b border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10">
                <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                  {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="font-semibold text-gray-900 dark:text-white text-sm">
                  {user?.full_name || 'User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                  {subscriptionTier === 'PRO' && <Crown className="w-3 h-3 text-purple-500" />}
                  {subscriptionTier === 'FREE' ? 'Free Plan' : subscriptionTier + ' Plan'}
                </p>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div className="py-2">
            <div className="flex items-center justify-between px-4 py-2">
              <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                <Moon className="w-4 h-4 dark:hidden" />
                <Sun className="w-4 h-4 hidden dark:block text-yellow-500" />
                <span>Dark Mode</span>
              </div>
              <ThemeToggle />
            </div>

            <button
              onClick={() => { onClose(); onNavigate('/profile'); }}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <User className="w-4 h-4" />
              <span>Profile Settings</span>
            </button>

            <button
              onClick={() => { onClose(); onNavigate('/subscription'); }}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <Crown className="w-4 h-4 text-purple-500" />
              <span>Upgrade Plan</span>
            </button>
          </div>

          {/* Sign Out */}
          <div className="border-t border-gray-100 dark:border-gray-700 py-2">
            <button
              onClick={() => { onClose(); onLogout(); }}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Main Smart Sidebar Component
export default function SmartSidebar({ 
  children, 
  contextContent,
  defaultSidebarOpen = true 
}) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(defaultSidebarOpen);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleNavigate = (route) => {
    navigate(route);
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      {/* Icon Rail - Always visible */}
      <IconRail
        activeRoute={location.pathname}
        onNavigate={handleNavigate}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        sidebarOpen={sidebarOpen}
        user={user}
        onUserMenuOpen={() => setUserMenuOpen(!userMenuOpen)}
      />

      {/* User Menu */}
      <UserMenu
        isOpen={userMenuOpen}
        onClose={() => setUserMenuOpen(false)}
        user={user}
        onLogout={logout}
        onNavigate={handleNavigate}
      />

      {/* Context Panel (Chat History, etc.) */}
      <ContextPanel isOpen={sidebarOpen} activeRoute={location.pathname}>
        {contextContent}
      </ContextPanel>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {children}
      </div>
    </div>
  );
}

// Export sub-components for flexibility
export { IconRail, ContextPanel, UserMenu };


