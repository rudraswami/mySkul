/**
 * useExistingVisualEngine
 * Lightweight adapter hook to pass through existing visual_data
 * without altering working behavior. Keeps NeuroSymbolicResponse stable
 * while enabling future replacement with a richer engine.
 */
import { useMemo } from 'react';
import { buildSceneFromMetaphor } from '../utils/svgGenerator';

/**
 * useExistingVisualEngine
 * Adapter that prefers backend-provided visual_data, but can synthesize
 * a dynamic scene from the current response fields (metaphor/practical_explanation/ask)
 * to replace static visuals. Backward compatible: returns null if nothing derivable.
 */
export function useExistingVisualEngine(visualData) {
  return useMemo(() => {
    // 1) If already structured scene data, use it as-is
    if (visualData && (visualData.scene_json || (visualData.type && visualData.generated))) {
      try {
        console.debug('[VISUAL_ENGINE] render_status=pass_through', {
          scene_present: Boolean(visualData.scene_json),
          type: visualData.type,
          generated: visualData.generated,
        });
      } catch {}
      return visualData;
    }

    // 2) If we have textual cues, synthesize a scene
    if (visualData && (visualData.metaphor || visualData.practical_explanation || visualData.ask)) {
      const seed =
        (typeof visualData.metaphor === 'string' && visualData.metaphor) ||
        (typeof visualData.practical_explanation === 'string' && visualData.practical_explanation) ||
        (typeof visualData.ask === 'string' && visualData.ask) ||
        '';

      // Theme passthrough (non-breaking): prefer explicit theme from visualData,
      // else allow QA override via REACT_APP_VISUAL_THEME. Guard to allowed set.
      const allowedThemes = new Set(['cricket', 'bollywood', 'cooking', 'festival']);
      const fromProp = (visualData && typeof visualData.theme === 'string') ? visualData.theme.toLowerCase().trim() : '';
      const fromEnv = (process.env.REACT_APP_VISUAL_THEME || '').toLowerCase().trim();
      const themeHint = allowedThemes.has(fromProp) ? fromProp : (allowedThemes.has(fromEnv) ? fromEnv : undefined);

      // Subject passthrough if present; default to 'general'
      const subjectHint = (visualData && (visualData.subject || visualData.domain || visualData.topic_subject)) || 'general';

      const scene = buildSceneFromMetaphor(seed, subjectHint, themeHint ? { theme: themeHint } : {});
      try {
        console.debug('[VISUAL_ENGINE] render_status=synthesized', {
          metaphor_name: seed?.slice(0, 40) || null,
          scene_json_elements: scene?.scene_json?.elements?.length || 0,
          symbolic_tags: (scene?.neuro_symbolic_map || []).map(m => m.concept),
          theme: themeHint || 'default',
          subject: subjectHint,
        });
      } catch {}
      return scene;
    }

    // 3) Nothing to render
    try {
      console.warn('[VISUAL_ENGINE] render_status=empty_input');
    } catch {}
    return null;
  }, [visualData]);
}
