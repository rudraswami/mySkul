/**
 * Plan Badge Component
 * Shows current subscription tier with visual styling
 */
import React from 'react';
import { Crown, Zap } from 'lucide-react';

export default function PlanBadge({ tier = 'free', className = '' }) {
  const tiers = {
    free: {
      label: 'Free',
      color: 'bg-gray-100 text-gray-700 border-gray-300',
      icon: null
    },
    basic: {
      label: 'Basic',
      color: 'bg-blue-100 text-blue-700 border-blue-300',
      icon: <Zap className="w-3 h-3" />
    },
    premium: {
      label: 'Premium',
      color: 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white border-purple-600',
      icon: <Crown className="w-3 h-3" />
    }
  };
  
  const tierConfig = tiers[tier.toLowerCase()] || tiers.free;
  
  return (
    <div className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-semibold border ${tierConfig.color} ${className}`}>
      {tierConfig.icon}
      <span>{tierConfig.label}</span>
    </div>
  );
}
