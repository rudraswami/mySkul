/**
 * ⏱️ Timeline Template
 * ====================
 * 
 * Sequence of events visualization.
 * Historical events, process steps, evolution.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { COLORS, SUBJECT_THEMES } from '../primitives';

const TimelineTemplate = ({
  config = {},
  step = 0,
  subject = 'biology',
}) => {
  const {
    events = [
      { time: 'Step 1', title: 'Start', emoji: '🏁', color: '#3B82F6', description: 'Beginning' },
      { time: 'Step 2', title: 'Process', emoji: '⚙️', color: '#F59E0B', description: 'Middle' },
      { time: 'Step 3', title: 'End', emoji: '🎯', color: '#10B981', description: 'Complete' },
    ],
    title = 'Timeline',
    subtitle = 'Follow the sequence!',
    direction = 'horizontal', // horizontal, vertical
    memory_hook = 'Step by step, we get there! 🎯',
  } = config;

  const theme = SUBJECT_THEMES[subject] || SUBJECT_THEMES.biology;
  const numEvents = events.length;

  // Horizontal timeline positions
  const START_X = 70;
  const END_X = 430;
  const TIMELINE_Y = 200;
  const eventSpacing = (END_X - START_X) / (numEvents - 1 || 1);

  return (
    <g>
      {/* Title */}
      <motion.text
        x={250} y={30}
        fontSize={22}
        fontWeight="bold"
        textAnchor="middle"
        fill={COLORS.navy}
        fontFamily="'Caveat', cursive"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        ⏱️ {title}
      </motion.text>
      <motion.text
        x={250} y={52}
        fontSize={14}
        textAnchor="middle"
        fill={COLORS.chalkLight}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {subtitle}
      </motion.text>

      {/* Timeline line */}
      <motion.line
        x1={START_X - 20}
        y1={TIMELINE_Y}
        x2={END_X + 20}
        y2={TIMELINE_Y}
        stroke="#D1D5DB"
        strokeWidth={4}
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1 }}
      />

      {/* Arrow at end */}
      <motion.polygon
        points={`${END_X + 25},${TIMELINE_Y} ${END_X + 10},${TIMELINE_Y - 8} ${END_X + 10},${TIMELINE_Y + 8}`}
        fill="#D1D5DB"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      />

      {/* Progress line */}
      {step >= 1 && (
        <motion.line
          x1={START_X}
          y1={TIMELINE_Y}
          x2={START_X + Math.min(step - 1, numEvents - 1) * eventSpacing}
          y2={TIMELINE_Y}
          stroke={theme.primary}
          strokeWidth={4}
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.5 }}
        />
      )}

      {/* Events */}
      {events.map((event, i) => {
        const x = START_X + i * eventSpacing;
        const isActive = step >= i + 1;
        const isCurrent = step === i + 1;
        const isAlternate = i % 2 === 1; // Alternate above/below

        return (
          <motion.g
            key={i}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: isActive ? 1 : 0.4 }}
            transition={{ delay: 0.3 + i * 0.2, type: 'spring' }}
          >
            {/* Connector line */}
            <line
              x1={x}
              y1={TIMELINE_Y}
              x2={x}
              y2={isAlternate ? TIMELINE_Y + 40 : TIMELINE_Y - 40}
              stroke={event.color}
              strokeWidth={2}
              strokeDasharray={isActive ? 'none' : '4 2'}
            />

            {/* Node circle */}
            <motion.circle
              cx={x}
              cy={TIMELINE_Y}
              r={isActive ? 18 : 14}
              fill={isActive ? event.color : 'white'}
              stroke={event.color}
              strokeWidth={3}
              animate={isCurrent ? { scale: [1, 1.2, 1] } : {}}
              transition={isCurrent ? { repeat: Infinity, duration: 1 } : {}}
            />

            {/* Emoji inside node */}
            <text
              x={x}
              y={TIMELINE_Y + 5}
              fontSize={14}
              textAnchor="middle"
            >
              {isActive ? event.emoji : (i + 1)}
            </text>

            {/* Event card */}
            <g transform={`translate(${x}, ${isAlternate ? TIMELINE_Y + 50 : TIMELINE_Y - 110})`}>
              <rect
                x={-55}
                y={0}
                width={110}
                height={60}
                rx={10}
                fill={isActive ? event.color : 'white'}
                stroke={event.color}
                strokeWidth={2}
                opacity={isActive ? 1 : 0.7}
              />
              
              {/* Time label */}
              <text
                x={0}
                y={18}
                fontSize={10}
                textAnchor="middle"
                fill={isActive ? 'white' : event.color}
                opacity={0.8}
              >
                {event.time}
              </text>
              
              {/* Title */}
              <text
                x={0}
                y={35}
                fontSize={12}
                fontWeight="bold"
                textAnchor="middle"
                fill={isActive ? 'white' : '#374151'}
              >
                {event.title}
              </text>
              
              {/* Description */}
              <text
                x={0}
                y={50}
                fontSize={9}
                textAnchor="middle"
                fill={isActive ? 'rgba(255,255,255,0.8)' : '#636E72'}
              >
                {event.description}
              </text>
            </g>
          </motion.g>
        );
      })}

      {/* Memory Hook */}
      {step >= numEvents + 1 && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={100} y={365} width={300} height={38} rx={19} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={250} y={390} fontSize={14} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 {memory_hook}
          </text>
        </motion.g>
      )}
    </g>
  );
};

export default TimelineTemplate;

