import React, { useMemo, useState, useRef, useEffect } from 'react';
import Lottie from 'lottie-react';

/**
 * DynamicSceneComposer
 * Minimal renderer for visualData produced by a visual engine.
 * Supports inline SVG, base64 images, and a simple fallback.
 */
export default function DynamicSceneComposer({ visualData }) {
  if (!visualData) return null;

  // Render inline SVG content (back-compat)
  if (visualData.type === 'svg' && typeof visualData.content === 'string') {
    return (
      <div className="w-full overflow-auto" dangerouslySetInnerHTML={{ __html: visualData.content }} />
    );
  }

  // Render image content (back-compat)
  if (visualData.type === 'image' && visualData.src) {
    return (
      <img src={visualData.src} alt={visualData.alt || 'Concept visual'} className="max-w-full h-auto rounded" />
    );
  }

  // Render story scene from scene_json with simple frame navigation
  if (visualData.type === 'story_scene' && visualData.scene_json) {
    const { scene_json, interaction_flow = [], caption_text, interactivity } = visualData;
    const baseWidth = scene_json.canvas?.width || 480;
    const baseHeight = scene_json.canvas?.height || 270;
    const [frameIndex, setFrameIndex] = useState(0);
    const frame = interaction_flow[frameIndex] || { highlight: [] };
    const highlight = new Set(frame.highlight || []);
    const highlightOrder = useMemo(() => {
      const m = new Map();
      (frame.highlight || []).forEach((id, i) => m.set(id, i));
      return m;
    }, [frame.highlight]);
    const containerRef = useRef(null);

    const elements = useMemo(() => {
      return (scene_json.elements || []).filter(el => {
        const id = String(el?.id || '').toLowerCase();
        if (el?.debug || el?.role === 'debug_label') return false;
        if (id.includes('debug') || id.includes('meta_badge')) return false;
        return true;
      });
    }, [scene_json.elements]);

    // Drag-and-drop interactive support (optional, non-breaking)
    const tokens = elements.filter(e => e.type === 'token');
    const dropzones = elements.filter(e => e.type === 'dropzone');
    const sliders = elements.filter(e => e.type === 'slider');
    const [tokenPositions, setTokenPositions] = useState(() => {
      const pos = {};
      tokens.forEach(t => { pos[t.id] = { x: t.x, y: t.y }; });
      return pos;
    });
    const [drag, setDrag] = useState(null); // { id, offsetX, offsetY }
    const [assignments, setAssignments] = useState({}); // { dropzoneId: tokenId }
    const [sliderValues, setSliderValues] = useState(() => {
      const vals = {};
      sliders.forEach(s => { vals[s.id] = (typeof s.value === 'number' ? s.value : (s.min ?? 0)); });
      return vals;
    });
    const sliderMeta = useMemo(() => {
      const meta = {};
      sliders.forEach(s => { meta[s.id] = { min: s.min ?? 0, max: s.max ?? 1, step: s.step ?? 0.01 }; });
      return meta;
    }, [sliders]);
    const [labelOverrides, setLabelOverrides] = useState({}); // { elementId: text }
    const accepts = useMemo(() => {
      const map = {};
      (interactivity?.drop_accepts || []).forEach(rule => { map[rule.dropzoneId] = rule.accepts || []; });
      return map;
    }, [interactivity]);

    // Map flow ids to indices for tap-to-frame
    const frameIndexById = useMemo(() => {
      const m = {};
      (interaction_flow || []).forEach((f, idx) => { if (f && f.id) m[f.id] = idx; });
      return m;
    }, [interaction_flow]);

    const background = scene_json.canvas?.background || '#ffffff';
    const palette = scene_json.palette || {};

    const svg = useMemo(() => {
      const w = baseWidth;
      const h = baseHeight;
      const pal = palette;

      const renderEl = (el) => {
        const common = (extra = '') => `${extra} data-id='${el.id || ''}'`;
        switch (el.type) {
          case 'rect': {
            const active = highlight.has(el.id);
            let width = el.w;
            if (el.bindWidth && el.bindWidth.sliderId && sliderMeta[el.bindWidth.sliderId]) {
              const { min, max } = sliderMeta[el.bindWidth.sliderId];
              const val = sliderValues[el.bindWidth.sliderId] ?? min;
              const frac = (val - min) / (max - min || 1);
              const from = el.bindWidth.from ?? 0;
              const to = el.bindWidth.to ?? (el.w ?? 0);
              width = from + frac * to;
            }
            return `<rect x='${el.x}' y='${el.y}' width='${width}' height='${el.h}' fill='${el.fill || 'none'}' stroke='${active ? '#ff7043' : el.stroke || '#ccc'}' stroke-width='${active ? 3 : 1}' ${common()} />`;
          }
          case 'circle': {
            const active = highlight.has(el.id);
            return `<circle cx='${el.cx}' cy='${el.cy}' r='${el.r || 5}' fill='${el.fill || 'none'}' stroke='${active ? '#ff7043' : el.stroke || '#333'}' stroke-width='${active ? 3 : 1}' ${common()} />`;
          }
          case 'arrow': {
            const [x1, y1] = el.from; const [x2, y2] = el.to;
            const active = highlight.has(el.id);
            const color = active ? '#ff7043' : (el.color || '#333');
            const head = `M ${x2} ${y2} l -6 -4 l 0 8 z`;
            const cls = active ? "class='glow'" : '';
            const idx = highlightOrder.get(el.id) ?? 0;
            const delay = (0.2 * idx).toFixed(2);
            return `<g ${cls} ${common()}>
              <line x1='${x1}' y1='${y1}' x2='${x2}' y2='${y2}' stroke='${color}' stroke-width='2' stroke-dasharray='140' stroke-dashoffset='140' style='animation: draw .6s ${delay}s ease-out forwards'/>
              <path d='${head}' fill='${color}' style='opacity:0; animation: fadeIn .3s ${delay}s ease-out forwards'/>
            </g>`;
          }
          case 'motion': {
            const pts = (el.points || []).map(p => p.join(',')).join(' ');
            const active = highlight.has(el.id);
            const idx = highlightOrder.get(el.id) ?? 0;
            const delay = (0.2 * idx).toFixed(2);
            return `<polyline points='${pts}' fill='none' stroke='${active ? '#ff7043' : el.color || '#4caf50'}' stroke-width='2' stroke-dasharray='180' stroke-dashoffset='180' style='animation: draw .7s ${delay}s ease-out forwards' ${common()} />`;
          }
          case 'arc': {
            const [cx, cy] = el.c; const r = el.r || 20; const a0 = el.a0 || 0; const a1 = el.a1 || Math.PI / 2;
            const x0 = cx + r * Math.cos(a0); const y0 = cy + r * Math.sin(a0);
            const x1 = cx + r * Math.cos(a1); const y1 = cy + r * Math.sin(a1);
            const largeArc = Math.abs(a1 - a0) > Math.PI ? 1 : 0;
            const path = `M ${x0} ${y0} A ${r} ${r} 0 ${largeArc} 1 ${x1} ${y1}`;
            const active = highlight.has(el.id);
            const cls = active ? "class='glow'" : '';
            const idx = highlightOrder.get(el.id) ?? 0;
            const delay = (0.2 * idx).toFixed(2);
            return `<path ${cls} d='${path}' stroke='${active ? '#ff7043' : el.color || '#673ab7'}' stroke-width='2' fill='none' style='stroke-dasharray:160; stroke-dashoffset:160; animation: draw .6s ${delay}s ease-out forwards' ${common()} />`;
          }
          case 'label': {
            const text = labelOverrides[el.id] ?? el.text ?? '';
            const active = highlight.has(el.id);
            const cls = active ? "class='glow'" : '';
            const idx = highlightOrder.get(el.id) ?? 0;
            const delay = (0.15 * idx).toFixed(2);
            return `<text ${cls} x='${el.x}' y='${el.y}' font-size='12' fill='${el.color || '#333'}' style='opacity:0; animation: fadeIn .3s ${delay}s ease-out forwards' ${common()}>${escapeHtml(text)}</text>`;
          }
          case 'icon': {
            return `<text x='${el.x}' y='${el.y}' font-size='20' ${common()}>${escapeHtml(el.icon || '')}</text>`;
          }
          case 'grid': {
            const items = [];
            const rows = el.rows || 1; const cols = el.cols || 1; const [cw, ch] = el.cell || [40, 30];
            for (let r = 0; r < rows; r++) {
              for (let c = 0; c < cols; c++) {
                const x = el.x + c * cw; const y = el.y + r * ch;
                items.push(`<rect x='${x}' y='${y}' width='${cw - 6}' height='${ch - 6}' fill='#fff' stroke='#bbb' />`);
              }
            }
            return `<g ${common()}>${items.join('')}</g>`;
          }
          case 'pattern': {
            // Render simple rangoli if requested; otherwise fallback to dashed placeholder
            if (el.style === 'rangoli') {
              const saffron = pal.saffron || '#FF9933';
              const gold = pal.gold || '#FFD700';
              const green = pal.green || '#138808';
              const cx = (el.x || 0) + (el.w || 0) / 2;
              const cy = (el.y || 0) + (el.h || 0) / 2;
              const R = Math.min((el.w || 120), (el.h || 120)) * 0.42;
              const rPetal = R * 0.22;
              const rDot = R * 0.06;
              const petals = 8;
              const items = [];
              // Base rings
              items.push(`<circle cx='${cx}' cy='${cy}' r='${(R*0.55).toFixed(1)}' fill='none' stroke='${gold}' stroke-width='1.5'/>`);
              items.push(`<circle cx='${cx}' cy='${cy}' r='${(R*0.85).toFixed(1)}' fill='none' stroke='${saffron}' stroke-width='1.2' stroke-dasharray='4,3'/>`);
              // Petal circles
              for (let i = 0; i < petals; i++) {
                const a = (Math.PI * 2 * i) / petals;
                const px = cx + R * Math.cos(a);
                const py = cy + R * Math.sin(a);
                const fill = i % 2 === 0 ? saffron : green;
                items.push(`<circle cx='${px.toFixed(1)}' cy='${py.toFixed(1)}' r='${rPetal.toFixed(1)}' fill='${fill}' stroke='${gold}' stroke-width='1' opacity='0.9'/>`);
              }
              // Dots ring
              for (let i = 0; i < petals * 2; i++) {
                const a = (Math.PI * 2 * i) / (petals * 2);
                const px = cx + (R * 0.68) * Math.cos(a);
                const py = cy + (R * 0.68) * Math.sin(a);
                items.push(`<circle cx='${px.toFixed(1)}' cy='${py.toFixed(1)}' r='${rDot.toFixed(1)}' fill='${gold}' opacity='0.8'/>`);
              }
              // Cross lines
              for (let i = 0; i < petals / 2; i++) {
                const a = (Math.PI * 2 * i) / (petals/2);
                const x1 = cx + (R*0.2) * Math.cos(a);
                const y1 = cy + (R*0.2) * Math.sin(a);
                const x2 = cx + (R*0.9) * Math.cos(a);
                const y2 = cy + (R*0.9) * Math.sin(a);
                items.push(`<line x1='${x1.toFixed(1)}' y1='${y1.toFixed(1)}' x2='${x2.toFixed(1)}' y2='${y2.toFixed(1)}' stroke='${gold}' stroke-width='1' opacity='0.6'/>`);
              }
              // Center motif
              items.push(`<circle cx='${cx}' cy='${cy}' r='${(R*0.12).toFixed(1)}' fill='${gold}' opacity='0.9'/>`);
              items.push(`<circle cx='${cx}' cy='${cy}' r='${(R*0.20).toFixed(1)}' fill='none' stroke='${green}' stroke-width='1.2'/>`);
              return `<g ${common()}>${items.join('')}</g>`;
            }
            return `<rect x='${el.x}' y='${el.y}' width='${el.w}' height='${el.h}' fill='none' stroke='#aaa' stroke-dasharray='6,4' ${common()} />`;
          }
          case 'token': {
            // Token rendered in HTML overlay; draw a subtle placeholder target in SVG for alignment
            return `<rect x='${el.x - 4}' y='${el.y - 20}' width='${Math.max(40, (el.text||'').length*8)}' height='28' fill='none' stroke='#ddd' stroke-dasharray='3,3' ${common()} />`;
          }
          case 'dropzone': {
            const active = highlight.has(el.id);
            return `<rect x='${el.x}' y='${el.y}' width='${el.w || 120}' height='${el.h || 40}' fill='${el.fill || '#fff'}' stroke='${active ? '#ff7043' : (el.stroke || '#999')}' stroke-width='2' rx='6' ${common()} />` +
                   (el.text ? `<text x='${el.x + 10}' y='${el.y + 26}' font-size='14' fill='#555'>${escapeHtml(el.text)}</text>` : '');
          }
          default:
            return '';
        }
      };

      const content = elements.map(renderEl).join('');
      const style = `<style>
        @keyframes rgPulse{0%{transform:scale(1)}100%{transform:scale(1.15)}}
        .pulse{animation:rgPulse .9s ease-in-out infinite alternate; transform-origin:center}
        .glow{filter: drop-shadow(0 0 4px rgba(255,215,0,0.9))}
        @keyframes draw{to{stroke-dashoffset:0}}
        @keyframes fadeIn{from{opacity:0; transform:scale(0.98)} to{opacity:1; transform:scale(1)}}
      </style>`;
      const gradTop = pal.green || '#138808';
      const gradBottom = pal.saffron || '#FF9933';
      const defs = `<defs>
        <linearGradient id='bgGrad' x1='0' y1='0' x2='0' y2='1'>
          <stop offset='0%' stop-color='${gradTop}' stop-opacity='0.08'/>
          <stop offset='100%' stop-color='${gradBottom}' stop-opacity='0.03'/>
        </linearGradient>
      </defs>`;
      return `<svg width='${w}' height='${h}' viewBox='0 0 ${w} ${h}' xmlns='http://www.w3.org/2000/svg' style='animation: fadeIn .35s ease-out'>
        ${style}
        ${defs}
        <!-- Neutralize scene background to avoid dark/blue fills from theme palettes -->
        <rect x='0' y='0' width='${w}' height='${h}' fill='transparent' />
        ${content}
      </svg>`;
    }, [baseWidth, baseHeight, background, elements, frameIndex, JSON.stringify(sliderValues), JSON.stringify(labelOverrides), palette]);

    // Enrich placeholder labels using caption_text keywords (very lightweight heuristic)
    useEffect(() => {
      if (!caption_text) return;
      const text = String(caption_text);
      const parts = text.split(/[,.]|\s-\s|\s→\s|\s->\s/g).map(s => s.trim()).filter(Boolean);
      const phrases = [];
      for (const p of parts) {
        if (p.length < 4) continue;
        if (/(rise|fall|cause|effect|outcome|response|allied|axis|war|treaty|reform|impact|cycle|bond|energy|probability|expect|timeline)/i.test(p)) {
          phrases.push(p.replace(/^\w\w?:\s*/, ''));
        }
      }
      const uniq = Array.from(new Set(phrases)).slice(0, 4);
      if (!uniq.length) return;
      const updates = {};
      const ids = ['e1_t','e2_t','e3_t','e4_t'];
      ids.forEach((id, i) => { if (uniq[i]) updates[id] = String(uniq[i]).slice(0, 28); });
      if (Object.keys(updates).length) setLabelOverrides(prev => ({ ...updates, ...prev }));
    }, [caption_text]);

    const next = () => setFrameIndex(i => Math.min(i + 1, Math.max(0, interaction_flow.length - 1)));
    const prev = () => setFrameIndex(i => Math.max(i - 1, 0));

    // Lottie: load JSON for elements of type 'lottie' (optional)
    const lottieEls = elements.filter(e => e.type === 'lottie');
    const [lottieDataMap, setLottieDataMap] = useState({});
    useEffect(() => {
      let cancelled = false;
      (async () => {
        for (const el of lottieEls) {
          if (!el?.src || lottieDataMap[el.id]) continue;
          try {
            const res = await fetch(el.src, { cache: 'force-cache' });
            if (!res.ok) continue;
            const data = await res.json();
            if (!cancelled) setLottieDataMap(prev => ({ ...prev, [el.id]: data }));
          } catch {}
        }
      })();
      return () => { cancelled = true; };
    }, [lottieEls.map(e => e.src).join('|')]);

    // Pointer handlers for tokens (basic DnD without external libs)
    const onTokenDown = (e, id) => {
      const rect = containerRef.current?.getBoundingClientRect();
      const scale = Number(containerRef.current?.dataset?.scale || 1);
      const px = (e.clientX - rect.left) / (scale || 1);
      const py = (e.clientY - rect.top) / (scale || 1);
      const cur = tokenPositions[id];
      setDrag({ id, offsetX: px - cur.x, offsetY: py - cur.y });
      e.preventDefault();
    };
    const onPointerMove = (e) => {
      if (!drag) return;
      const rect = containerRef.current?.getBoundingClientRect();
      const scale = Number(containerRef.current?.dataset?.scale || 1);
      const x = (e.clientX - rect.left) / (scale || 1) - drag.offsetX;
      const y = (e.clientY - rect.top) / (scale || 1) - drag.offsetY;
      setTokenPositions(prev => ({ ...prev, [drag.id]: { x, y } }));
    };
    const onPointerUp = () => {
      if (!drag) return;
      const pos = tokenPositions[drag.id];
      // Hit test against dropzones; pick first matching
      const dz = dropzones.find(z => pos.x >= z.x && pos.x <= z.x + (z.w||120) && pos.y >= z.y && pos.y <= z.y + (z.h||40));
      if (dz) {
        setAssignments(prev => ({ ...prev, [dz.id]: drag.id }));
      }
      setDrag(null);
    };

    // Reset support (non-breaking): restore initial positions and values
    const initialTokenPositionsRef = useRef(tokenPositions);
    const initialSliderValuesRef = useRef(sliderValues);
    const handleReset = () => {
      setAssignments({});
      setTokenPositions(initialTokenPositionsRef.current || {});
      setSliderValues(initialSliderValuesRef.current || {});
      setLabelOverrides({});
      setFrameIndex(0);
      // reset confetti trigger if present
      try { setConfettiFired(false); } catch {}
    };

    // Slider bindings: update target labels from templates when slider changes
    const applySliderBindings = (sliderId, value) => {
      const sb = interactivity?.slider_bind?.bindings || [];
      const updates = {};
      for (const bind of sb) {
        if (bind.sliderId !== sliderId) continue;
        const targets = bind.targets || [];
        for (const t of targets) {
          const tpl = String(t.template || '');
          const v = Number(value);
          let out = tpl
            .replaceAll('{k}', String(v))
            .replaceAll('{t}', String(v))
            .replaceAll('{k-1}', String(v - 1))
            .replaceAll('{sin(k)}', Number.isFinite(v) ? Math.sin(v).toFixed(2) : '')
            .replaceAll('{sin(t)}', Number.isFinite(v) ? Math.sin(v).toFixed(2) : '');
          updates[t.elementId] = out;
        }
      }
      if (Object.keys(updates).length) setLabelOverrides(prev => ({ ...prev, ...updates }));
    };

    useEffect(() => {
      const move = (e) => onPointerMove(e);
      const up = () => onPointerUp();
      window.addEventListener('pointermove', move);
      window.addEventListener('pointerup', up);
      return () => {
        window.removeEventListener('pointermove', move);
        window.removeEventListener('pointerup', up);
      };
    });

    // Success detection for drag goals (used for confetti trigger)
    const isSolved = interactivity?.goal ? Object.keys(interactivity.goal).every(dz => (accepts[dz] || []).includes(assignments[dz])) : false;
    const [confettiFired, setConfettiFired] = useState(false);
    useEffect(() => {
      if (isSolved && !confettiFired) setConfettiFired(true);
    }, [isSolved, confettiFired]);

    // Auto-advance frames if requested (QA override via env allows global force)
    useEffect(() => {
      const raw = visualData.animation || {};
      const force = String(process.env.REACT_APP_FORCE_AUTO_ADVANCE || '').toLowerCase() === 'true';
      const effective = { ...raw };
      if (force) {
        effective.autoAdvance = true;
        const iv = Number(process.env.REACT_APP_AUTO_ADVANCE_INTERVAL_MS);
        if (!Number.isNaN(iv) && iv > 0) effective.intervalMs = iv;
      }
      if (!effective.autoAdvance || !interaction_flow.length) return;
      const interval = Math.max(300, Number(effective.intervalMs) || 1500);
      const id = setInterval(() => {
        setFrameIndex(i => (i < interaction_flow.length - 1 ? i + 1 : i));
      }, interval);
      return () => clearInterval(id);
    }, [visualData.animation, interaction_flow.length]);

    // Scaling: compute a scale factor to keep visuals compact and centered
    const [scale, setScale] = useState(1);
    useEffect(() => {
      const update = () => {
        const w = baseWidth;
        const h = baseHeight;
        const vw = (typeof window !== 'undefined' ? window.innerWidth : w) || w;
        const vh = (typeof window !== 'undefined' ? window.innerHeight : h) || h;
        const maxVisualH = Math.max(220, Math.min(vh * 0.45, 520));
        const availW = Math.min(vw * 0.82, 960);
        const s = Math.min(availW / w, maxVisualH / h);
        setScale(Number.isFinite(s) && s > 0 ? s : 1);
      };
      update();
      window.addEventListener('resize', update);
      return () => window.removeEventListener('resize', update);
    }, [baseWidth, baseHeight]);

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-end gap-2 text-xs text-gray-500">
          {interaction_flow.length > 0 && (
            <div className="flex items-center gap-2">
              <button onClick={prev} className="rounded border px-2 py-1 text-xs">Prev</button>
              <span>{frameIndex + 1}/{Math.max(1, interaction_flow.length)}</span>
              <button onClick={next} className="rounded border px-2 py-1 text-xs">Next</button>
              <button
                onClick={() => { setFrameIndex(0); try { setConfettiFired(false);} catch{}; }}
                className="rounded border px-2 py-1 text-xs"
              >
                Replay
              </button>
            </div>
          )}
        </div>
        <div className="mx-auto flex w-full max-w-4xl flex-col items-center gap-4">
          <div
            className="relative w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
            style={{ aspectRatio: `${baseWidth}/${baseHeight}`, maxHeight: '60vh' }}
          >
            <div
              ref={containerRef}
              data-scale={scale}
              style={{
                position: 'absolute',
                inset: 0,
                margin: 'auto',
                width: baseWidth,
                height: baseHeight,
                transform: `scale(${scale})`,
                transformOrigin: 'center'
              }}
            >
              <div dangerouslySetInnerHTML={{ __html: svg }} />
              {(interactivity?.show_reset || interactivity?.reset_button?.show) && (
                <button
                  onClick={handleReset}
                  aria-label="Reset"
                  style={{ position: 'absolute', right: 8, top: 8, padding: '6px 10px', background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: 6, boxShadow: '0 1px 2px rgba(0,0,0,0.06)', cursor: 'pointer' }}
                >
                  Reset
                </button>
              )}
              {/* HTML overlay for tokens and dropzones for interactivity */}
              {dropzones.map(z => {
                const assigned = assignments[z.id];
                const isCorrect = assigned ? (accepts[z.id] || []).includes(assigned) : null;
                const borderColor = isCorrect == null ? '#999' : (isCorrect ? '#16a34a' : '#dc2626');
                return (
                  <div key={z.id} style={{ position: 'absolute', left: z.x, top: z.y, width: z.w || 120, height: z.h || 40, pointerEvents: 'none', border: `2px dashed ${borderColor}`, borderRadius: 8 }} />
                );
              })}
              {tokens.map(t => {
                const p = tokenPositions[t.id] || { x: t.x, y: t.y };
                return (
                  <button
                    key={t.id}
                    onPointerDown={(e) => onTokenDown(e, t.id)}
                    style={{ position: 'absolute', left: p.x - 4, top: p.y - 20, padding: '4px 10px', background: '#ffffff', border: '1px solid #bbb', borderRadius: 6, cursor: 'grab' }}
                  >
                    {t.text || t.label || t.id}
                  </button>
                );
              })}
              {/* Tap-to-frame hotspots */}
              {(interactivity?.tap_to_frame || []).map((m, idx) => {
                const el = elements.find(e => e.id === m.elementId);
                if (!el) return null;
                let w = el.w || 48; let h = el.h || 28; let left = (el.x ?? 0) - 4; let top = (el.y ?? 0) - 20;
                if (typeof el.cx === 'number' && typeof el.cy === 'number') {
                  const r = el.r || 12; w = r * 2; h = r * 2; left = el.cx - r; top = el.cy - r;
                }
                const gotoIdx = frameIndexById[m.goto] ?? 0;
                return (
                  <button
                    key={`tap_${idx}_${m.elementId}`}
                    onClick={() => setFrameIndex(gotoIdx)}
                    aria-label={`focus ${m.goto}`}
                    style={{ position: 'absolute', left, top, width: w, height: h, background: 'transparent', border: '2px dashed rgba(99,102,241,0.25)', borderRadius: 8, cursor: 'pointer' }}
                  />
                );
              })}
              {sliders.map(s => {
                const val = sliderValues[s.id] ?? (s.min ?? 0);
                const onChange = (e) => {
                  const v = Number(e.target.value);
                  setSliderValues(prev => ({ ...prev, [s.id]: v }));
                  applySliderBindings(s.id, v);
                };
                return (
                  <input
                    key={s.id}
                    type="range"
                    min={s.min ?? 0}
                    max={s.max ?? 1}
                    step={s.step ?? 0.01}
                    value={val}
                    onChange={onChange}
                    aria-label={s.ariaLabel || s.id}
                    style={{ position: 'absolute', left: s.x, top: s.y, width: (s.w || 200), height: 32 }}
                  />
                );
              })}
              {lottieEls.map(el => {
                const data = lottieDataMap[el.id];
                if (!data) return null;
                const style = { position: 'absolute', left: el.x || 0, top: el.y || 0, width: el.w || 120, height: el.h || 120, pointerEvents: 'none' };
                const confettiId = interactivity?.confetti_on_success?.id;
                const confettiTargets = (interactivity?.confetti_on_success && interactivity.confetti_on_success.targets) || [];
                const explicitMatch = confettiId ? el.id === confettiId : false;
                const targetMatch = confettiTargets.length ? confettiTargets.includes(el.id) : false;
                const nameMatch = /confetti|fireworks/i.test(el.id || '');
                const shouldBoost = confettiFired && (explicitMatch || targetMatch || nameMatch);
                return (
                  <div key={el.id} style={style}>
                    <Lottie animationData={data} loop={el.loop !== false} autoplay={(el.autoplay !== false) || shouldBoost} style={{ width: '100%', height: '100%' }} />
                  </div>
                );
              })}
            </div>
          </div>
          {(caption_text || frame?.caption || interactivity?.goal) && (
            <div className="flex w-full flex-col items-center gap-2 text-center">
              {frame?.caption && (
                <p className="text-sm font-medium text-gray-700">{frame.caption}</p>
              )}
              {caption_text && (
                <p className="text-sm text-gray-600">{caption_text}</p>
              )}
              {interactivity?.goal && (
                <div className="text-sm">
                  {Object.keys(interactivity.goal).every(dz => (accepts[dz] || []).includes(assignments[dz])) ? (
                    <span className="text-green-700">Correct! {interactivity.success_text || ''}</span>
                  ) : (
                    <span className="text-gray-600">{interactivity.hint_text || ''}</span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Unknown type fallback
  return (
    <pre className="text-xs text-gray-500 bg-gray-50 p-2 rounded">{JSON.stringify(visualData, null, 2)}</pre>
  );
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
