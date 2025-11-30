/**
 * 🏁 Race Template
 * ================
 * 
 * Comparison-based visualization for motion, force, velocity concepts.
 * Shows two objects competing to demonstrate physics principles.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { COLORS, SUBJECT_THEMES } from '../primitives';

const RaceTemplate = ({
  config = {},
  step = 0,
  subject = 'physics',
}) => {
  const {
    object_a = { type: 'auto_rickshaw', label: 'FAST', color: '#FF9933', speed: 20 },
    object_b = { type: 'auto_rickshaw', label: 'SLOW', color: '#3B82F6', speed: 10 },
    track_length = 100,
    unit = 'm',
    formula = 'v = d / t',
    memory_hook = 'Speed wins the race! 🏆',
    title = 'Race Challenge',
    subtitle = 'Which one is faster?',
  } = config;

  const theme = SUBJECT_THEMES[subject] || SUBJECT_THEMES.physics;
  
  const [objectAX, setObjectAX] = useState(100);
  const [objectBX, setObjectBX] = useState(100);
  const [time, setTime] = useState(0);
  const [isRacing, setIsRacing] = useState(false);
  const [raceComplete, setRaceComplete] = useState(false);

  const TRACK_START = 100;
  const TRACK_END = 420;
  const TRACK_LENGTH = TRACK_END - TRACK_START;

  // Race animation
  useEffect(() => {
    if (step >= 2 && !isRacing && !raceComplete) {
      setIsRacing(true);
      const startTime = Date.now();

      const animate = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        setTime(elapsed);

        const speedA = object_a.speed || 20;
        const speedB = object_b.speed || 10;

        const distA = Math.min(elapsed * speedA, track_length);
        const distB = Math.min(elapsed * speedB, track_length);

        const posA = TRACK_START + (distA / track_length) * TRACK_LENGTH;
        const posB = TRACK_START + (distB / track_length) * TRACK_LENGTH;

        setObjectAX(posA);
        setObjectBX(posB);

        if (elapsed < 5 && distA < track_length) {
          requestAnimationFrame(animate);
        } else {
          setIsRacing(false);
          setRaceComplete(true);
        }
      };

      requestAnimationFrame(animate);
    }
  }, [step, isRacing, raceComplete, object_a.speed, object_b.speed, track_length]);

  const distanceA = Math.min(time * (object_a.speed || 20), track_length);
  const distanceB = Math.min(time * (object_b.speed || 10), track_length);

  return (
    <g>
      {/* Title */}
      <motion.text
        x={250}
        y={30}
        fontSize={22}
        fontWeight="bold"
        textAnchor="middle"
        fill={COLORS.navy}
        fontFamily="'Caveat', cursive"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 30 }}
      >
        🏁 {title}
      </motion.text>
      <motion.text
        x={250}
        y={52}
        fontSize={14}
        textAnchor="middle"
        fill={COLORS.chalkLight}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {subtitle}
      </motion.text>

      {/* Scoreboard */}
      <motion.g
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.4 }}
      >
        <rect x={400} y={65} width={90} height={75} rx={10} fill="#1F2937" stroke={theme.primary} strokeWidth={2} />
        <text x={445} y={85} fontSize={11} textAnchor="middle" fill={theme.primary} fontWeight="bold">⏱️ TIME</text>
        <text x={445} y={115} fontSize={26} textAnchor="middle" fill="white" fontWeight="bold" fontFamily="monospace">
          {time.toFixed(1)}s
        </text>
        {isRacing && (
          <motion.text
            x={445} y={135}
            fontSize={10}
            textAnchor="middle"
            fill={COLORS.green}
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ repeat: Infinity, duration: 0.5 }}
          >
            RACING...
          </motion.text>
        )}
      </motion.g>

      {/* Object A Label */}
      <motion.g initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>
        <rect x={15} y={95} width={70} height={45} rx={6} fill={object_a.color} />
        <text x={50} y={113} fontSize={11} fontWeight="bold" textAnchor="middle" fill="white">{object_a.label}</text>
        <text x={50} y={130} fontSize={10} textAnchor="middle" fill="white">{distanceA.toFixed(0)}{unit}</text>
      </motion.g>

      {/* Object B Label */}
      <motion.g initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}>
        <rect x={15} y={190} width={70} height={45} rx={6} fill={object_b.color} />
        <text x={50} y={208} fontSize={11} fontWeight="bold" textAnchor="middle" fill="white">{object_b.label}</text>
        <text x={50} y={225} fontSize={10} textAnchor="middle" fill="white">{distanceB.toFixed(0)}{unit}</text>
      </motion.g>

      {/* Track A */}
      <motion.rect
        x={TRACK_START} y={105} width={TRACK_LENGTH} height={45} rx={5}
        fill="#374151" stroke="#1F2937" strokeWidth={2}
        initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} style={{ originX: 0 }}
      />
      {/* Road markings */}
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <rect key={`a-${i}`} x={TRACK_START + 30 + i * 55} y={125} width={35} height={5} rx={2} fill="#FCD34D" />
      ))}

      {/* Track B */}
      <motion.rect
        x={TRACK_START} y={200} width={TRACK_LENGTH} height={45} rx={5}
        fill="#374151" stroke="#1F2937" strokeWidth={2}
        initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 0.2 }} style={{ originX: 0 }}
      />
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <rect key={`b-${i}`} x={TRACK_START + 30 + i * 55} y={220} width={35} height={5} rx={2} fill="#FCD34D" />
      ))}

      {/* Distance markers */}
      <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
        <text x={TRACK_START} y={170} fontSize={9} textAnchor="middle" fill={COLORS.chalkLight}>0{unit}</text>
        <text x={(TRACK_START + TRACK_END) / 2} y={170} fontSize={9} textAnchor="middle" fill={COLORS.chalkLight}>{track_length / 2}{unit}</text>
        <text x={TRACK_END - 10} y={170} fontSize={9} textAnchor="middle" fill={COLORS.chalkLight}>{track_length}{unit}</text>
      </motion.g>

      {/* Object A */}
      <motion.g animate={{ x: objectAX - 100 }}>
        <g transform="translate(100, 120) scale(0.5)">
          <path d="M -30 0 L -30 -25 Q -25 -35 -10 -35 L 25 -35 Q 35 -35 35 -20 L 35 0 Z" fill={object_a.color} stroke="#1F2937" strokeWidth={2} />
          <circle cx={-15} cy={8} r={10} fill="#1F2937" />
          <circle cx={25} cy={8} r={10} fill="#1F2937" />
        </g>
        {isRacing && (
          <g>
            <rect x={85} y={95} width={35} height={16} rx={4} fill={object_a.color} />
            <text x={102} y={107} fontSize={9} textAnchor="middle" fill="white" fontWeight="bold">
              {(distanceA / (time || 0.1)).toFixed(0)}m/s
            </text>
          </g>
        )}
      </motion.g>

      {/* Object B */}
      <motion.g animate={{ x: objectBX - 100 }}>
        <g transform="translate(100, 215) scale(0.5)">
          <path d="M -30 0 L -30 -25 Q -25 -35 -10 -35 L 25 -35 Q 35 -35 35 -20 L 35 0 Z" fill={object_b.color} stroke="#1F2937" strokeWidth={2} />
          <circle cx={-15} cy={8} r={10} fill="#1F2937" />
          <circle cx={25} cy={8} r={10} fill="#1F2937" />
        </g>
        {isRacing && (
          <g>
            <rect x={85} y={190} width={35} height={16} rx={4} fill={object_b.color} />
            <text x={102} y={202} fontSize={9} textAnchor="middle" fill="white" fontWeight="bold">
              {(distanceB / (time || 0.1)).toFixed(0)}m/s
            </text>
          </g>
        )}
      </motion.g>

      {/* Finish line */}
      <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
        <line x1={TRACK_END} y1={100} x2={TRACK_END} y2={250} stroke="white" strokeWidth={4} strokeDasharray="8 4" />
        <text x={TRACK_END + 12} y={130} fontSize={18}>🏁</text>
        <text x={TRACK_END + 12} y={225} fontSize={18}>🏁</text>
      </motion.g>

      {/* Formula */}
      {step >= 3 && raceComplete && (
        <motion.g initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <rect x={90} y={265} width={320} height={55} rx={12} fill="#FEF3C7" stroke={theme.primary} strokeWidth={3} />
          <text x={250} y={288} fontSize={14} textAnchor="middle" fill={COLORS.navy} fontWeight="bold">
            {formula}
          </text>
          <text x={250} y={308} fontSize={12} textAnchor="middle" fill={COLORS.chalkLight}>
            {object_a.label}: {track_length}{unit} ÷ {time.toFixed(1)}s = {(track_length / time).toFixed(1)}m/s ✅
          </text>
        </motion.g>
      )}

      {/* Memory Hook */}
      {step >= 4 && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={100} y={335} width={300} height={38} rx={19} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={250} y={360} fontSize={14} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 {memory_hook}
          </text>
        </motion.g>
      )}
    </g>
  );
};

export default RaceTemplate;

