import React, { useState } from 'react';
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
  Brain
} from 'lucide-react';

export default function Navigation({ mobileMenuOpen, setMobileMenuOpen }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [navigating, setNavigating] = useState(null);

  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      current: location.pathname === '/dashboard'
    },
    {
      name: 'AI Tutor',
      href: '/tutor',
      icon: MessageCircle,
      current: location.pathname === '/tutor'
    },
    {
      name: 'Subscription',
      href: '/subscription',
      icon: CreditCard,
      current: location.pathname === '/subscription'
    }
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

      {/* Sidebar - Professional Design */}
      <motion.div 
        initial={false}
        animate={{
          x: mobileMenuOpen ? 0 : (window.innerWidth >= 1024 ? 0 : -256)
        }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 shadow-lg border-r border-gray-200 dark:border-gray-800 lg:translate-x-0 lg:static lg:inset-0"
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

        {/* Logo Section - Cognitive + Education */}
        <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3">
            {/* Logo: Brain + Book (Cognitive + Education) */}
            <div className="relative flex-shrink-0">
              {/* Logo Container */}
              <div className="relative w-11 h-11 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center shadow-sm">
                {/* Brain Icon (Cognitive) */}
                <Brain className="h-6 w-6 text-white absolute -top-0.5 -left-0.5" strokeWidth={2.5} />
                {/* Book Icon (Education) - Overlapping */}
                <BookOpen className="h-5 w-5 text-white absolute -bottom-0.5 -right-0.5" strokeWidth={2.5} />
              </div>
            </div>
            
            {/* Brand Text */}
            <div className="flex-1 min-w-0">
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white tracking-tight">
                Druv AI
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400 font-medium truncate">
                {user?.exam_type || 'JEE'} Preparation
              </p>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 overflow-y-auto">
          <ul className="space-y-1">
            {navigation.map((item, index) => {
              const Icon = item.icon;
              const isActive = item.current;
              
              return (
                <motion.li
                  key={item.name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                >
                  <motion.button
                    whileHover={{ x: 2 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleNavigation(item.href, item.name)}
                    disabled={navigating === item.name}
                    className={`group relative flex items-center w-full min-h-11 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                    } ${navigating === item.name ? 'opacity-60 cursor-not-allowed' : ''}`}
                  >
                    {/* Active indicator bar */}
                    {isActive && (
                      <motion.div
                        layoutId="activeIndicator"
                        className="absolute left-0 top-0 bottom-0 w-1 bg-blue-600 dark:bg-blue-500 rounded-r-full"
                        initial={false}
                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                      />
                    )}
                    
                    {/* Icon */}
                    <div className={`mr-3 flex-shrink-0 ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200'}`}>
                      {navigating === item.name ? (
                        <LoadingSpinner size="sm" className="h-5 w-5" />
                      ) : (
                        <Icon className="h-5 w-5" />
                      )}
                    </div>
                    
                    {/* Label */}
                    <span className="flex-1 text-left">{item.name}</span>
                  </motion.button>
                </motion.li>
              );
            })}
          </ul>
        </nav>

        {/* User Profile & Actions */}
        <div className="border-t border-gray-200 dark:border-gray-800 p-4 space-y-3">
          {/* User Info */}
          <div className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <Avatar className="h-10 w-10 flex-shrink-0">
              <AvatarFallback className="bg-blue-600 text-white font-semibold text-sm dark:bg-blue-500">
                {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {user?.full_name || 'User'}
              </p>
              <div className="flex items-center gap-1.5 mt-0.5">
                {subscriptionTier === 'PRO' && (
                  <Crown className="h-3 w-3 text-purple-600 dark:text-purple-400 flex-shrink-0" />
                )}
                <span className={`text-xs font-medium px-2 py-0.5 rounded-md ${tierColors[subscriptionTier] || tierColors.FREE}`}>
                  {subscriptionTier === 'FREE' ? 'Free' : subscriptionTier}
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-1">
            {/* Theme Toggle */}
            <div className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-md bg-gray-100 dark:bg-gray-800">
                  <div className="h-3.5 w-3.5 rounded-full bg-gray-400 dark:bg-gray-600"></div>
                </div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Theme</span>
              </div>
              <ThemeToggle />
            </div>
            
            {/* Profile Settings */}
            <button
              onClick={() => handleNavigation('/profile', 'Profile Settings')}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <div className="p-1.5 rounded-md bg-gray-100 dark:bg-gray-800">
                <User className="h-3.5 w-3.5 text-gray-600 dark:text-gray-400" />
              </div>
              <span>Profile Settings</span>
            </button>
            
            {/* Sign Out */}
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm font-medium text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            >
              <div className="p-1.5 rounded-md bg-red-100 dark:bg-red-900/30">
                <LogOut className="h-3.5 w-3.5" />
              </div>
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </motion.div>
    </>
  );
}
