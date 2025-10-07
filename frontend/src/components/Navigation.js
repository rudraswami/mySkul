import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Avatar, AvatarFallback } from './ui/avatar';
import { LoadingSpinner } from './ui/loading';
import { 
  Brain, 
  LayoutDashboard, 
  MessageCircle, 
  FileText, 
  LogOut,
  User,
  Mic,
  CreditCard
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
      name: 'Mock Tests',
      href: '/tests',
      icon: FileText,
      current: location.pathname === '/tests'
    },
    {
      name: 'Auto-Note Mentor',
      href: '/auto-notes',
      icon: Mic,
      current: location.pathname === '/auto-notes'
    },
    // Removed: Analytics and Wellness - not essential for core exam preparation functionality
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
    // Close mobile menu when navigating
    setMobileMenuOpen(false);
    setTimeout(() => {
      navigate(href);
      setNavigating(null);
    }, 300);
  };

  return (
    <>
      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-gray-600 bg-opacity-50 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`${
        mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
      } fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg border-r border-gray-200 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        
        {/* Mobile Close Button */}
        <div className="lg:hidden absolute top-0 right-0 -mr-12 pt-2">
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="ml-1 flex items-center justify-center min-h-12 min-w-12 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white mobile-transition"
            aria-label="Close navigation menu"
          >
            <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Logo */}
        <div className="flex items-center justify-start px-6 py-4 border-b border-gray-200">
          <Brain className="h-8 w-8 text-blue-600 mr-3" />
          <div>
            <h1 className="text-xl font-bold text-gray-900">Dhruv AI</h1>
            <p className="text-xs text-gray-500">{user?.exam_type} Preparation</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6">
          <ul className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.name}>
                  <button
                    onClick={() => handleNavigation(item.href, item.name)}
                    disabled={navigating === item.name}
                    className={`group flex items-center w-full px-3 py-3 text-sm font-medium rounded-lg transition-colors duration-200 ${
                      item.current
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    } ${navigating === item.name ? 'opacity-75 cursor-not-allowed' : ''}`}
                  >
                    {navigating === item.name ? (
                      <LoadingSpinner size="sm" className="mr-3 h-5 w-5 flex-shrink-0" />
                    ) : (
                        <Icon 
                          className={`mr-3 h-5 w-5 ${
                            item.current ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'
                          }`}
                        />
                      )}
                      {item.name}
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* User Profile & Logout */}
          <div className="border-t border-gray-200 p-4">
            {/* User Info */}
            <div className="flex items-center mb-4">
              <Avatar className="h-10 w-10">
                <AvatarFallback className="bg-blue-100 text-blue-700">
                  {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-gray-700">{user?.full_name}</p>
                <p className="text-xs text-gray-500">{user?.subscription_type || 'Free'} Plan</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-2">
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-full justify-start text-gray-600 hover:text-gray-900"
                onClick={() => handleNavigation('/profile', 'Profile Settings')}
              >
                <User className="h-4 w-4 mr-2" />
                Profile Settings
              </Button>
              
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-full justify-start text-gray-600 hover:text-red-600"
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </>
    );
  }