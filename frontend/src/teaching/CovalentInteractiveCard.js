import React, { useMemo, useState } from 'react';
import DynamicSceneComposer from '../components/DynamicSceneComposer';
import TeachingCard from './TeachingCard';
import { Link2 } from 'lucide-react';
import covalentBonding from './scripts/covalentBonding';

export default function CovalentInteractiveCard() {
  const { scene } = covalentBonding({ complexity: 'simple' });
  const [zoom, setZoom] = useState(1);
  const [distance, setDistance] = useState(1); // 1 = far, 0 = close
  const [playing, setPlaying] = useState(false);

  const driven = useMemo(() => {
    if (!scene?.scene_json) return scene;
    const cloned = JSON.parse(JSON.stringify(scene));
    // Map 'energy' slider semantics from distance (inverse)
    const energy = 1 - Math.min(Math.max(distance, 0), 1);
    const els = cloned.scene_json.elements || [];
    const inter = cloned.interactivity || (cloned.interactivity = {});
    inter.sliders = (inter.sliders || []).map(s => s.id === 'energy' ? { ...s, value: energy } : s);
    return cloned;
  }, [scene, distance]);

  const handlePlay = () => {
    if (playing) return;
    setPlaying(true);
    let t = 1;
    const id = setInterval(() => {
      t -= 0.1;
      setDistance(v => (v > 0.05 ? Math.max(0, v - 0.1) : 0));
      if (t <= 0) {
        clearInterval(id);
        setTimeout(() => setPlaying(false), 200);
      }
    }, 180);
  };

  return (
    <TeachingCard title="Covalent Bonding" subtitle="Atoms share electron pairs; energy drops → stability rises">
      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-800 mb-3">
        <div className="min-w-[220px]">
          <div className="text-xs text-gray-600 mb-1">Atom Approach</div>
          <input type="range" min={0} max={1} step={0.05} value={1 - distance} onChange={e => setDistance(1 - Number(e.target.value))} disabled={playing} className="w-full" />
        </div>
        <div className="min-w-[220px]">
          <div className="text-xs text-gray-600 mb-1">Zoom</div>
          <input type="range" min={0.9} max={1.3} step={0.02} value={zoom} onChange={e => setZoom(Number(e.target.value))} className="w-full" />
        </div>
        <div className="min-w-[120px]">
          <div className="text-xs text-gray-600 mb-1">Teach</div>
          <button onClick={handlePlay} disabled={playing} className="px-3 py-1.5 rounded-md border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50">Play Bonding</button>
        </div>
      </div>

      <div className="w-full rounded-2xl border border-slate-200 bg-white shadow-sm p-2">
        <DynamicSceneComposer visualData={driven} hideControls={true} userZoom={zoom} />
      </div>
    </TeachingCard>
  );
}

