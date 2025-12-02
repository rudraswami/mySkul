/**
 * Subject Badge Component
 * Displays detected subject with color-coded badge
 */
import React from 'react';
import { Book, Calculator, Atom, FlaskConical, Dna, Code, BookOpen } from 'lucide-react';

const SubjectBadge = ({ subject }) => {
  const subjectConfig = {
    'Mathematics': {
      colors: 'from-blue-500 to-cyan-500',
      icon: Calculator,
      label: 'Math'
    },
    'Physics': {
      colors: 'from-purple-500 to-pink-500',
      icon: Atom,
      label: 'Physics'
    },
    'Chemistry': {
      colors: 'from-green-500 to-emerald-500',
      icon: FlaskConical,
      label: 'Chemistry'
    },
    'Biology': {
      colors: 'from-green-600 to-teal-600',
      icon: Dna,
      label: 'Biology'
    },
    'Computer Science': {
      colors: 'from-indigo-500 to-purple-500',
      icon: Code,
      label: 'CS'
    },
    'English': {
      colors: 'from-red-500 to-orange-500',
      icon: BookOpen,
      label: 'English'
    }
  };

  const config = subjectConfig[subject] || {
    colors: 'from-gray-500 to-gray-600',
    icon: Book,
    label: subject || 'General'
  };

  const Icon = config.icon;

  return (
    <div className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r ${config.colors} text-white text-xs font-semibold shadow-md`}>
      <Icon className="h-3.5 w-3.5" />
      <span>{config.label}</span>
    </div>
  );
};

export default SubjectBadge;
























