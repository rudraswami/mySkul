import { useEffect, useState } from 'react';
import Lottie from 'lottie-react';

type VisualData = {
  type: 'animation' | 'scene' | 'svg';
  mode?: 'auto' | 'offer';
  lottie_file?: string;
  asset_url?: string;
  content?: string;
  caption?: string;
  persona?: string;
};

type VisualPlayerProps = {
  visual?: VisualData | null;
  autoPlay?: boolean;
};

const VisualPlayer = ({ visual, autoPlay = true }: VisualPlayerProps) => {
  const [animationData, setAnimationData] = useState<any>(null);

  useEffect(() => {
    let cancelled = false;
    const loadLottie = async () => {
      if (!visual?.lottie_file) return;
      try {
        const res = await fetch(visual.lottie_file);
        const data = await res.json();
        if (!cancelled) setAnimationData(data);
      } catch (err) {
        console.error('Failed to load Lottie asset', err);
      }
    };
    if (visual?.type === 'animation') {
      loadLottie();
    } else {
      setAnimationData(null);
    }
    return () => {
      cancelled = true;
    };
  }, [visual?.lottie_file, visual?.type]);

  if (!visual) return null;

  const caption = visual.caption || 'Visual explanation';

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-4">
      {visual.type === 'animation' && animationData ? (
        <Lottie animationData={animationData} autoplay={autoPlay} loop={autoPlay} />
      ) : visual.type === 'scene' && visual.asset_url ? (
        <img
          src={visual.asset_url}
          alt={caption}
          className="w-full h-auto rounded-xl"
          loading="lazy"
        />
      ) : visual.type === 'svg' && visual.content ? (
        <div
          className="w-full flex justify-center items-center"
          dangerouslySetInnerHTML={{ __html: visual.content }}
        />
      ) : (
        <div className="text-sm text-gray-600">{caption}</div>
      )}
      {caption && (
        <p className="text-xs text-gray-500 mt-3">{caption}</p>
      )}
    </div>
  );
};

export default VisualPlayer;
