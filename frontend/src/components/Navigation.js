import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Avatar, AvatarFallback } from './ui/avatar';
import { LoadingSpinner } from './ui/loading';
import BrandLogo from './ui/BrandLogo';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LogOut,
  User,
  Crown,
  Brain,
  ChevronDown,
  Settings,
  Home,
  Sparkles
} from 'lucide-react';

/**
 * 🚀 DRON AI — Navigation Sidebar v1.0
 * ==================================================
 * 
 * Design System Compliant:
 * - Brand: DRON AI
 * - Theme: Dark (slate-900 family)
 * - Cards: Glass effect with soft borders
 * - Typography: Sentence case, readable
 */

export default function Navigation({ mobileMenuOpen, setMobileMenuOpen, collapsed, onToggleCollapse }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [navigating, setNavigating] = useState(null);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);
  
  const isSathiPage = location.pathname === '/tutor' || location.pathname.startsWith('/tutor');
  // On AI Sathi page: show collapsed sidebar for consistency (not hidden)
  const isCollapsed = collapsed !== undefined ? collapsed : isSathiPage;

  useEffect(() => {
    function handleClickOutside(event) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Cognito OS: AI Companion first (primary), Progress (secondary)
  const navigation = [
    { name: 'Ask AI', href: '/tutor', icon: Sparkles, current: location.pathname === '/tutor' },
    { name: 'Progress', href: '/dashboard', icon: Home, current: location.pathname === '/dashboard' }
  ];

  const handleLogout = () => logout();

  const handleNavigation = (href, name) => {
    setNavigating(name);
    setMobileMenuOpen(false);
    setTimeout(() => {
      navigate(href);
      setNavigating(null);
    }, 300);
  };

  const subscriptionTier = user?.subscription_type || 'Free';
  const displayName = user?.full_name || 'Student';
  const firstName = displayName.split(' ')[0];

  return (
    <>
      {/* Mobile Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-40 lg:hidden"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* SIDEBAR */}
      <motion.div 
        initial={false}
        animate={{
          x: mobileMenuOpen ? 0 : (window.innerWidth >= 1024 ? 0 : -280),
          width: isCollapsed ? 80 : 260
        }}
        transition={{ type: "spring", damping: 30, stiffness: 200 }}
        className="fixed inset-y-0 left-0 z-50 flex flex-col h-full flex-shrink-0 
          bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950
          border-r border-slate-800/60
          lg:translate-x-0 lg:static lg:inset-0"
      >
        {/* LOGO — Unified Brand */}
        <div className={`flex-shrink-0 border-b border-slate-800/60 ${isCollapsed ? 'px-4 py-6' : 'px-6 py-6'}`}>
          <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
            <BrandLogo 
              size="md" 
              variant={isCollapsed ? 'icon' : 'full'}
              showTagline={!isCollapsed}
              onClick={() => navigate('/dashboard')}
            />
          </div>
        </div>

        {/* NAV ITEMS */}
        <nav className={`flex-1 overflow-y-auto ${isCollapsed ? 'px-3 py-6' : 'px-4 py-6'} space-y-2`}>
          {navigation.map((item, index) => {
            const Icon = item.icon;
            const isActive = item.current;
            
            return (
              <motion.button
                key={item.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.08 }}
                onClick={() => handleNavigation(item.href, item.name)}
                disabled={navigating === item.name}
                className={`w-full group relative flex items-center gap-3 rounded-xl transition-all duration-300 ${
                  isActive 
                    ? 'bg-violet-500/15 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]' 
                    : 'hover:bg-slate-800/50 text-slate-400 hover:text-white'
                } ${isCollapsed ? 'h-12 justify-center' : 'px-4 py-3'}`}
              >
                {/* Active Indicator */}
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-violet-500 rounded-full shadow-[0_0_10px_rgba(139,92,246,0.5)]"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.5 }}
                  />
                )}
                
                <div className={`relative z-10 transition-colors ${isActive ? 'text-violet-400' : ''}`}>
                  {navigating === item.name ? <LoadingSpinner size="sm" /> : <Icon className="w-5 h-5" strokeWidth={1.5} />}
                </div>
                
                {!isCollapsed && (
                  <span className={`relative z-10 font-medium text-sm ${isActive ? 'text-white' : ''}`}>
                    {item.name}
                  </span>
                )}

                {item.badge && !isCollapsed && (
                  <span className="ml-auto px-2 py-0.5 text-[10px] font-bold bg-violet-500/20 text-violet-400 border border-violet-500/30 rounded-full">
                    {item.badge}
                  </span>
                )}
              </motion.button>
            );
          })}
          
        </nav>

        {/* USER PROFILE */}
        <div className={`border-t border-slate-800/60 p-4`} ref={userMenuRef}>
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className={`w-full flex items-center gap-3 p-3 rounded-xl bg-slate-800/40 hover:bg-slate-800/70 border border-slate-700/30 transition-all ${isCollapsed ? 'justify-center' : ''}`}
            >
              {/* Avatar */}
              <div className="relative">
                <div className="absolute inset-0 bg-violet-500 blur-md opacity-30 rounded-xl" />
                <Avatar className="w-9 h-9 border border-slate-700 shadow-lg rounded-xl relative">
                  <AvatarFallback className="bg-gradient-to-br from-violet-600 to-indigo-700 text-white font-bold text-sm">
                    {firstName[0]}
                  </AvatarFallback>
                </Avatar>
              </div>
              
              {!isCollapsed && (
                <div className="flex-1 min-w-0 text-left">
                  <p className="text-sm font-semibold text-white truncate">{firstName}</p>
                  <p className="text-[11px] text-slate-500 capitalize">{subscriptionTier} Plan</p>
                </div>
              )}
              
              {!isCollapsed && (
                <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
              )}
            </button>

            {/* Dropdown */}
            <AnimatePresence>
              {userMenuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.15 }}
                  className={`absolute bg-slate-900 border border-slate-700/50 rounded-xl shadow-2xl overflow-hidden z-[60] backdrop-blur-xl p-1.5 min-w-[200px] ${
                    isCollapsed ? 'left-full bottom-0 ml-3' : 'bottom-full left-0 right-0 mb-2'
                  }`}
                >
                  <div className="px-3 py-2 border-b border-slate-800/60 mb-1">
                    <p className="text-xs text-slate-500">Signed in as</p>
                    <p className="text-sm font-medium text-white truncate">{displayName}</p>
                  </div>
                  
                  {[
                    { icon: User, label: 'Profile', route: '/profile' },
                    { icon: Crown, label: 'Upgrade Plan', route: '/subscription' },
                    { icon: Settings, label: 'Settings', route: '/settings' },
                  ].map((m, i) => (
                    <button
                      key={i}
                      onClick={() => { setUserMenuOpen(false); handleNavigation(m.route, m.label); }}
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-slate-400 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all"
                    >
                      <m.icon className="w-4 h-4" strokeWidth={1.5} />
                      <span>{m.label}</span>
                    </button>
                  ))}
                  
                  <div className="h-px bg-slate-800/60 my-1" />
                  
                  <button
                    onClick={() => { setUserMenuOpen(false); handleLogout(); }}
                    className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all"
                  >
                    <LogOut className="w-4 h-4" strokeWidth={1.5} />
                    <span>Sign Out</span>
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </>
  );
}
