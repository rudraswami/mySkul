import React, { useMemo, useState } from 'react';
import DynamicSceneComposer from '../components/DynamicSceneComposer';
import TeachingCard from './TeachingCard';
import { Atom } from 'lucide-react';

export default function AtomicInteractiveCard({ visualData }) {
  const initialZ = 10;
  const initialN = 1;
  const [Z, setZ] = useState(initialZ);
  const [n, setN] = useState(initialN);
  const [zoom, setZoom] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [animZ, setAnimZ] = useState(initialZ);
  const [showTable, setShowTable] = useState(false);

  const zVal = isPlaying ? animZ : Z;

  const drivenVisual = useMemo(() => {
    if (!visualData?.scene_json) return visualData;
    const cloned = JSON.parse(JSON.stringify(visualData));
    const els = cloned.scene_json.elements || [];
    els.forEach(el => {
      if (el.type === 'slider' && el.id === 'Z') el.value = zVal;
      if (el.type === 'slider' && el.id === 'n') el.value = n;
    });
    return cloned;
  }, [visualData, zVal, n]);

  const reKey = `atom-${zVal}-${n}`;

  const handlePlay = () => {
    setIsPlaying(true);
    setAnimZ(1);
    const target = Z;
    let current = 1;
    const id = setInterval(() => {
      current += 1;
      setAnimZ(prev => (prev < target ? prev + 1 : prev));
      if (current >= target) {
        clearInterval(id);
        setTimeout(() => setIsPlaying(false), 200);
      }
    }, 220);
  };

  return (
    <TeachingCard title="Atomic Structure" subtitle="Electrons fill inner shells first (2, 8, 8, 2)" icon={<Atom className="w-7 h-7" />}>
      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-800 mb-3">
        <div className="min-w-[200px]">
          <div className="text-xs text-gray-600 mb-1">Element</div>
          <select value={Z} onChange={e => setZ(Number(e.target.value))} disabled={isPlaying} className="w-full border border-slate-300 rounded-md px-2 py-1 bg-white">
            {[['H',1],['He',2],['Li',3],['Be',4],['B',5],['C',6],['N',7],['O',8],['F',9],['Ne',10],['Na',11],['Mg',12],['Al',13],['Si',14],['P',15],['S',16],['Cl',17],['Ar',18],['K',19],['Ca',20]].map(([sym,val]) => (
              <option key={val} value={val}>{sym} ({val})</option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => setShowTable(v => !v)}
            className="mt-2 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-xs hover:bg-slate-50"
          >
            {showTable ? 'Hide' : 'Show'} Periodic Table (H–Ca)
          </button>
          {showTable && (
            <div className="mt-2 grid grid-cols-5 gap-1">
              {[
                ['H',1], ['He',2], ['Li',3], ['Be',4], ['B',5],
                ['C',6], ['N',7], ['O',8], ['F',9], ['Ne',10],
                ['Na',11], ['Mg',12], ['Al',13], ['Si',14], ['P',15],
                ['S',16], ['Cl',17], ['Ar',18], ['K',19], ['Ca',20],
              ].map(([sym,val]) => (
                <button
                  key={val}
                  onClick={() => { if (!isPlaying) setZ(val); }}
                  className={`rounded-md px-2 py-1 text-xs border ${Z===val ? 'bg-blue-600 text-white border-blue-700' : 'bg-white hover:bg-slate-50 border-slate-300'}`}
                  title={`${sym} (${val})`}
                >
                  {sym}
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="min-w-[220px]">
          <div className="text-xs text-gray-600 mb-1">Atomic Number Z: {zVal}</div>
          <input type="range" min={1} max={20} step={1} value={isPlaying ? zVal : Z} onChange={e => setZ(Number(e.target.value))} disabled={isPlaying} className="w-full" />
        </div>
        <div className="min-w-[220px]">
          <div className="text-xs text-gray-600 mb-1">Energy Level n: {n}</div>
          <input type="range" min={1} max={3} step={1} value={n} onChange={e => setN(Number(e.target.value))} disabled={isPlaying} className="w-full" />
        </div>
        <div className="min-w-[220px]">
          <div className="text-xs text-gray-600 mb-1">Zoom</div>
          <input type="range" min={0.9} max={1.3} step={0.02} value={zoom} onChange={e => setZoom(Number(e.target.value))} className="w-full" />
        </div>
        <div className="min-w-[120px]">
          <div className="text-xs text-gray-600 mb-1">Teach</div>
          <button onClick={handlePlay} disabled={isPlaying} className="px-3 py-1.5 rounded-md border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50">Play Fill</button>
        </div>
      </div>

      <div className="w-full rounded-2xl border border-slate-200 bg-white shadow-sm p-2">
        <DynamicSceneComposer key={reKey} visualData={drivenVisual} hideControls={true} userZoom={zoom} />
      </div>

      <div className="mt-3 text-xs text-gray-700">
        {(() => {
          const cap = { K: 2, L: 8, M: 8, N: 2 };
          const fill = { K: Math.min(zVal, cap.K), L: Math.max(0, Math.min(zVal - cap.K, cap.L)), M: Math.max(0, Math.min(zVal - cap.K - cap.L, cap.M)), N: Math.max(0, Math.min(zVal - cap.K - cap.L - cap.M, cap.N)) };
          return (
            <div className="space-y-2">
              <div className="bg-slate-50 border border-slate-200 rounded-md p-2">
                <div>Now filling: K {fill.K}/{cap.K} → L {fill.L}/{cap.L} → M {fill.M}/{cap.M}{cap.N?` → N ${fill.N}/${cap.N}`:''}</div>
              </div>
              <div className="flex items-center gap-3">
                {(['K','L','M','N']).map((shell, idx) => {
                  const value = fill[shell] || 0; const total = cap[shell] || 0;
                  const active = value > 0 || (idx === 0 && zVal > 0);
                  return (
                    <div key={shell} className="flex items-center gap-2">
                      <div className={`w-2.5 h-2.5 rounded-full ${active ? 'bg-blue-600' : 'bg-slate-300'}`} />
                      <div className="text-[11px]">
                        <span className="font-medium">{shell}</span> <span className="opacity-70">{value}/{total}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })()}
      </div>
    </TeachingCard>
  );
}

