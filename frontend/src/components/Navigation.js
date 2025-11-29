import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ThemeToggle } from '../contexts/ThemeContext';
import { Button } from './ui/button';
import { Avatar, AvatarFallback } from './ui/avatar';
import { LoadingSpinner } from './ui/loading';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  MessageCircle, 
  CreditCard,
  LogOut,
  User,
  X,
  Crown,
  BookOpen,
  Brain,
  ChevronDown,
  Settings,
  Moon,
  Sun,
  Sparkles
} from 'lucide-react';

export default function Navigation({ mobileMenuOpen, setMobileMenuOpen, collapsed, onToggleCollapse }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [navigating, setNavigating] = useState(null);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);
  
  // Check if on Sathi/Tutor page - we hide navigation there since AITutor has its own sidebar
  const isSathiPage = location.pathname === '/tutor' || location.pathname.startsWith('/tutor');
  // If collapsed prop is explicitly provided, use it; otherwise auto-collapse on Sathi page
  const isCollapsed = collapsed !== undefined ? collapsed : isSathiPage;
  // Completely hide on Sathi page (AITutor has its own chat history sidebar)
  const isHidden = isSathiPage;

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Navigation items - Subscription moved to user dropdown
  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      current: location.pathname === '/dashboard'
    },
    {
      name: 'Sathi',  // Renamed from "AI Tutor" - "Sathi" means friend in Hindi
      href: '/tutor',
      icon: Sparkles,  // Changed icon to Sparkles for uniqueness
      current: location.pathname === '/tutor',
      badge: 'AI'  // Small badge to indicate AI
    }
    // Subscription removed - now in user dropdown as "Upgrade Plan"
  ];

  const handleLogout = () => {
    logout();
  };

  const handleNavigation = (href, name) => {
    setNavigating(name);
    setMobileMenuOpen(false);
    setTimeout(() => {
      navigate(href);
      setNavigating(null);
    }, 300);
  };

  // Get user's subscription tier for badge
  const subscriptionTier = user?.subscription_type || 'FREE';
  const tierColors = {
    'FREE': 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    'STUDENT': 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    'PRO': 'bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
  };

  // If hidden (on Sathi page), return null completely
  // SathiNavMenu component in AITutorNeuroSymbolic provides integrated navigation
  if (isHidden && !mobileMenuOpen) {
    return null;
  }

  return (
    <>
      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar - Collapsible Design with flex layout */}
      <motion.div 
        initial={false}
        animate={{
          x: mobileMenuOpen ? 0 : (window.innerWidth >= 1024 ? 0 : -256),
          width: isCollapsed ? 64 : 256
        }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="fixed inset-y-0 left-0 z-50 bg-white dark:bg-gray-900 shadow-lg border-r border-gray-200 dark:border-gray-800 lg:translate-x-0 lg:static lg:inset-0 flex flex-col h-full flex-shrink-0"
        style={{ width: isCollapsed ? 64 : 256 }}
      >
        {/* Mobile Close Button */}
        <div className="lg:hidden absolute top-4 right-4 z-10">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center justify-center w-9 h-9 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            aria-label="Close navigation menu"
          >
            <X className="h-5 w-5 text-gray-600 dark:text-gray-300" />
          </motion.button>
        </div>

        {/* Logo Section - Collapsible */}
        <div className={`border-b border-gray-200 dark:border-gray-800 flex-shrink-0 ${isCollapsed ? 'px-2 py-3' : 'px-6 py-5'}`}>
          <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
            {/* Logo: Brain + Book (Cognitive + Education) */}
            <div className="relative flex-shrink-0">
              {/* Logo Container */}
              <div className={`relative bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20 ${isCollapsed ? 'w-10 h-10' : 'w-11 h-11'}`}>
                <span className="text-white font-bold text-lg">D</span>
              </div>
            </div>
            
            {/* Brand Text - Hidden when collapsed */}
            {!isCollapsed && (
              <div className="flex-1 min-w-0">
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white tracking-tight">
                  Druv AI
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400 font-medium truncate">
                  {user?.exam_type || 'JEE'} Preparation
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Items - flex-1 pushes user section to bottom */}
        <nav className={`flex-1 overflow-y-auto min-h-0 ${isCollapsed ? 'px-2 py-3' : 'px-3 py-4'}`}>
          <ul className={`${isCollapsed ? 'space-y-2 flex flex-col items-center' : 'space-y-1'}`}>
            {navigation.map((item, index) => {
              const Icon = item.icon;
              const isActive = item.current;
              
              return (
                <motion.li
                  key={item.name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className={isCollapsed ? 'w-full flex justify-center' : ''}
                >
                  <motion.button
                    whileHover={{ scale: isCollapsed ? 1.1 : 1, x: isCollapsed ? 0 : 2 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleNavigation(item.href, item.name)}
                    disabled={navigating === item.name}
                    className={`group relative flex items-center transition-all duration-200 ${
                      isCollapsed 
                        ? `w-10 h-10 justify-center rounded-xl ${
                            isActive 
                              ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/30' 
                              : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-200'
                          }`
                        : `w-full min-h-11 px-3 py-2.5 text-sm font-medium rounded-lg ${
                            isActive
                              ? 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
                              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                          }`
                    } ${navigating === item.name ? 'opacity-60 cursor-not-allowed' : ''}`}
                    title={isCollapsed ? item.name : undefined}
                  >
                    {/* Active indicator bar - only for expanded */}
                    {isActive && !isCollapsed && (
                      <motion.div
                        layoutId="activeIndicator"
                        className="absolute left-0 top-0 bottom-0 w-1 bg-purple-600 dark:bg-purple-500 rounded-r-full"
                        initial={false}
                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                      />
                    )}
                    
                    {/* Icon */}
                    <div className={`flex-shrink-0 ${!isCollapsed && 'mr-3'} ${isActive && !isCollapsed ? 'text-purple-600 dark:text-purple-400' : ''}`}>
                      {navigating === item.name ? (
                        <LoadingSpinner size="sm" className="h-5 w-5" />
                      ) : (
                        <Icon className="h-5 w-5" />
                      )}
                    </div>
                    
                    {/* Label - Hidden when collapsed */}
                    {!isCollapsed && (
                      <span className="flex-1 text-left">{item.name}</span>
                    )}
                    
                    {/* Badge (for Sathi) - Hidden when collapsed */}
                    {item.badge && !isCollapsed && (
                      <span className="ml-auto px-1.5 py-0.5 text-[10px] font-bold bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-md">
                        {item.badge}
                      </span>
                    )}
                    
                    {/* Badge - Show as dot when collapsed */}
                    {item.badge && isCollapsed && (
                      <span className="absolute -top-1 -right-1 w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full" />
                    )}
                    
                    {/* Tooltip when collapsed */}
                    {isCollapsed && (
                      <div className="absolute left-full ml-3 px-2 py-1 bg-gray-800 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50 shadow-lg">
                        {item.name}
                      </div>
                    )}
                  </motion.button>
                </motion.li>
              );
            })}
          </ul>
        </nav>

        {/* User Profile Section - Fixed at bottom with dropdown */}
        <div className={`border-t border-gray-200 dark:border-gray-800 flex-shrink-0 mt-auto ${isCollapsed ? 'p-2' : 'p-3'}`} ref={userMenuRef}>
          <div className="relative">
            {/* User Button with Dropdown */}
            <motion.button
              whileHover={{ scale: isCollapsed ? 1.1 : 1.01 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className={`flex items-center transition-all duration-200 ${
                isCollapsed 
                  ? 'w-10 h-10 mx-auto justify-center rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800' 
                  : 'w-full gap-3 px-3 py-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
              title={isCollapsed ? user?.full_name || 'Account' : undefined}
            >
              <Avatar className={`flex-shrink-0 ring-2 ring-white dark:ring-gray-700 shadow-sm ${isCollapsed ? 'h-8 w-8' : 'h-9 w-9'}`}>
                <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold text-sm">
                  {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              {!isCollapsed && (
                <>
                  <div className="flex-1 min-w-0 text-left">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                      {user?.full_name || 'User'}
                    </p>
                    <div className="flex items-center gap-1.5">
                      {subscriptionTier === 'PRO' && (
                        <Crown className="h-3 w-3 text-purple-500 flex-shrink-0" />
                      )}
                      <span className={`text-xs font-medium ${subscriptionTier === 'PRO' ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400'}`}>
                        {subscriptionTier === 'FREE' ? 'Free Plan' : subscriptionTier + ' Plan'}
                      </span>
                    </div>
                  </div>
                  <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform duration-200 ${userMenuOpen ? 'rotate-180' : ''}`} />
                </>
              )}
            </motion.button>

            {/* Dropdown Menu */}
            <AnimatePresence>
              {userMenuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 8, scale: 0.96 }}
                  transition={{ duration: 0.15 }}
                  className={`absolute mb-2 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50 ${
                    isCollapsed 
                      ? 'left-full bottom-0 ml-2 w-56' 
                      : 'bottom-full left-0 right-0'
                  }`}
                >
                  {/* Theme Toggle */}
                  <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                    <div className="flex items-center gap-2.5">
                      <Moon className="h-4 w-4 text-gray-500 dark:hidden" />
                      <Sun className="h-4 w-4 text-yellow-500 hidden dark:block" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Dark Mode</span>
                    </div>
                    <ThemeToggle />
                  </div>

                  {/* Menu Items */}
                  <div className="py-1">
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        handleNavigation('/profile', 'Profile');
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <User className="h-4 w-4 text-gray-500" />
                      <span>Profile Settings</span>
                    </button>
                    
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        handleNavigation('/subscription', 'Subscription');
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <Crown className="h-4 w-4 text-purple-500" />
                      <span>Upgrade Plan</span>
                    </button>
                  </div>

                  {/* Sign Out */}
                  <div className="border-t border-gray-100 dark:border-gray-700 py-1">
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        handleLogout();
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </>
  );
}
