/**
 * 🚀 REVOLUTIONARY SKETCH ENGINE V3.0 - THE BREAKTHROUGH
 * =======================================================
 * 
 * NOT just animations - VISUAL UNDERSTANDING
 * 
 * Core Philosophy:
 * - Show COMPARISON (fast vs slow, heavy vs light)
 * - Show LIVE VALUES changing (d, t, v updating)
 * - Create "AHA!" moments through visual revelation
 * - Tell a STORY that hooks students
 * - Make abstract concepts CONCRETE
 * 
 * What makes this DIFFERENT:
 * 1. COMPARISON MODE - Always show contrast
 * 2. LIVE CALCULATOR - Values update with animation
 * 3. CAUSE-EFFECT - See relationships visually
 * 4. DRAMATIC REVEALS - Build suspense
 * 5. INDIAN CONTEXT - Relatable scenarios
 */

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence, useAnimation } from 'framer-motion';

// ============ COLORS ============
const COLORS = {
  saffron: '#FF9933',
  green: '#138808',
  navy: '#000080',
  gold: '#FFD700',
  chalk: '#2D3436',
  chalkLight: '#636E72',
  paper: '#FFFBF0',
  paperLines: '#E8DCC8',
  highlight: '#FEF3C7',
  success: '#10B981',
  accent: '#8B5CF6',
  red: '#EF4444',
  blue: '#3B82F6',
  orange: '#F97316'
};

// ============ HAND-DRAWN PATH GENERATOR ============
const wobble = (value, amount = 2) => value + (Math.random() - 0.5) * amount;

const handDrawnLine = (x1, y1, x2, y2, segments = 8) => {
  let d = `M ${wobble(x1)} ${wobble(y1)}`;
  for (let i = 1; i <= segments; i++) {
    const t = i / segments;
    const x = x1 + (x2 - x1) * t;
    const y = y1 + (y2 - y1) * t;
    d += ` L ${wobble(x, 1.5)} ${wobble(y, 1.5)}`;
  }
  return d;
};

// ============ ANIMATED PATH ============
const AnimatedPath = ({ d, stroke, strokeWidth = 3, delay = 0, duration = 0.8, fill = 'none' }) => {
  const pathRef = useRef(null);
  const [length, setLength] = useState(500);
  
  useEffect(() => {
    if (pathRef.current) {
      setLength(pathRef.current.getTotalLength() || 500);
    }
  }, [d]);
  
  return (
    <motion.path
      ref={pathRef}
      d={d}
      stroke={stroke}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      fill={fill}
      initial={{ strokeDasharray: length, strokeDashoffset: length, opacity: 0 }}
      animate={{ strokeDashoffset: 0, opacity: 1 }}
      transition={{ delay, duration, ease: 'easeInOut' }}
    />
  );
};

// ============ HANDWRITTEN TEXT ============
const HandText = ({ children, x, y, size = 20, color = COLORS.chalk, delay = 0, weight = 'normal', anchor = 'middle' }) => {
  return (
    <motion.text
      x={x}
      y={y}
      fontSize={size}
      fontWeight={weight}
      textAnchor={anchor}
      fill={color}
      fontFamily="'Caveat', 'Patrick Hand', cursive"
      initial={{ opacity: 0, y: y + 10 }}
      animate={{ opacity: 1, y }}
      transition={{ delay, duration: 0.4 }}
    >
      {children}
    </motion.text>
  );
};

// ============ LIVE VALUE DISPLAY ============
const LiveValue = ({ x, y, label, value, unit, color = COLORS.navy, delay = 0 }) => {
  return (
    <motion.g
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, type: 'spring' }}
    >
      <rect
        x={x - 45}
        y={y - 22}
        width={90}
        height={44}
        rx={8}
        fill="white"
        stroke={color}
        strokeWidth={2}
      />
      <text x={x} y={y - 5} fontSize={11} textAnchor="middle" fill={COLORS.chalkLight} fontFamily="sans-serif">
        {label}
      </text>
      <motion.text
        x={x}
        y={y + 14}
        fontSize={18}
        fontWeight="bold"
        textAnchor="middle"
        fill={color}
        fontFamily="'Caveat', cursive"
        key={value}
        initial={{ scale: 1.3 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 500 }}
      >
        {value} {unit}
      </motion.text>
    </motion.g>
  );
};

// ============ AUTO RICKSHAW (PROPER) ============
const AutoRickshaw = ({ x, y, scale = 1, color = COLORS.saffron, label = '', showDriver = true }) => {
  return (
    <g transform={`translate(${x}, ${y}) scale(${scale})`}>
      {/* Body */}
      <path
        d="M -30 0 L -30 -25 Q -25 -35 -10 -35 L 25 -35 Q 35 -35 35 -20 L 35 0 Z"
        fill={color}
        stroke={color === COLORS.saffron ? '#D97706' : '#1D4ED8'}
        strokeWidth={2}
      />
      {/* Roof */}
      <path
        d="M -20 -35 L -15 -50 L 20 -50 L 25 -35"
        fill="#1F2937"
        stroke="#1F2937"
        strokeWidth={2}
      />
      {/* Front windshield */}
      <path
        d="M -28 -10 L -28 -25 L -12 -33 L -12 -10 Z"
        fill="#93C5FD"
        stroke="#60A5FA"
        strokeWidth={1}
      />
      {/* Wheels */}
      <circle cx={-15} cy={8} r={10} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={25} cy={8} r={10} fill="#1F2937" stroke="#374151" strokeWidth={3} />
      <circle cx={-15} cy={8} r={4} fill="#9CA3AF" />
      <circle cx={25} cy={8} r={4} fill="#9CA3AF" />
      {/* Driver */}
      {showDriver && (
        <>
          <circle cx={-20} cy={-22} r={6} fill="#FBBF24" />
          <circle cx={-20} cy={-24} r={3} fill="#FEF3C7" />
        </>
      )}
      {/* Label */}
      {label && (
        <text x={0} y={35} fontSize={14} textAnchor="middle" fill={COLORS.chalk} fontFamily="'Caveat', cursive" fontWeight="bold">
          {label}
        </text>
      )}
    </g>
  );
};

// ============ RACE TRACK ============
const RaceTrack = ({ y, startX, endX, markers = [0, 25, 50, 75, 100], delay = 0 }) => {
  return (
    <g>
      {/* Road */}
      <motion.rect
        x={startX}
        y={y - 30}
        width={endX - startX}
        height={60}
        fill="#374151"
        rx={5}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay, duration: 0.8 }}
        style={{ originX: 0 }}
      />
      {/* Road markings */}
      <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: delay + 0.5 }}>
        {[0, 1, 2, 3, 4, 5, 6].map((i) => (
          <rect
            key={i}
            x={startX + 30 + i * 50}
            y={y - 3}
            width={30}
            height={6}
            fill="#FCD34D"
            rx={2}
          />
        ))}
      </motion.g>
      {/* Distance markers */}
      <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: delay + 0.8 }}>
        {markers.map((m, i) => {
          const markerX = startX + ((endX - startX) * i) / (markers.length - 1);
          return (
            <g key={m}>
              <line x1={markerX} y1={y - 35} x2={markerX} y2={y - 45} stroke="white" strokeWidth={2} />
              <text x={markerX} y={y - 50} fontSize={12} textAnchor="middle" fill="white" fontFamily="sans-serif">
                {m}m
              </text>
            </g>
          );
        })}
      </motion.g>
    </g>
  );
};

// ============ STOPWATCH ============
const Stopwatch = ({ x, y, time, isRunning, color = COLORS.chalk }) => {
  return (
    <motion.g
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: 'spring', delay: 0.5 }}
    >
      {/* Watch body */}
      <circle cx={x} cy={y} r={35} fill="white" stroke={color} strokeWidth={3} />
      <circle cx={x} cy={y} r={30} fill="#F9FAFB" stroke="#E5E7EB" strokeWidth={1} />
      {/* Button */}
      <rect x={x - 5} y={y - 50} width={10} height={15} rx={3} fill={color} />
      {/* Time display */}
      <text x={x} y={y - 8} fontSize={10} textAnchor="middle" fill={COLORS.chalkLight} fontFamily="sans-serif">
        TIME
      </text>
      <motion.text
        x={x}
        y={y + 12}
        fontSize={22}
        fontWeight="bold"
        textAnchor="middle"
        fill={isRunning ? COLORS.green : color}
        fontFamily="monospace"
        key={time}
        animate={isRunning ? { scale: [1, 1.1, 1] } : {}}
        transition={{ duration: 0.3 }}
      >
        {time.toFixed(1)}s
      </motion.text>
      {/* Running indicator */}
      {isRunning && (
        <motion.circle
          cx={x + 20}
          cy={y - 20}
          r={5}
          fill={COLORS.green}
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ repeat: Infinity, duration: 0.5 }}
        />
      )}
    </motion.g>
  );
};

// ============ FORMULA REVEAL ============
const FormulaReveal = ({ x, y, delay = 0, values = {} }) => {
  const { d = '?', t = '?', v = '?' } = values;
  
  return (
    <motion.g
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
    >
      {/* Background */}
      <rect
        x={x - 120}
        y={y - 35}
        width={240}
        height={70}
        rx={12}
        fill={COLORS.highlight}
        stroke={COLORS.saffron}
        strokeWidth={3}
      />
      
      {/* Pulsing glow */}
      <motion.rect
        x={x - 125}
        y={y - 40}
        width={250}
        height={80}
        rx={15}
        fill="none"
        stroke={COLORS.gold}
        strokeWidth={2}
        animate={{ opacity: [0.3, 0.7, 0.3], scale: [1, 1.02, 1] }}
        transition={{ repeat: Infinity, duration: 2 }}
      />
      
      {/* Formula: v = d / t */}
      <text x={x - 80} y={y + 8} fontSize={28} fontWeight="bold" fill={COLORS.navy} fontFamily="'Caveat', cursive">
        v = 
      </text>
      
      {/* Fraction */}
      <text x={x + 10} y={y - 5} fontSize={24} fontWeight="bold" fill={COLORS.green} fontFamily="'Caveat', cursive" textAnchor="middle">
        {d}m
      </text>
      <line x1={x - 30} y1={y + 5} x2={x + 50} y2={y + 5} stroke={COLORS.chalk} strokeWidth={3} />
      <text x={x + 10} y={y + 28} fontSize={24} fontWeight="bold" fill={COLORS.blue} fontFamily="'Caveat', cursive" textAnchor="middle">
        {t}s
      </text>
      
      {/* Result */}
      <text x={x + 80} y={y + 8} fontSize={28} fontWeight="bold" fill={COLORS.saffron} fontFamily="'Caveat', cursive">
        = {v}
      </text>
    </motion.g>
  );
};

// ============ CELEBRATION ============
const Celebration = ({ cx, cy, delay = 0 }) => {
  const particles = useMemo(() => 
    Array.from({ length: 20 }).map((_, i) => ({
      angle: (i / 20) * Math.PI * 2,
      distance: 40 + Math.random() * 30,
      color: [COLORS.saffron, COLORS.green, COLORS.gold, '#FF6B6B', '#4ECDC4'][i % 5],
      size: 4 + Math.random() * 5,
      delay: i * 0.02
    })), []);
  
  return (
    <g>
      {particles.map((p, i) => (
        <motion.circle
          key={i}
          cx={cx}
          cy={cy}
          r={p.size}
          fill={p.color}
          initial={{ scale: 0, x: 0, y: 0, opacity: 1 }}
          animate={{
            scale: [0, 1.5, 0],
            x: Math.cos(p.angle) * p.distance,
            y: Math.sin(p.angle) * p.distance,
            opacity: [1, 1, 0]
          }}
          transition={{ delay: delay + p.delay, duration: 0.8 }}
        />
      ))}
      {/* Stars */}
      {['⭐', '🌟', '✨'].map((star, i) => (
        <motion.text
          key={star}
          x={cx + (i - 1) * 50}
          y={cy}
          fontSize={24}
          textAnchor="middle"
          initial={{ scale: 0, y: 0 }}
          animate={{ scale: 1.2, y: -40 - i * 10 }}
          transition={{ delay: delay + i * 0.1, type: 'spring', stiffness: 200, damping: 10 }}
        >
          {star}
        </motion.text>
      ))}
    </g>
  );
};

// ============ MEMORY HOOK BANNER (Clean Design) ============
const MemoryHook = ({ x, y, text, delay = 0 }) => {
  return (
    <motion.g
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay, type: 'spring', stiffness: 120 }}
    >
      {/* Clean rounded rectangle */}
      <rect
        x={x - 190}
        y={y - 18}
        width={380}
        height={36}
        rx={18}
        fill="#ECFDF5"
        stroke={COLORS.green}
        strokeWidth={2}
      />
      {/* Text centered */}
      <text 
        x={x} 
        y={y + 6} 
        fontSize={16} 
        fontWeight="bold" 
        textAnchor="middle" 
        fill="#065F46" 
        fontFamily="'Caveat', cursive"
      >
        {text}
      </text>
    </motion.g>
  );
};

// ============ MODERN STEP INDICATOR (No Numbers - Clean Dots) ============
const StepIndicator = ({ current, total, x, y }) => {
  const dotSpacing = 24;
  const totalWidth = (total - 1) * dotSpacing;
  const startX = x - totalWidth / 2;
  
  return (
    <g>
      {/* Progress bar background */}
      <rect
        x={startX - 8}
        y={y - 3}
        width={totalWidth + 16}
        height={6}
        rx={3}
        fill="#E5E7EB"
      />
      {/* Progress bar fill */}
      <motion.rect
        x={startX - 8}
        y={y - 3}
        width={(current / (total - 1)) * (totalWidth + 16)}
        height={6}
        rx={3}
        fill={COLORS.saffron}
        initial={{ width: 0 }}
        animate={{ width: (current / (total - 1)) * (totalWidth + 16) }}
        transition={{ duration: 0.5 }}
      />
      {/* Dots */}
      {Array.from({ length: total }).map((_, i) => (
        <motion.circle
          key={i}
          cx={startX + i * dotSpacing}
          cy={y}
          r={i === current ? 8 : i <= current ? 6 : 5}
          fill={i <= current ? COLORS.saffron : '#D1D5DB'}
          stroke={i === current ? 'white' : 'transparent'}
          strokeWidth={2}
          animate={i === current ? { scale: [1, 1.2, 1] } : {}}
          transition={{ repeat: i === current ? Infinity : 0, duration: 1.5 }}
        />
      ))}
    </g>
  );
};

// ============ VELOCITY SCENE - THE BREAKTHROUGH ============
const VelocityScene = ({ step, onStepChange }) => {
  const [fastAutoX, setFastAutoX] = useState(80);
  const [slowAutoX, setSlowAutoX] = useState(80);
  const [time, setTime] = useState(0);
  const [isRacing, setIsRacing] = useState(false);
  const [raceComplete, setRaceComplete] = useState(false);
  
  const TRACK_START = 80;
  const TRACK_END = 420;
  const TRACK_LENGTH = TRACK_END - TRACK_START; // 340px = 100m in our scale
  
  const fastSpeed = 20; // m/s (covers 100m in 5s)
  const slowSpeed = 10; // m/s (covers 100m in 10s)
  
  // Animation effect
  useEffect(() => {
    if (step >= 2 && !isRacing && !raceComplete) {
      setIsRacing(true);
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = (Date.now() - startTime) / 1000; // seconds
        setTime(elapsed);
        
        // Fast auto: 20 m/s means it takes 5s to cover 100m
        const fastDistance = Math.min(elapsed * fastSpeed, 100); // in meters
        const fastPosition = TRACK_START + (fastDistance / 100) * TRACK_LENGTH;
        setFastAutoX(fastPosition);
        
        // Slow auto: 10 m/s means it takes 10s to cover 100m
        // But we only run for 5s, so it covers 50m
        const slowDistance = Math.min(elapsed * slowSpeed, 100);
        const slowPosition = TRACK_START + (slowDistance / 100) * TRACK_LENGTH;
        setSlowAutoX(slowPosition);
        
        if (elapsed < 5) {
          requestAnimationFrame(animate);
        } else {
          setTime(5);
          setIsRacing(false);
          setRaceComplete(true);
        }
      };
      
      requestAnimationFrame(animate);
    }
  }, [step, isRacing, raceComplete]);
  
  // Calculate current values
  const fastDistance = Math.min(time * fastSpeed, 100);
  const slowDistance = Math.min(time * slowSpeed, 100);
  const fastVelocity = time > 0 ? (fastDistance / time).toFixed(0) : '?';
  const slowVelocity = time > 0 ? (slowDistance / time).toFixed(0) : '?';
  
  return (
    <g>
      {/* Dramatic Title */}
      <HandText x={250} y={28} size={22} color={COLORS.navy} weight="bold">
        🏁 Mumbai Auto Race Challenge!
      </HandText>
      <motion.text
        x={250} y={50}
        fontSize={13}
        textAnchor="middle"
        fill={COLORS.chalkLight}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        Two autos, same time... which one has MORE VELOCITY?
      </motion.text>
      
      {/* SCOREBOARD - Top Right */}
      <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4 }}>
        <rect x={400} y={65} width={90} height={80} rx={10} fill="#1F2937" stroke={COLORS.saffron} strokeWidth={2} />
        <text x={445} y={85} fontSize={11} textAnchor="middle" fill={COLORS.saffron} fontWeight="bold">⏱️ TIME</text>
        <text x={445} y={115} fontSize={28} textAnchor="middle" fill="white" fontWeight="bold" fontFamily="monospace">
          {time.toFixed(1)}s
        </text>
        {isRacing && (
          <motion.text
            x={445} y={138}
            fontSize={10}
            textAnchor="middle"
            fill={COLORS.green}
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ repeat: Infinity, duration: 0.5 }}
          >
            RACING...
          </motion.text>
        )}
        {raceComplete && (
          <text x={445} y={138} fontSize={10} textAnchor="middle" fill={COLORS.saffron}>FINISHED!</text>
        )}
      </motion.g>
      
      {/* Track Labels with Live Distance */}
      <motion.g initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>
        {/* Fast Auto Label */}
        <rect x={15} y={100} width={65} height={45} rx={6} fill={COLORS.saffron} />
        <text x={47} y={118} fontSize={11} fontWeight="bold" textAnchor="middle" fill="white">SAFFRON</text>
        <text x={47} y={135} fontSize={10} textAnchor="middle" fill="white">{fastDistance.toFixed(0)}m</text>
        
        {/* Slow Auto Label */}
        <rect x={15} y={195} width={65} height={45} rx={6} fill={COLORS.blue} />
        <text x={47} y={213} fontSize={11} fontWeight="bold" textAnchor="middle" fill="white">BLUE</text>
        <text x={47} y={230} fontSize={10} textAnchor="middle" fill="white">{slowDistance.toFixed(0)}m</text>
      </motion.g>
      
      {/* Track 1 - Fast Auto */}
      <RaceTrack y={125} startX={TRACK_START} endX={TRACK_END} delay={0.2} />
      
      {/* Track 2 - Slow Auto */}
      <RaceTrack y={220} startX={TRACK_START} endX={TRACK_END} delay={0.4} />
      
      {/* Distance markers */}
      <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
        <text x={TRACK_START} y={168} fontSize={9} textAnchor="middle" fill={COLORS.chalkLight}>0m</text>
        <text x={(TRACK_START + TRACK_END) / 2} y={168} fontSize={9} textAnchor="middle" fill={COLORS.chalkLight}>50m</text>
        <text x={TRACK_END - 10} y={168} fontSize={9} textAnchor="middle" fill={COLORS.chalkLight}>100m</text>
      </motion.g>
      
      {/* Fast Auto with speed bubble */}
      <motion.g animate={{ x: fastAutoX - 80 }}>
        <AutoRickshaw x={80} y={117} scale={0.65} color={COLORS.saffron} />
        {isRacing && (
          <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <rect x={75} y={93} width={35} height={16} rx={4} fill={COLORS.saffron} />
            <text x={92} y={105} fontSize={9} textAnchor="middle" fill="white" fontWeight="bold">
              {fastVelocity}m/s
            </text>
          </motion.g>
        )}
      </motion.g>
      
      {/* Slow Auto with speed bubble */}
      <motion.g animate={{ x: slowAutoX - 80 }}>
        <AutoRickshaw x={80} y={212} scale={0.65} color={COLORS.blue} />
        {isRacing && (
          <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <rect x={75} y={188} width={35} height={16} rx={4} fill={COLORS.blue} />
            <text x={92} y={200} fontSize={9} textAnchor="middle" fill="white" fontWeight="bold">
              {slowVelocity}m/s
            </text>
          </motion.g>
        )}
      </motion.g>
      
      {/* Finish Line */}
      <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
        <line x1={TRACK_END} y1={100} x2={TRACK_END} y2={255} stroke="white" strokeWidth={4} strokeDasharray="8 4" />
        <text x={390} y={125} fontSize={16}>🏁</text>
        <text x={390} y={220} fontSize={16}>🏁</text>
      </motion.g>
      
      {/* Step 3: Show Formula */}
      {step >= 3 && raceComplete && (
        <motion.g initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
          <rect x={70} y={260} width={320} height={60} rx={12} fill="#FEF3C7" stroke={COLORS.saffron} strokeWidth={3} />
          
          <text x={230} y={282} fontSize={13} textAnchor="middle" fill={COLORS.navy} fontWeight="bold">
            Velocity = Distance ÷ Time
          </text>
          
          <g transform="translate(95, 298)">
            <text fontSize={11} fill={COLORS.saffron} fontWeight="bold">Saffron: 100m ÷ 5s = </text>
            <text x={130} fontSize={13} fill={COLORS.saffron} fontWeight="bold">20 m/s ✅</text>
          </g>
          <g transform="translate(95, 315)">
            <text fontSize={11} fill={COLORS.blue} fontWeight="bold">Blue: 50m ÷ 5s = </text>
            <text x={100} fontSize={13} fill={COLORS.blue} fontWeight="bold">10 m/s</text>
          </g>
        </motion.g>
      )}
      
      {/* Step 4: Memory Hook */}
      {step >= 4 && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={80} y={330} width={300} height={38} rx={19} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={230} y={355} fontSize={13} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 v = d/t (More distance = More velocity!)
          </text>
        </motion.g>
      )}
      
      {/* Celebration when complete */}
      {step >= 4 && <Celebration cx={230} cy={180} delay={0.3} />}
    </g>
  );
};

// ============ FORCE SCENE - REVOLUTIONARY CRICKET METAPHOR ============
const ForceScene = ({ step }) => {
  const [cricketBallX, setCricketBallX] = useState(120);
  const [medicineBallX, setMedicineBallX] = useState(120);
  const [cricketSpeed, setCricketSpeed] = useState(0);
  const [medicineSpeed, setMedicineSpeed] = useState(0);
  const [showPush, setShowPush] = useState(false);
  const [isRacing, setIsRacing] = useState(false);
  
  // Cricket ball vs Medicine ball - same hit force!
  useEffect(() => {
    if (step >= 1) {
      setShowPush(true);
    }
    
    if (step >= 2 && !isRacing) {
      setIsRacing(true);
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        
        // Same Force (10N), different mass
        const F = 10; // Same force for both
        const cricketMass = 0.16; // 160g cricket ball
        const medicineMass = 3; // 3kg medicine ball
        
        const cricketAccel = F / cricketMass; // a = F/m = 62.5 m/s²
        const medicineAccel = F / medicineMass; // a = F/m = 3.3 m/s²
        
        // Distance = ½at²
        const cricketDist = 0.5 * cricketAccel * elapsed * elapsed * 0.8;
        const medicineDist = 0.5 * medicineAccel * elapsed * elapsed * 0.8;
        
        // Speed = at
        setCricketSpeed(Math.min(cricketAccel * elapsed, 99));
        setMedicineSpeed(Math.min(medicineAccel * elapsed, 99));
        
        setCricketBallX(120 + Math.min(cricketDist, 300));
        setMedicineBallX(120 + Math.min(medicineDist, 300));
        
        if (elapsed < 2.5) {
          requestAnimationFrame(animate);
        }
      };
      
      requestAnimationFrame(animate);
    }
  }, [step, isRacing]);
  
  return (
    <g>
      {/* Dramatic Title */}
      <HandText x={250} y={30} size={24} color={COLORS.navy} weight="bold">
        🏏 Same Push, Different Results!
      </HandText>
      
      {/* Story subtitle */}
      <motion.text
        x={250} y={55}
        fontSize={14}
        textAnchor="middle"
        fill={COLORS.chalkLight}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        What if Bumrah hits a cricket ball vs a medicine ball?
      </motion.text>
      
      {/* SCENE: Two tracks */}
      <g>
        {/* Cricket Ball Track */}
        <motion.rect 
          x={115} y={90} width={330} height={55} rx={8} 
          fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2}
          initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} 
          style={{ originX: 0 }}
        />
        
        {/* Medicine Ball Track */}
        <motion.rect 
          x={115} y={175} width={330} height={55} rx={8}
          fill="#FEF2F2" stroke={COLORS.red} strokeWidth={2}
          initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} 
          transition={{ delay: 0.2 }}
          style={{ originX: 0 }}
        />
        
        {/* Track Labels with Mass */}
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
          <text x={108} y={85} fontSize={12} textAnchor="end" fill={COLORS.green} fontWeight="bold">
            Cricket Ball
          </text>
          <text x={108} y={98} fontSize={10} textAnchor="end" fill={COLORS.chalkLight}>
            (160g = 0.16kg)
          </text>
          
          <text x={108} y={170} fontSize={12} textAnchor="end" fill={COLORS.red} fontWeight="bold">
            Medicine Ball
          </text>
          <text x={108} y={183} fontSize={10} textAnchor="end" fill={COLORS.chalkLight}>
            (3kg = heavy!)
          </text>
        </motion.g>
      </g>
      
      {/* ANIMATED HAND PUSHING */}
      {showPush && (
        <motion.g
          initial={{ x: -30, opacity: 0 }}
          animate={{ x: 0, opacity: step >= 2 ? 0 : 1 }}
          transition={{ duration: 0.5 }}
        >
          <text x={85} y={125} fontSize={30}>👊</text>
          <text x={85} y={210} fontSize={30}>👊</text>
          
          {/* Force arrows */}
          <motion.line x1={100} y1={117} x2={118} y2={117} stroke={COLORS.saffron} strokeWidth={4}
            initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} style={{ originX: 0 }} />
          <motion.line x1={100} y1={202} x2={118} y2={202} stroke={COLORS.saffron} strokeWidth={4}
            initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} style={{ originX: 0 }} />
          
          {/* Same Force label */}
          <motion.g initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.3 }}>
            <rect x={60} y={145} width={55} height={35} rx={6} fill={COLORS.saffron} />
            <text x={87} y={160} fontSize={11} textAnchor="middle" fill="white" fontWeight="bold">SAME</text>
            <text x={87} y={174} fontSize={11} textAnchor="middle" fill="white" fontWeight="bold">FORCE!</text>
          </motion.g>
        </motion.g>
      )}
      
      {/* CRICKET BALL - Small & Fast */}
      <motion.g animate={{ x: cricketBallX - 120 }}>
        <motion.circle 
          cx={120} cy={117} r={14}
          fill={COLORS.green}
          stroke="#059669" strokeWidth={2}
          animate={isRacing ? { scale: [1, 1.1, 1] } : {}}
          transition={{ repeat: Infinity, duration: 0.3 }}
        />
        <text x={120} y={121} fontSize={8} textAnchor="middle" fill="white" fontWeight="bold">🏏</text>
        
        {/* Speed indicator */}
        {step >= 2 && (
          <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <rect x={105} y={125} width={30} height={16} rx={3} fill={COLORS.green} />
            <text x={120} y={137} fontSize={9} textAnchor="middle" fill="white" fontWeight="bold">
              {cricketSpeed.toFixed(0)} m/s
            </text>
          </motion.g>
        )}
      </motion.g>
      
      {/* MEDICINE BALL - Big & Slow */}
      <motion.g animate={{ x: medicineBallX - 120 }}>
        <circle cx={120} cy={202} r={22} fill={COLORS.red} stroke="#B91C1C" strokeWidth={2} />
        <text x={120} y={207} fontSize={12} textAnchor="middle" fill="white" fontWeight="bold">3kg</text>
        
        {/* Speed indicator */}
        {step >= 2 && (
          <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <rect x={100} y={218} width={40} height={16} rx={3} fill={COLORS.red} />
            <text x={120} y={230} fontSize={9} textAnchor="middle" fill="white" fontWeight="bold">
              {medicineSpeed.toFixed(0)} m/s
            </text>
          </motion.g>
        )}
      </motion.g>
      
      {/* FINISH LINE */}
      <line x1={430} y1={85} x2={430} y2={235} stroke={COLORS.navy} strokeWidth={3} strokeDasharray="8 4" />
      <text x={445} y={160} fontSize={10} fill={COLORS.navy} fontWeight="bold" transform="rotate(90, 445, 160)">FINISH</text>
      
      {/* Step 3: Formula Reveal - Connected to visual */}
      {step >= 3 && (
        <motion.g initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <rect x={100} y={255} width={300} height={70} rx={12} fill="#FEF3C7" stroke={COLORS.saffron} strokeWidth={3} />
          
          {/* Formula breakdown */}
          <text x={250} y={278} fontSize={14} textAnchor="middle" fill={COLORS.navy} fontWeight="bold">
            Newton says: a = F ÷ m
          </text>
          
          {/* Visual formula */}
          <g transform="translate(130, 290)">
            <text fontSize={12} fill={COLORS.green} fontWeight="bold">Cricket: 10N ÷ 0.16kg = </text>
            <text x={165} fontSize={14} fill={COLORS.green} fontWeight="bold">62.5 m/s² 🚀</text>
          </g>
          <g transform="translate(130, 310)">
            <text fontSize={12} fill={COLORS.red} fontWeight="bold">Medicine: 10N ÷ 3kg = </text>
            <text x={155} fontSize={14} fill={COLORS.red} fontWeight="bold">3.3 m/s² 🐢</text>
          </g>
        </motion.g>
      )}
      
      {/* Step 4: Memory Hook - Indian Context */}
      {step >= 4 && (
        <motion.g initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={70} y={340} width={360} height={45} rx={22} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={250} y={368} fontSize={15} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 Light = Fast, Heavy = Lazy! (F = ma)
          </text>
        </motion.g>
      )}
      
      {step >= 4 && <Celebration cx={250} cy={150} delay={0.3} />}
    </g>
  );
};

// ============ GRAVITY SCENE ============
const GravityScene = ({ step }) => {
  const [featherY, setFeatherY] = useState(60);
  const [stoneY, setStoneY] = useState(60);
  const [isAnimating, setIsAnimating] = useState(false);
  const [showVacuum, setShowVacuum] = useState(false);
  
  useEffect(() => {
    if (step >= 2 && !isAnimating) {
      setIsAnimating(true);
      setShowVacuum(step >= 3);
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        
        // In vacuum (step 3+), both fall at same rate
        // In air (step 2), feather falls slower
        const g = 9.8;
        const stoneFall = 0.5 * g * elapsed * elapsed * 15;
        const featherFall = showVacuum ? stoneFall : 0.5 * g * elapsed * elapsed * 5;
        
        setStoneY(60 + Math.min(stoneFall, 200));
        setFeatherY(60 + Math.min(featherFall, 200));
        
        if (elapsed < 2) {
          requestAnimationFrame(animate);
        }
      };
      
      requestAnimationFrame(animate);
    }
  }, [step, isAnimating, showVacuum]);
  
  return (
    <g>
      {/* Dramatic Title */}
      <HandText x={250} y={28} size={22} color={COLORS.navy} weight="bold">
        🧪 Galileo's Mind-Blowing Discovery!
      </HandText>
      <motion.text
        x={250} y={50}
        fontSize={13}
        textAnchor="middle"
        fill={COLORS.chalkLight}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        Will Laddu and Roti fall at same speed? Let's test!
      </motion.text>
      
      {/* Two experiment zones */}
      <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
        {/* AIR Zone */}
        <rect x={60} y={65} width={175} height={190} rx={10} fill="#FEF3C7" stroke="#D97706" strokeWidth={2} />
        <rect x={60} y={65} width={175} height={28} rx={10} fill="#F59E0B" />
        <text x={147} y={84} fontSize={12} textAnchor="middle" fill="white" fontWeight="bold">🌬️ IN AIR</text>
        
        {/* VACUUM Zone */}
        <rect x={265} y={65} width={175} height={190} rx={10} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
        <rect x={265} y={65} width={175} height={28} rx={10} fill={COLORS.green} />
        <text x={352} y={84} fontSize={12} textAnchor="middle" fill="white" fontWeight="bold">🚀 NO AIR (Vacuum)</text>
      </motion.g>
      
      {/* Object labels */}
      <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
        <text x={107} y={110} fontSize={11} textAnchor="middle" fill={COLORS.chalkLight} fontWeight="bold">Feather</text>
        <text x={190} y={110} fontSize={11} textAnchor="middle" fill={COLORS.chalkLight} fontWeight="bold">Stone</text>
        <text x={312} y={110} fontSize={11} textAnchor="middle" fill={COLORS.chalkLight} fontWeight="bold">Feather</text>
        <text x={395} y={110} fontSize={11} textAnchor="middle" fill={COLORS.chalkLight} fontWeight="bold">Stone</text>
      </motion.g>
      
      {/* AIR Zone - Feather (slow) */}
      <motion.g animate={{ y: Math.min((featherY - 60) * 0.4, 110) }}>
        <text x={107} y={125} fontSize={28} textAnchor="middle">🪶</text>
      </motion.g>
      
      {/* AIR Zone - Stone (fast) */}
      <motion.g animate={{ y: Math.min(stoneY - 60, 110) }}>
        <circle cx={190} cy={130} r={16} fill="#6B7280" stroke="#4B5563" strokeWidth={2} />
        <text x={190} y={135} fontSize={9} textAnchor="middle" fill="white" fontWeight="bold">5kg</text>
      </motion.g>
      
      {/* VACUUM Zone - Both fall together! */}
      <motion.g animate={{ y: showVacuum ? Math.min(stoneY - 60, 110) : 0 }}>
        <text x={312} y={125} fontSize={28} textAnchor="middle">🪶</text>
      </motion.g>
      
      <motion.g animate={{ y: showVacuum ? Math.min(stoneY - 60, 110) : 0 }}>
        <circle cx={395} cy={130} r={16} fill="#6B7280" stroke="#4B5563" strokeWidth={2} />
        <text x={395} y={135} fontSize={9} textAnchor="middle" fill="white" fontWeight="bold">5kg</text>
      </motion.g>
      
      {/* Ground lines */}
      <line x1={65} y1={250} x2={230} y2={250} stroke={COLORS.chalk} strokeWidth={3} />
      <line x1={270} y1={250} x2={435} y2={250} stroke={COLORS.chalk} strokeWidth={3} />
      
      {/* Result Labels */}
      {step >= 2 && (
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <text x={147} y={268} fontSize={11} textAnchor="middle" fill="#D97706" fontWeight="bold">
            Stone wins! ⬇️
          </text>
          <text x={352} y={268} fontSize={11} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            SAME TIME! 🤯
          </text>
        </motion.g>
      )}
      
      {/* Formula */}
      {step >= 3 && (
        <motion.g initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <rect x={80} y={280} width={340} height={55} rx={12} fill="#FEF3C7" stroke={COLORS.saffron} strokeWidth={3} />
          <text x={250} y={302} fontSize={13} textAnchor="middle" fill={COLORS.navy} fontWeight="bold">
            Without air resistance:
          </text>
          <text x={250} y={324} fontSize={20} fontWeight="bold" textAnchor="middle" fill={COLORS.navy} fontFamily="'Caveat', cursive">
            ALL objects fall at g = 9.8 m/s² 🌍
          </text>
        </motion.g>
      )}
      
      {/* Memory hook */}
      {step >= 4 && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={80} y={345} width={340} height={40} rx={20} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={250} y={371} fontSize={14} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 In vacuum, elephant = ant = same fall speed!
          </text>
        </motion.g>
      )}
      
      {step >= 4 && <Celebration cx={250} cy={180} delay={0.3} />}
    </g>
  );
};

// ============ PHOTOSYNTHESIS SCENE (Compact Layout) ============
const PhotosynthesisScene = ({ step }) => {
  const [sunRays, setSunRays] = useState(false);
  const [waterFlow, setWaterFlow] = useState(false);
  const [co2Flow, setCo2Flow] = useState(false);
  const [glucoseGlow, setGlucoseGlow] = useState(false);
  const [o2Bubbles, setO2Bubbles] = useState(false);
  
  useEffect(() => {
    if (step >= 1) setSunRays(true);
    if (step >= 2) {
      setWaterFlow(true);
      setCo2Flow(true);
    }
    if (step >= 3) {
      setGlucoseGlow(true);
      setO2Bubbles(true);
    }
  }, [step]);
  
  return (
    <g>
      {/* Dramatic Title */}
      <HandText x={250} y={28} size={20} color={COLORS.navy} weight="bold">
        🌿 How Plants Cook Their Own Food!
      </HandText>
      <motion.text
        x={250} y={48}
        fontSize={12}
        textAnchor="middle"
        fill={COLORS.chalkLight}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        Just like Mom's kitchen, but with sunlight! ☀️
      </motion.text>
      
      {/* INPUT SIDE - Left Panel */}
      <motion.g initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
        <rect x={30} y={65} width={100} height={170} rx={10} fill="#E0F2FE" stroke={COLORS.blue} strokeWidth={2} />
        <rect x={30} y={65} width={100} height={25} rx={10} fill={COLORS.blue} />
        <text x={80} y={82} fontSize={11} textAnchor="middle" fill="white" fontWeight="bold">📥 INPUTS</text>
        
        {/* Sun Energy */}
        {sunRays && (
          <motion.g initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', delay: 0.3 }}>
            <circle cx={80} cy={110} r={22} fill={COLORS.gold} />
            <text x={80} y={115} fontSize={18} textAnchor="middle">☀️</text>
            <text x={80} y={145} fontSize={10} textAnchor="middle" fill={COLORS.gold} fontWeight="bold">Sunlight</text>
          </motion.g>
        )}
        
        {/* Water */}
        {waterFlow && (
          <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.5 }}>
            <rect x={45} y={155} width={70} height={30} rx={5} fill="white" stroke={COLORS.blue} strokeWidth={1} />
            <text x={80} y={175} fontSize={14} textAnchor="middle">💧</text>
            <text x={80} y={195} fontSize={9} textAnchor="middle" fill={COLORS.blue} fontWeight="bold">H₂O (Water)</text>
          </motion.g>
        )}
        
        {/* CO2 */}
        {co2Flow && (
          <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.7 }}>
            <rect x={45} y={205} width={70} height={25} rx={5} fill="white" stroke="#6B7280" strokeWidth={1} />
            <text x={80} y={222} fontSize={11} textAnchor="middle" fill="#6B7280" fontWeight="bold">CO₂</text>
          </motion.g>
        )}
      </motion.g>
      
      {/* CENTER - The Plant Factory */}
      <motion.g initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: 0.4 }}>
        {/* Factory box */}
        <rect x={150} y={80} width={150} height={150} rx={15} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={3} />
        
        {/* Factory label */}
        <rect x={175} y={70} width={100} height={22} rx={6} fill={COLORS.green} />
        <text x={225} y={85} fontSize={10} textAnchor="middle" fill="white" fontWeight="bold">🏭 LEAF FACTORY</text>
        
        {/* Chlorophyll cells */}
        <g transform="translate(225, 155)">
          {[[-30, -20], [30, -20], [0, 15], [-25, 25], [25, 25]].map(([cx, cy], i) => (
            <motion.circle
              key={i}
              cx={cx}
              cy={cy}
              r={12}
              fill="#22C55E"
              stroke="#15803D"
              strokeWidth={2}
              animate={glucoseGlow ? { 
                scale: [1, 1.15, 1],
                fill: ['#22C55E', '#FBBF24', '#22C55E']
              } : {}}
              transition={{ repeat: Infinity, duration: 1.5, delay: i * 0.2 }}
            />
          ))}
          <text x={0} y={-5} fontSize={9} textAnchor="middle" fill="#15803D" fontWeight="bold">Chlorophyll</text>
        </g>
        
        {/* Magic happening indicator */}
        {glucoseGlow && (
          <motion.text
            x={225} y={215}
            fontSize={16}
            textAnchor="middle"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 1 }}
          >
            ⚡
          </motion.text>
        )}
      </motion.g>
      
      {/* Animated arrows - Inputs to Factory */}
      {sunRays && (
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <motion.line x1={130} y1={120} x2={148} y2={130} stroke={COLORS.gold} strokeWidth={3}
            initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 0.3 }} />
          <motion.line x1={130} y1={175} x2={148} y2={160} stroke={COLORS.blue} strokeWidth={2}
            initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 0.5 }} />
        </motion.g>
      )}
      
      {/* OUTPUT SIDE - Right Panel */}
      <motion.g initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.6 }}>
        <rect x={320} y={65} width={115} height={170} rx={10} fill="#FEF3C7" stroke={COLORS.saffron} strokeWidth={2} />
        <rect x={320} y={65} width={115} height={25} rx={10} fill={COLORS.saffron} />
        <text x={377} y={82} fontSize={11} textAnchor="middle" fill="white" fontWeight="bold">📤 OUTPUTS</text>
        
        {/* Glucose - Food! */}
        {glucoseGlow && (
          <motion.g initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', delay: 0.8 }}>
            <rect x={335} y={100} width={85} height={55} rx={8} fill="white" stroke={COLORS.saffron} strokeWidth={2} />
            <text x={377} y={120} fontSize={18} textAnchor="middle">🍬</text>
            <text x={377} y={140} fontSize={12} fontWeight="bold" textAnchor="middle" fill={COLORS.saffron}>
              C₆H₁₂O₆
            </text>
            <text x={377} y={152} fontSize={8} textAnchor="middle" fill={COLORS.chalkLight}>(Glucose = Food!)</text>
          </motion.g>
        )}
        
        {/* Oxygen bubbles */}
        {o2Bubbles && (
          <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }}>
            <rect x={335} y={165} width={85} height={55} rx={8} fill="white" stroke={COLORS.blue} strokeWidth={2} />
            <g>
              {[0, 1, 2].map((i) => (
                <motion.circle
                  key={i}
                  cx={360 + i * 18}
                  cy={190}
                  r={8}
                  fill="#BFDBFE"
                  stroke={COLORS.blue}
                  strokeWidth={1}
                  animate={{ y: [0, -8, 0], scale: [1, 1.1, 1] }}
                  transition={{ repeat: Infinity, duration: 1.5, delay: i * 0.3 }}
                />
              ))}
            </g>
            <text x={377} y={215} fontSize={10} textAnchor="middle" fill={COLORS.blue} fontWeight="bold">O₂ (Oxygen)</text>
          </motion.g>
        )}
      </motion.g>
      
      {/* Arrow from factory to output */}
      {glucoseGlow && (
        <motion.line x1={302} y1={155} x2={318} y2={155} stroke={COLORS.saffron} strokeWidth={3}
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 0.7 }} />
      )}
      
      {/* Formula - Clean banner at bottom */}
      {step >= 3 && (
        <motion.g initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
          <rect x={50} y={250} width={350} height={40} rx={10} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={225} y={276} fontSize={14} fontWeight="bold" textAnchor="middle" fill={COLORS.green} fontFamily="'Caveat', cursive">
            6CO₂ + 6H₂O + Light → C₆H₁₂O₆ + 6O₂
          </text>
        </motion.g>
      )}
      
      {/* Memory hook */}
      {step >= 4 && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={70} y={300} width={310} height={38} rx={19} fill="#FEF3C7" stroke={COLORS.saffron} strokeWidth={2} />
          <text x={225} y={325} fontSize={13} textAnchor="middle" fill={COLORS.saffron} fontWeight="bold">
            💡 Sunlight + Water + CO₂ = Plant's Lunch! 🥗
          </text>
        </motion.g>
      )}
    </g>
  );
};

// ============ SCENE SELECTOR ============
const getSceneComponent = (concept) => {
  const conceptLower = concept?.toLowerCase() || '';
  
  // Physics concepts
  if (['velocity', 'speed', 'motion', 'distance', 'displacement', 'kinematics'].some(k => conceptLower.includes(k))) {
    return VelocityScene;
  }
  
  if (['force', 'newton', 'acceleration', 'mass', 'inertia', 'friction', 'push', 'pull', 'f=ma'].some(k => conceptLower.includes(k))) {
    return ForceScene;
  }
  
  if (['gravity', 'fall', 'weight', 'freefall', 'galileo', 'g=9.8'].some(k => conceptLower.includes(k))) {
    return GravityScene;
  }
  
  // Biology concepts
  if (['photosynthesis', 'plant', 'chlorophyll', 'glucose', 'leaves', 'food making'].some(k => conceptLower.includes(k))) {
    return PhotosynthesisScene;
  }
  
  // Default to VelocityScene for unknown concepts
  return VelocityScene;
};

// ============ MAIN COMPONENT ============
const RevolutionarySketch = ({ 
  concept = 'velocity',
  subject = 'physics',
  question = '',
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const totalSteps = 5;
  
  // Auto-advance steps
  useEffect(() => {
    if (!isPlaying || currentStep >= totalSteps) return;
    
    const durations = [1500, 2500, 3500, 2500, 2000];
    const timer = setTimeout(() => {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }, durations[currentStep] || 2000);
    
    return () => clearTimeout(timer);
  }, [currentStep, isPlaying, totalSteps]);
  
  const handleReplay = useCallback(() => {
    setCurrentStep(0);
    setIsPlaying(true);
  }, []);
  
  const SceneComponent = getSceneComponent(concept);
  
  // Get concept title
  const conceptTitles = {
    'velocity': { en: 'Velocity', hi: 'वेग' },
    'speed': { en: 'Speed', hi: 'चाल' },
    'motion': { en: 'Motion', hi: 'गति' },
    'force': { en: 'Force', hi: 'बल' },
    'gravity': { en: 'Gravity', hi: 'गुरुत्वाकर्षण' },
    'photosynthesis': { en: 'Photosynthesis', hi: 'प्रकाश संश्लेषण' }
  };
  
  const title = conceptTitles[concept?.toLowerCase()] || { en: concept, hi: '' };
  
  return (
    <div className="revolutionary-sketch rounded-2xl overflow-hidden shadow-2xl border-2 border-orange-300">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500 px-5 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🎬</span>
          <div>
            <span className="font-bold text-white text-lg">Watch & Learn</span>
            {title.hi && (
              <span className="ml-2 text-white/80 text-sm">({title.hi})</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="bg-white/30 backdrop-blur-sm px-4 py-1.5 rounded-full text-white text-sm font-bold">
            {title.en}
          </span>
          <button
            onClick={handleReplay}
            className="p-2 bg-white/30 rounded-full hover:bg-white/50 transition-all"
            title="Replay"
          >
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Main Canvas - Larger for better viewing */}
      <svg
        viewBox="0 0 500 450"
        className="w-full"
        style={{ 
          minHeight: '450px',
          background: `linear-gradient(180deg, ${COLORS.paper} 0%, #FEF3C7 100%)`
        }}
      >
        {/* Background grid pattern */}
        <defs>
          <pattern id="sketchPaper" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke={COLORS.paperLines} strokeWidth="0.5" opacity="0.5"/>
          </pattern>
        </defs>
        <rect width="500" height="450" fill="url(#sketchPaper)"/>
        
        {/* Scene Content */}
        <SceneComponent step={currentStep} onStepChange={setCurrentStep} />
      </svg>
      
      {/* Footer - Clean minimal design */}
      <div className="bg-gradient-to-r from-emerald-50 to-teal-50 px-5 py-2.5 flex items-center justify-between border-t border-emerald-200">
        <div className="flex items-center gap-2">
          {currentStep >= totalSteps ? (
            <motion.div 
              initial={{ scale: 0 }} 
              animate={{ scale: 1 }} 
              className="flex items-center gap-2 text-emerald-600"
            >
              <span className="text-lg">✅</span>
              <span className="font-medium text-sm">Complete!</span>
            </motion.div>
          ) : (
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
              <span className="text-emerald-600 text-sm">Playing...</span>
            </div>
          )}
        </div>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleReplay}
          className="px-4 py-1.5 bg-emerald-500 text-white text-sm font-medium rounded-full hover:bg-emerald-600 transition-all flex items-center gap-1.5 shadow-md"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Replay
        </motion.button>
      </div>
    </div>
  );
};

export default RevolutionarySketch;
