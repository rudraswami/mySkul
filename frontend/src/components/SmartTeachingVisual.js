import React from 'react';
import TeachingOrchestrator from '../teaching/TeachingOrchestrator';

/**
 * SmartTeachingVisual
 * Drop-in wrapper to upgrade static visuals to professor-style storytelling
 * without touching existing layout logic.
 */
export default function SmartTeachingVisual({ topic, subject, visualData, complexity = 'simple', onComplete }) {
  return (
    <TeachingOrchestrator
      topic={topic}
      subject={subject}
      complexity={complexity}
      visualData={visualData}
      onComplete={onComplete}
    />
  );
}

