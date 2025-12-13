/**
 * 🇮🇳 Cultural Metaphors
 * =======================
 * 
 * India-first metaphor system for relatable learning
 */

// Metaphor Database (Phase 8 - COMPLETE)
export { default as METAPHOR_DATABASE } from './MetaphorDatabase';
export {
  METAPHOR_CATEGORIES,
  getMetaphor,
  getMetaphorsByCategory,
  findMetaphorByKeyword,
  getConceptMapping,
  getSubstitution,
  getAllMetaphorIds,
  searchMetaphorsByConcept,
} from './MetaphorDatabase';

// Metaphor Mapper (Phase 8 - COMPLETE)
export { default as MetaphorMapper, MetaphorMapper as MetaphorMapperClass } from './MetaphorMapper';
export { createMetaphorMapper, applyMetaphor } from './MetaphorMapper';

// Asset Library (Phase 8 - COMPLETE)
export { default as SVG_ASSETS } from './AssetLibrary';
export {
  getAsset,
  getAssetDataUrl,
  renderAsset,
  getAllAssetIds,
  hasAsset,
} from './AssetLibrary';

// Default export
export { default } from './MetaphorMapper';
