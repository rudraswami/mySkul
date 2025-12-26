/**
 * 🔔 NotificationBell - Real-time Notification Component
 * ========================================================
 * 
 * CRITICAL for reminders to work!
 * Features:
 * - Polls every 30 seconds for new notifications
 * - Shows bell icon with badge count
 * - Dropdown with notification list
 * - Toast notifications with sound
 * - Quick actions (Start studying, Snooze, Dismiss)
 * - Click to navigate to relevant content
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// 🔊 Notification sound (base64 encoded chime)
const NOTIFICATION_SOUND = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2teleQcHS6PZ4pViAABPsNzbcwAAW7jT1GI8A1G42cxjPg5SvM/EYEAbS77EsGNgKEqzmKt2hGQ6f42Gg3VxeS8vc3t5cF1KT2VoZVBMYmNhT0xgYVpNSl5bVktMXFRNREtaUk9GSFFNS0NOR0dDPEJAPjo2OTk3MjIxMS4pKScpJCIeGxoZFhQTEQ8NDAsJBwYEAwIBAAABAQIDBAUGBwkKCwwNDxETFBYYGhseISQnKSssMDI1ODo9QENGS09SV1xhZmtvdHl+g4mPla2z';

const NotificationBell = ({ userId, onStartStudy, onNavigateToChat }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [lastNotificationId, setLastNotificationId] = useState(null);
  const [lastNotificationUpdated, setLastNotificationUpdated] = useState(null);
  const [activeToast, setActiveToast] = useState(null);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const dropdownRef = useRef(null);
  const audioRef = useRef(null);
  
  // Initialize audio on mount
  useEffect(() => {
    audioRef.current = new Audio(NOTIFICATION_SOUND);
    audioRef.current.volume = 0.6;
  }, []);
  
  // Get auth token
  const getAuthHeaders = () => {
    const token = localStorage.getItem('dhruv_ai_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  // Strip markdown from text
  const stripMarkdown = (text) => {
    if (!text) return '';
    return text
      .replace(/\*\*(.*?)\*\*/g, '$1')  // Bold
      .replace(/\*(.*?)\*/g, '$1')       // Italic
      .replace(/__(.*?)__/g, '$1')       // Bold alt
      .replace(/_(.*?)_/g, '$1')         // Italic alt
      .replace(/`(.*?)`/g, '$1')         // Code
      .replace(/\[(.*?)\]\(.*?\)/g, '$1') // Links
      .trim();
  };

  // Format notification message for display
  const formatMessage = (notification) => {
    const msg = stripMarkdown(notification.message || '');
    const title = stripMarkdown(notification.title || 'Notification');
    
    // Make messages more friendly
    if (notification.type === 'reminder' && msg === 'study') {
      return 'Time to study! Your scheduled reminder is here. 📚';
    }
    if (msg.length < 10 && notification.data?.topic) {
      return `Time to study: ${notification.data.topic}`;
    }
    return msg || title;
  };

  // Play notification sound
  const playNotificationSound = () => {
    try {
      if (audioRef.current) {
        audioRef.current.currentTime = 0;
        audioRef.current.play().catch(() => {});
      }
    } catch (e) {
      console.log('Audio playback failed:', e);
    }
  };

  // Poll for new notifications
  const pollNotifications = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/notifications/poll`, {
        headers: getAuthHeaders()
      });
      
      const { unread_count, latest, has_new } = response.data;
      setUnreadCount(unread_count);
      
      // Show toast for new notification OR updated notification (coalesced with new content)
      // Check both notification_id AND created_at to detect content refreshes
      const isNewNotification = latest && latest.notification_id !== lastNotificationId;
      const isUpdatedContent = latest && latest.created_at !== lastNotificationUpdated;
      
      if (has_new && latest && (isNewNotification || isUpdatedContent)) {
        setLastNotificationId(latest.notification_id);
        setLastNotificationUpdated(latest.created_at);
        showNotificationToast(latest);
      }
    } catch (error) {
      console.error('Failed to poll notifications:', error);
    }
  }, [lastNotificationId, lastNotificationUpdated]);

  // Fetch full notification list
  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/notifications/`, {
        headers: getAuthHeaders(),
        params: { limit: 20 }
      });
      
      setNotifications(response.data.notifications || []);
      setUnreadCount(response.data.unread_count || 0);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    try {
      await axios.post(`${API_URL}/api/notifications/mark-read`, {
        notification_ids: notificationId ? [notificationId] : null
      }, {
        headers: getAuthHeaders()
      });
      
      setNotifications(prev => 
        prev.map(n => 
          notificationId ? 
            (n.notification_id === notificationId ? { ...n, read: true } : n) :
            { ...n, read: true }
        )
      );
      setUnreadCount(notificationId ? Math.max(0, unreadCount - 1) : 0);
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  // 📊 Track notification outcome for Mentor Companion learning
  const trackOutcome = async (notificationId, outcome, details = null) => {
    try {
      await axios.post(`${API_URL}/api/notifications/outcome`, {
        notification_id: notificationId,
        outcome: outcome,
        details: details
      }, {
        headers: getAuthHeaders()
      });
      console.log(`📊 Outcome tracked: ${notificationId} → ${outcome}`);
    } catch (error) {
      console.error('Failed to track outcome:', error);
    }
  };

  // Show toast notification
  const showNotificationToast = (notification) => {
    playNotificationSound();
    setActiveToast(notification);
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
      setActiveToast(null);
    }, 10000);
  };
  
  // Handle notification click - open detail view
  const handleNotificationClick = (notification) => {
    setSelectedNotification(notification);
    if (!notification.read) {
      markAsRead(notification.notification_id);
    }
    // 📊 Track that user clicked/engaged with this notification
    trackOutcome(notification.notification_id, 'clicked', {
      type: notification.type,
      title: notification.title
    });
  };

  // Handle quick actions
  const handleStartStudying = (notification) => {
    markAsRead(notification.notification_id);
    setSelectedNotification(null);
    setIsOpen(false);
    setActiveToast(null);
    
    // 📊 Track that user started studying after this notification - this is SUCCESS!
    trackOutcome(notification.notification_id, 'studied', {
      type: notification.type,
      topic: notification.data?.topic || notification.message
    });
    
    // Navigate to chat with topic pre-filled
    if (onStartStudy) {
      onStartStudy(notification.data?.topic || notification.message || 'study session');
    } else if (onNavigateToChat) {
      onNavigateToChat(notification.data?.topic);
    }
  };

  const handleSnooze = async (notification, minutes = 30) => {
    try {
      markAsRead(notification.notification_id);
      setSelectedNotification(null);
      setActiveToast(null);
      
      // 📊 Track snooze - user wants to engage later
      trackOutcome(notification.notification_id, 'snoozed', {
        type: notification.type,
        snooze_minutes: minutes
      });
      
      // Show snooze confirmation
      alert(`⏰ Snoozed for ${minutes} minutes! I'll remind you again.`);
    } catch (error) {
      console.error('Failed to snooze:', error);
    }
  };

  const handleDismiss = (notification) => {
    markAsRead(notification.notification_id);
    setSelectedNotification(null);
    setActiveToast(null);
    
    // 📊 Track dismiss - notification wasn't valuable to user
    trackOutcome(notification.notification_id, 'dismissed', {
      type: notification.type
    });
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setSelectedNotification(null);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Start polling on mount
  useEffect(() => {
    pollNotifications();
    const interval = setInterval(pollNotifications, 30000);
    return () => clearInterval(interval);
  }, [pollNotifications]);

  // Fetch full list when dropdown opens
  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  // Format time ago
  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  // Get icon based on notification type (includes Phase 3 Mentor Intent types)
  const getNotificationIcon = (type) => {
    switch (type) {
      // Legacy types
      case 'reminder': return '⏰';
      case 'streak': return '🔥';
      case 'achievement': return '🏆';
      case 'study': return '📚';
      case 'motivation': return '💪';
      case 'break': return '☕';
      case 'spaced_repetition': return '🧠';
      case 'revision': return '📖';
      // Phase 3 Mentor Intent types
      case 'help': return '💙';
      case 'protect': return '🛡️';
      case 'celebrate': return '🎉';
      case 'guide': return '🧭';
      case 'silence': return '🤫';
      default: return '🔔';
    }
  };

  // Get action text based on notification type (clean, no redundant emoji)
  const getActionText = (type) => {
    switch (type) {
      // Legacy types
      case 'reminder': return 'Start Studying';
      case 'revision': return 'Begin Revision';
      case 'spaced_repetition': return 'Quick Review';
      case 'break': return 'Take a Break';
      // Phase 3 Mentor Intent types
      case 'help': return 'Get Help';
      case 'protect': return 'Keep Going';
      case 'celebrate': return 'View Achievement';
      case 'guide': return 'Continue Learning';
      default: return 'View Details';
    }
  };

  return (
    <div className="notification-bell-container" ref={dropdownRef} style={{ position: 'relative', zIndex: 9999 }}>
      {/* Bell Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => {
          setIsOpen(!isOpen);
          setSelectedNotification(null);
        }}
        style={{
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
          border: '1px solid rgba(102, 126, 234, 0.3)',
          borderRadius: '12px',
          cursor: 'pointer',
          position: 'relative',
          padding: '8px 12px',
          fontSize: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}
      >
        <motion.span 
          role="img" 
          aria-label="notifications"
          animate={unreadCount > 0 ? { rotate: [0, -10, 10, -10, 0] } : {}}
          transition={{ duration: 0.5, repeat: unreadCount > 0 ? Infinity : 0, repeatDelay: 3 }}
        >
          🔔
        </motion.span>
        
        {/* Badge */}
        <AnimatePresence>
          {unreadCount > 0 && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              style={{
                position: 'absolute',
                top: -4,
                right: -4,
                background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                color: 'white',
                borderRadius: '10px',
                minWidth: '20px',
                height: '20px',
                fontSize: '11px',
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '0 6px',
                boxShadow: '0 2px 8px rgba(239, 68, 68, 0.4)'
              }}
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </motion.span>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Dropdown - Fixed positioning */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            style={{
              position: 'fixed',
              top: '70px',
              right: '20px',
              width: '380px',
              maxHeight: '520px',
              background: 'linear-gradient(180deg, #1e1e2e 0%, #1a1a28 100%)',
              borderRadius: '16px',
              boxShadow: '0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.1)',
              overflow: 'hidden',
              zIndex: 10001
            }}
          >
            {/* Header */}
            <div style={{
              padding: '16px 20px',
              background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)',
              borderBottom: '1px solid rgba(255,255,255,0.1)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '20px' }}>🔔</span>
                <h3 style={{ margin: 0, color: 'white', fontSize: '16px', fontWeight: '600' }}>
                  Notifications
                </h3>
                {unreadCount > 0 && (
                  <span style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    padding: '3px 10px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    color: 'white',
                    fontWeight: '600'
                  }}>
                    {unreadCount} new
                  </span>
                )}
              </div>
              {unreadCount > 0 && (
                <button
                  onClick={() => markAsRead(null)}
                  style={{
                    background: 'rgba(255,255,255,0.1)',
                    border: 'none',
                    color: '#a5b4fc',
                    cursor: 'pointer',
                    fontSize: '12px',
                    padding: '6px 12px',
                    borderRadius: '8px',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => e.target.style.background = 'rgba(255,255,255,0.15)'}
                  onMouseOut={(e) => e.target.style.background = 'rgba(255,255,255,0.1)'}
                >
                  Mark all read
                </button>
              )}
            </div>

            {/* Notification List or Detail View */}
            <div style={{ maxHeight: '440px', overflowY: 'auto' }}>
              {selectedNotification ? (
                // Detail View - Cleaner design
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  style={{ padding: '20px' }}
                >
                  {/* Back button */}
                  <button
                    onClick={() => setSelectedNotification(null)}
                    style={{
                      background: 'rgba(255,255,255,0.1)',
                      border: 'none',
                      color: '#a5b4fc',
                      cursor: 'pointer',
                      fontSize: '13px',
                      padding: '8px 14px',
                      borderRadius: '8px',
                      marginBottom: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      transition: 'background 0.2s'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.15)'}
                    onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                  >
                    ← Back to all
                  </button>
                  
                  {/* Notification detail - Better sized icon */}
                  <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                    <div style={{
                      width: '64px',
                      height: '64px',
                      background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)',
                      borderRadius: '16px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto 16px'
                    }}>
                      <span style={{ fontSize: '32px' }}>
                        {getNotificationIcon(selectedNotification.type)}
                      </span>
                    </div>
                    <h3 style={{ color: 'white', margin: '0 0 8px', fontSize: '18px', fontWeight: '600' }}>
                      {stripMarkdown(selectedNotification.title)}
                    </h3>
                    <p style={{ color: 'rgba(255,255,255,0.8)', margin: 0, fontSize: '14px', lineHeight: '1.6' }}>
                      {formatMessage(selectedNotification)}
                    </p>
                    <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: '12px', marginTop: '10px', display: 'block' }}>
                      {formatTimeAgo(selectedNotification.created_at)}
                    </span>
                  </div>
                  
                  {/* Action Buttons - Consistent styling */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleStartStudying(selectedNotification)}
                      style={{
                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        border: 'none',
                        color: 'white',
                        padding: '14px 20px',
                        borderRadius: '12px',
                        fontSize: '15px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        boxShadow: '0 4px 15px rgba(99, 102, 241, 0.4)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px'
                      }}
                    >
                      <span>📚</span>
                      {getActionText(selectedNotification.type)}
                    </motion.button>
                    
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleSnooze(selectedNotification, 30)}
                        style={{
                          flex: 1,
                          background: 'rgba(255,255,255,0.1)',
                          border: '1px solid rgba(255,255,255,0.15)',
                          color: 'white',
                          padding: '12px 16px',
                          borderRadius: '10px',
                          fontSize: '14px',
                          fontWeight: '500',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '6px'
                        }}
                      >
                        <span>⏰</span> Snooze 30m
                      </motion.button>
                      
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleDismiss(selectedNotification)}
                        style={{
                          flex: 1,
                          background: 'rgba(255,255,255,0.05)',
                          border: '1px solid rgba(255,255,255,0.1)',
                          color: 'rgba(255,255,255,0.7)',
                          padding: '12px 16px',
                          borderRadius: '10px',
                          fontSize: '14px',
                          fontWeight: '500',
                          cursor: 'pointer'
                        }}
                      >
                        Dismiss
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              ) : loading ? (
                <div style={{ padding: '40px', textAlign: 'center', color: 'rgba(255,255,255,0.5)' }}>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    style={{ fontSize: '24px', marginBottom: '8px' }}
                  >
                    ⏳
                  </motion.div>
                  Loading...
                </div>
              ) : notifications.length === 0 ? (
                <div style={{ 
                  padding: '50px 20px', 
                  textAlign: 'center', 
                  color: 'rgba(255,255,255,0.5)' 
                }}>
                  <span style={{ fontSize: '48px', display: 'block', marginBottom: '12px', opacity: 0.5 }}>🔕</span>
                  <p style={{ margin: 0, fontSize: '15px' }}>No notifications yet</p>
                  <p style={{ margin: '8px 0 0', fontSize: '13px', opacity: 0.7 }}>
                    Reminders and updates will appear here
                  </p>
                </div>
              ) : (
                // Notification List
                notifications.map((notification, index) => (
                  <motion.div
                    key={notification.notification_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ backgroundColor: 'rgba(255,255,255,0.08)' }}
                    onClick={() => handleNotificationClick(notification)}
                    style={{
                      padding: '14px 20px',
                      borderBottom: '1px solid rgba(255,255,255,0.05)',
                      cursor: 'pointer',
                      opacity: notification.read ? 0.6 : 1,
                      background: notification.read ? 'transparent' : 'rgba(102, 126, 234, 0.08)'
                    }}
                  >
                    <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                      <div style={{
                        width: '44px',
                        height: '44px',
                        borderRadius: '12px',
                        background: notification.read ? 'rgba(255,255,255,0.05)' : 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '22px',
                        flexShrink: 0
                      }}>
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between',
                          alignItems: 'flex-start',
                          marginBottom: '4px'
                        }}>
                          <strong style={{ 
                            color: 'white', 
                            fontSize: '14px',
                            fontWeight: notification.read ? '500' : '600'
                          }}>
                            {stripMarkdown(notification.title)}
                          </strong>
                          <span style={{ 
                            color: 'rgba(255,255,255,0.4)', 
                            fontSize: '11px',
                            whiteSpace: 'nowrap',
                            marginLeft: '8px'
                          }}>
                            {formatTimeAgo(notification.created_at)}
                          </span>
                        </div>
                        <p style={{ 
                          margin: 0, 
                          color: 'rgba(255,255,255,0.7)',
                          fontSize: '13px',
                          lineHeight: '1.4',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical'
                        }}>
                          {formatMessage(notification)}
                        </p>
                        
                        {/* Quick hint */}
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          marginTop: '8px'
                        }}>
                          {!notification.read && (
                            <span style={{
                              width: '8px',
                              height: '8px',
                              background: '#667eea',
                              borderRadius: '50%'
                            }} />
                          )}
                          <span style={{
                            fontSize: '11px',
                            color: '#a5b4fc'
                          }}>
                            Tap to view options →
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 🔔 Full-screen Toast Notification - Production Ready, TRUE CENTER */}
      <AnimatePresence>
        {activeToast && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              width: '100vw',
              height: '100vh',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'rgba(0, 0, 0, 0.5)',
              backdropFilter: 'blur(8px)',
              WebkitBackdropFilter: 'blur(8px)',
              zIndex: 99999,
              padding: '16px'
            }}
            onClick={() => setActiveToast(null)}
          >
            {/* Toast Card - Centered via flexbox parent */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ type: 'spring', damping: 25, stiffness: 350 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                width: '100%',
                maxWidth: '360px',
                background: '#ffffff',
                borderRadius: '20px',
                boxShadow: '0 20px 50px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(0, 0, 0, 0.05)',
                overflow: 'hidden'
              }}
            >
              {/* Header - Compact & Clean */}
              <div style={{
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                padding: '20px 20px 18px',
                textAlign: 'center'
              }}>
                {/* Icon - Smaller, cleaner */}
                <div style={{
                  width: '48px',
                  height: '48px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  borderRadius: '14px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '12px'
                }}>
                  <span style={{ fontSize: '24px' }}>{getNotificationIcon(activeToast.type)}</span>
                </div>
                
                {/* Title - Dynamic from notification (intelligent AI-generated) */}
                <h2 style={{ 
                  color: 'white', 
                  margin: 0, 
                  fontSize: '17px',
                  fontWeight: '600',
                  lineHeight: '1.3'
                }}>
                  {stripMarkdown(activeToast.title) || 'Time for a quick review'}
                </h2>
              </div>
              
              {/* Content */}
              <div style={{ padding: '20px' }}>
                <p style={{ 
                  color: '#4b5563', 
                  margin: '0 0 20px', 
                  fontSize: '14px',
                  lineHeight: '1.55',
                  textAlign: 'center'
                }}>
                  {formatMessage(activeToast)}
                </p>
                
                {/* Action Buttons */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {/* Primary Action */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleStartStudying(activeToast)}
                    style={{
                      width: '100%',
                      background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                      border: 'none',
                      color: 'white',
                      padding: '13px 20px',
                      borderRadius: '12px',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      boxShadow: '0 4px 12px rgba(99, 102, 241, 0.25)'
                    }}
                  >
                    📚 View Details
                  </motion.button>
                  
                  {/* Secondary Actions - Matching style */}
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSnooze(activeToast, 30)}
                      style={{
                        flex: 1,
                        background: '#f3f4f6',
                        border: 'none',
                        color: '#374151',
                        padding: '12px 14px',
                        borderRadius: '10px',
                        fontSize: '13px',
                        fontWeight: '500',
                        cursor: 'pointer'
                      }}
                    >
                      ⏰ Snooze 30m
                    </motion.button>
                    
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setActiveToast(null)}
                      style={{
                        flex: 1,
                        background: '#f3f4f6',
                        border: 'none',
                        color: '#6b7280',
                        padding: '12px 14px',
                        borderRadius: '10px',
                        fontSize: '13px',
                        fontWeight: '500',
                        cursor: 'pointer'
                      }}
                    >
                      Later
                    </motion.button>
                  </div>
                </div>
              </div>
              
              {/* Auto-dismiss progress bar */}
              <motion.div
                initial={{ width: '100%' }}
                animate={{ width: '0%' }}
                transition={{ duration: 10, ease: 'linear' }}
                style={{
                  height: '3px',
                  background: 'linear-gradient(90deg, #6366f1, #8b5cf6)'
                }}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NotificationBell;










