import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Mic, X, Sparkles, TrendingUp } from 'lucide-react';

/**
 * Interactive AI Mentor Chat Component
 * Provides contextual guidance and feedback
 */
const AIMentorChat = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  const messagesEndRef = useRef(null);
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    // Initial greeting
    if (isOpen && messages.length === 0) {
      setTimeout(() => {
        addAIMessage("Hi! I'm your AI Mentor. How can I help you today? 🎓");
      }, 500);
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addUserMessage = (text) => {
    const message = {
      id: Date.now(),
      type: 'user',
      content: text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const addAIMessage = (text) => {
    const message = {
      id: Date.now() + 1,
      type: 'ai',
      content: text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    addUserMessage(userMessage);
    setInput('');
    setIsTyping(true);

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const responses = [
        "That's a great question! Let me help you understand this better. 📚",
        "I can see you're working hard! Keep up the amazing effort. 💪",
        "Based on your recent progress, I'd recommend focusing on your weaker topics first. 🎯",
        "You're doing fantastic! Your consistency is really paying off. 🌟",
        "Let me break this down for you in simpler terms... 🧠"
      ];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      addAIMessage(randomResponse);
      setIsTyping(false);
    }, 1500);
  };

  const quickSuggestions = [
    "What should I study today?",
    "Review my progress",
    "Study tips for exams",
    "Motivate me!"
  ];

  const handleQuickSuggestion = (suggestion) => {
    setInput(suggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-end p-4 md:p-6 pointer-events-none">
      <div className="pointer-events-auto w-full max-w-md h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col animate-slide-in-right overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-4 flex items-center justify-between text-white">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center animate-pulse-glow">
                <Sparkles className="h-5 w-5" />
              </div>
              <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-purple-600"></div>
            </div>
            <div>
              <h3 className="font-bold">AI Mentor</h3>
              <p className="text-xs text-purple-100">Always here to help</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-container">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex chat-message ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`chat-bubble ${message.type === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}`}>
                {typeof message.content === 'string' 
                  ? message.content 
                  : (message.content?.default_view?.main_content?.content || 
                     message.content?.text || 
                     message.content?.message || 
                     JSON.stringify(message.content))}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="chat-bubble chat-bubble-ai flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestions */}
        {messages.length === 1 && (
          <div className="px-4 pb-2">
            <p className="text-xs text-gray-500 mb-2">Quick suggestions:</p>
            <div className="flex flex-wrap gap-2">
              {quickSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickSuggestion(suggestion)}
                  className="text-xs px-3 py-1.5 bg-purple-50 text-purple-700 rounded-full hover:bg-purple-100 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setVoiceMode(!voiceMode)}
              className={`p-2 rounded-lg transition-colors ${voiceMode ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'}`}
              title="Voice input"
            >
              <Mic className="h-5 w-5" />
            </button>
            
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="p-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Insights Footer */}
        <div className="px-4 py-2 bg-gradient-to-r from-purple-50 to-indigo-50 border-t border-purple-100">
          <div className="flex items-center space-x-2 text-xs text-purple-700">
            <TrendingUp className="h-3 w-3" />
            <span>AI Mentor is learning your patterns to provide better guidance</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIMentorChat;
