/**
 * ⏰ TIMELINE MODE
 * =================
 * 
 * Chronological sequences and historical events
 * Best for: History, evolution, sequential events
 * 
 * Examples:
 * - Historical timeline
 * - Evolution of species
 * - Development stages
 * - Project milestones
 */

import React from 'react';
import {
  SketchCircle,
  SketchLine,
  SketchLabel,
  SketchRect,
} from '../sketch/SketchPrimitives';

export const TimelineMode = ({ blueprint, animationState = {} }) => {
  const { events = [], labels = [], orientation = 'horizontal' } = blueprint;
  
  return (
    <g id="timeline-mode">
      {orientation === 'horizontal' ? (
        <HorizontalTimeline events={events} labels={labels} />
      ) : (
        <VerticalTimeline events={events} labels={labels} />
      )}
    </g>
  );
};

// Horizontal timeline
const HorizontalTimeline = ({ events, labels }) => {
  const timelineY = 150;
  const startX = 50;
  const endX = 350;
  const spacing = (endX - startX) / Math.max(events.length - 1, 1);
  
  return (
    <g>
      {/* Main timeline line */}
      <SketchLine
        x1={startX}
        y1={timelineY}
        x2={endX}
        y2={timelineY}
        strokeWidth={3}
        delay={0}
      />
      
      {/* Arrow at end */}
      <polygon
        points={`${endX},${timelineY} ${endX - 8},${timelineY - 5} ${endX - 8},${timelineY + 5}`}
        fill="#333"
      />
      
      {/* Events */}
      {events.map((event, i) => {
        const x = startX + i * spacing;
        const isAbove = i % 2 === 0;
        
        return (
          <TimelineEvent
            key={`event-${i}`}
            event={event}
            x={x}
            y={timelineY}
            isAbove={isAbove}
            delay={0.3 + i * 0.3}
          />
        );
      })}
      
      {/* Additional labels */}
      {labels.map((label, i) => (
        <SketchLabel
          key={`label-${i}`}
          x={label.x}
          y={label.y}
          text={label.text}
          fontSize={label.fontSize}
          delay={i * 0.2}
        />
      ))}
    </g>
  );
};

// Vertical timeline
const VerticalTimeline = ({ events, labels }) => {
  const timelineX = 100;
  const startY = 50;
  const endY = 270;
  const spacing = (endY - startY) / Math.max(events.length - 1, 1);
  
  return (
    <g>
      {/* Main timeline line */}
      <SketchLine
        x1={timelineX}
        y1={startY}
        x2={timelineX}
        y2={endY}
        strokeWidth={3}
        delay={0}
      />
      
      {/* Arrow at end */}
      <polygon
        points={`${timelineX},${endY} ${timelineX - 5},${endY - 8} ${timelineX + 5},${endY - 8}`}
        fill="#333"
      />
      
      {/* Events */}
      {events.map((event, i) => {
        const y = startY + i * spacing;
        const isRight = i % 2 === 0;
        
        return (
          <TimelineEvent
            key={`event-${i}`}
            event={event}
            x={timelineX}
            y={y}
            isRight={isRight}
            vertical={true}
            delay={0.3 + i * 0.3}
          />
        );
      })}
      
      {/* Additional labels */}
      {labels.map((label, i) => (
        <SketchLabel
          key={`label-${i}`}
          x={label.x}
          y={label.y}
          text={label.text}
          fontSize={label.fontSize}
          delay={i * 0.2}
        />
      ))}
    </g>
  );
};

// Timeline event
const TimelineEvent = ({ event, x, y, isAbove, isRight, vertical = false, delay }) => {
  const offset = vertical ? (isRight ? 50 : -50) : (isAbove ? -60 : 60);
  const labelX = vertical ? x + offset : x;
  const labelY = vertical ? y : y + offset;
  
  return (
    <g>
      {/* Event marker dot */}
      <SketchCircle
        cx={x}
        cy={y}
        radius={6}
        fill={event.color || '#3B82F6'}
        delay={delay}
      />
      
      {/* Connector line */}
      <SketchLine
        x1={x}
        y1={y}
        x2={labelX}
        y2={labelY - (vertical ? 0 : (isAbove ? 20 : -20))}
        strokeWidth={1.5}
        strokeDasharray="2,2"
        delay={delay + 0.1}
      />
      
      {/* Event label box */}
      <g>
        <SketchRect
          x={labelX - 60}
          y={labelY - 30}
          width={120}
          height={50}
          fill="#FFF"
          strokeWidth={2}
          delay={delay + 0.2}
        />
        
        {/* Event title */}
        <text
          x={labelX}
          y={labelY - 10}
          textAnchor="middle"
          fontSize="12"
          fontWeight="bold"
          fill="#333"
        >
          {event.title}
        </text>
        
        {/* Event date/time */}
        {event.date && (
          <text
            x={labelX}
            y={labelY + 5}
            textAnchor="middle"
            fontSize="10"
            fill="#666"
          >
            {event.date}
          </text>
        )}
        
        {/* Event emoji/icon */}
        {event.emoji && (
          <text
            x={labelX}
            y={labelY - 35}
            textAnchor="middle"
            fontSize="20"
          >
            {event.emoji}
          </text>
        )}
      </g>
    </g>
  );
};

export default TimelineMode;

