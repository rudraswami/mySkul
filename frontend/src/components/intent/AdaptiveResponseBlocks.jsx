import React, { useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import { Heart, GraduationCap, GitBranch, GitMerge, Balance, ArrowRight, Sparkles } from 'lucide-react';
import SemanticAIResponse from '../SemanticAIResponse';
import VisualPlayer from './VisualPlayer';

/**
 * Normalize structured blocks coming from backend.
 * Ensures every entry has a type + data pair for rendering.
 */
const useNormalizedBlocks = (structuredBlocks) =>
  useMemo(() => {
    if (!structuredBlocks || typeof structuredBlocks !== 'object') {
      return [];
    }
    return Object.entries(structuredBlocks)
      .map(([key, value]) => {
        if (!value) return null;
        if (value.type) return { type: value.type, data: value };
        const mappedType = ({
          definition_block: 'definition_card',
          compare_table: 'compare_grid',
        })[key] || key;
        return { type: mappedType, data: value };
      })
      .filter(Boolean);
  }, [structuredBlocks]);

export const MentorBlock = ({ mentor, timestamp }) => {
  if (!mentor || (!mentor.response && !mentor.raw_text)) {
    return null;
  }
  return (
    <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-100 rounded-2xl shadow-sm p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Heart className="h-5 w-5 text-purple-500" />
          <div>
            <p className="font-semibold text-purple-900">Mentor Guidance</p>
            <p className="text-xs text-purple-600">Friendly first layer</p>
          </div>
        </div>
        {timestamp && (
          <span className="text-xs text-purple-600 flex items-center gap-1">
            <Sparkles className="h-3 w-3" />
            {timestamp}
          </span>
        )}
      </div>
      <SemanticAIResponse
        content={mentor.raw_text || mentor.response}
        type="mentor"
      />
    </div>
  );
};

MentorBlock.propTypes = {
  mentor: PropTypes.object,
  timestamp: PropTypes.string,
};

export const ProfessorBlock = ({ professor, timestamp }) => {
  if (!professor || professor.active === false || (!professor.response && !professor.raw_text)) {
    return null;
  }
  return (
    <div className="border border-blue-200 rounded-2xl shadow-sm p-5 bg-white">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <GraduationCap className="h-5 w-5 text-blue-600" />
          <div>
            <p className="font-semibold text-blue-900">Professor Insight</p>
            <p className="text-xs text-blue-600">Structured reasoning</p>
          </div>
        </div>
        {timestamp && (
          <span className="text-xs text-blue-600 flex items-center gap-1">
            <GitBranch className="h-3 w-3" />
            {timestamp}
          </span>
        )}
      </div>
      {professor.deferred_reason && (
        <div className="text-xs text-blue-500 mb-2">
          {professor.deferred_reason}
        </div>
      )}
      <SemanticAIResponse
        content={professor.raw_text || professor.response}
        type="professor"
      />
    </div>
  );
};

ProfessorBlock.propTypes = {
  professor: PropTypes.object,
  timestamp: PropTypes.string,
};

const DefinitionCard = ({ data }) => (
  <div className="bg-white rounded-2xl border border-amber-100 shadow-sm p-5">
    <p className="text-xs font-semibold text-amber-500 uppercase tracking-wide mb-1">Concept definition</p>
    <h4 className="text-lg font-bold text-amber-900 mb-2">{data.concept || 'Concept'}</h4>
    <p className="text-sm text-amber-900 leading-relaxed mb-3">{data.definition}</p>
    {Array.isArray(data.exam_ready_points) && data.exam_ready_points.length > 0 && (
      <ul className="text-sm text-amber-800 space-y-1">
        {data.exam_ready_points.map((point, idx) => (
          <li key={idx} className="flex items-start gap-2">
            <ArrowRight className="h-3 w-3 mt-1 text-amber-500" />
            <span>{point}</span>
          </li>
        ))}
      </ul>
    )}
    {data.mentor_hint && (
      <p className="mt-3 text-xs text-amber-600 italic">
        {data.mentor_hint}
      </p>
    )}
  </div>
);

DefinitionCard.propTypes = {
  data: PropTypes.object.isRequired,
};

const ReasoningPath = ({ data }) => (
  <div className="bg-blue-50 rounded-2xl border border-blue-100 p-5">
    <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-2 flex items-center gap-2">
      <GitMerge className="h-4 w-4" /> Reasoning Flow
    </p>
    <ol className="space-y-2 text-sm text-blue-900">
      {(data.steps || []).map((step, idx) => (
        <li key={idx} className="flex gap-3">
          <span className="font-bold">{idx + 1}.</span>
          <span>{step}</span>
        </li>
      ))}
    </ol>
    {data.professor_notes && (
      <div className="mt-3 text-xs text-blue-700 bg-white rounded-xl border border-blue-100 p-3">
        {data.professor_notes}
      </div>
    )}
    {data.edge_case && (
      <div className="mt-2 text-xs text-blue-600 italic">
        Edge case: {data.edge_case}
      </div>
    )}
  </div>
);

ReasoningPath.propTypes = {
  data: PropTypes.object.isRequired,
};

const CompareGrid = ({ data }) => (
  <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
    <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-200">
      <div className="p-4">
        <p className="text-xs font-semibold uppercase text-gray-500 mb-1">{data.left_title || 'Left'}</p>
        <ul className="text-sm text-gray-800 space-y-1">
          {(data.left_points || []).map((point, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <Balance className="h-3 w-3 mt-1 text-gray-400" />
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="p-4">
        <p className="text-xs font-semibold uppercase text-gray-500 mb-1">{data.right_title || 'Right'}</p>
        <ul className="text-sm text-gray-800 space-y-1">
          {(data.right_points || []).map((point, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <Balance className="h-3 w-3 mt-1 text-gray-400" />
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  </div>
);

CompareGrid.propTypes = {
  data: PropTypes.object.isRequired,
};

const ApplicationStory = ({ data }) => (
  <div className="bg-green-50 border border-green-200 rounded-2xl p-5">
    <p className="text-xs font-semibold text-green-600 uppercase tracking-wide mb-2">
      Real Life Story
    </p>
    <p className="text-sm text-green-900 mb-3">{data.scenario}</p>
    {(data.action_steps || []).length > 0 && (
      <ul className="text-sm text-green-800 space-y-1">
        {data.action_steps.map((step, idx) => (
          <li key={idx} className="flex gap-2">
            <ArrowRight className="h-3 w-3 mt-1 text-green-500" />
            <span>{step}</span>
          </li>
        ))}
      </ul>
    )}
    {data.cta && (
      <p className="mt-3 text-xs text-green-700 italic">{data.cta}</p>
    )}
  </div>
);

ApplicationStory.propTypes = {
  data: PropTypes.object.isRequired,
};

const FollowUpCard = ({ data }) => (
  <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5">
    <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-2">
      Clarification
    </p>
    {data.what_changed && (
      <p className="text-sm text-slate-900 mb-2">{data.what_changed}</p>
    )}
    {data.fresh_example && (
      <p className="text-xs text-slate-600 italic">{data.fresh_example}</p>
    )}
  </div>
);

FollowUpCard.propTypes = {
  data: PropTypes.object.isRequired,
};

const ConceptLayers = ({ data }) => (
  <div className="bg-indigo-50 border border-indigo-200 rounded-2xl p-5 space-y-2">
    <p className="text-xs font-semibold text-indigo-600 uppercase tracking-wide">Concept layers</p>
    <p className="text-sm text-indigo-900">{data.overview}</p>
    {(data.key_steps || []).length > 0 && (
      <ol className="list-decimal list-inside text-sm text-indigo-800 space-y-1">
        {data.key_steps.map((step, idx) => (
          <li key={idx}>{step}</li>
        ))}
      </ol>
    )}
    {data.real_life && (
      <p className="text-xs text-indigo-600 italic">{data.real_life}</p>
    )}
  </div>
);

ConceptLayers.propTypes = {
  data: PropTypes.object.isRequired,
};

export const StructuredBlockRenderer = ({ structuredBlocks }) => {
  const normalized = useNormalizedBlocks(structuredBlocks);
  if (!normalized.length) return null;
  return (
    <div className="space-y-4">
      {normalized.map((block, idx) => {
        switch (block.type) {
          case 'definition_card':
          case 'definition_block':
            return <DefinitionCard key={idx} data={block.data} />;
          case 'reasoning_path':
            return <ReasoningPath key={idx} data={block.data} />;
          case 'compare_grid':
          case 'compare_table':
            return <CompareGrid key={idx} data={block.data} />;
          case 'application_story':
            return <ApplicationStory key={idx} data={block.data} />;
          case 'follow_up':
            return <FollowUpCard key={idx} data={block.data} />;
          case 'concept_layers':
            return <ConceptLayers key={idx} data={block.data} />;
          default:
            return (
              <div key={idx} className="border rounded-xl p-4 text-sm text-gray-700 bg-white">
                <p className="font-semibold mb-1 capitalize">{block.type}</p>
                <pre className="text-xs overflow-x-auto">{JSON.stringify(block.data, null, 2)}</pre>
              </div>
            );
        }
      })}
    </div>
  );
};

StructuredBlockRenderer.propTypes = {
  structuredBlocks: PropTypes.object,
};

export const VisualOfferCard = ({ offer, visualData, topic, onTriggerVisual }) => {
  const hasVisualAsset = Boolean(
    visualData &&
    (visualData.lottie_file || visualData.asset_url || visualData.content)
  );

  if (!offer && !hasVisualAsset) {
    return null;
  }

  const initialOpen = visualData?.mode === 'auto';
  const [showVisual, setShowVisual] = useState(initialOpen);

  const handleClick = () => {
    if (hasVisualAsset) {
      setShowVisual((prev) => !prev);
    } else if (onTriggerVisual) {
      onTriggerVisual(topic || offer?.topic || '');
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Visual Experience
          </p>
          <p className="text-sm text-gray-800">
            {offer?.message || 'Visual insight ready'}
          </p>
        </div>
        <button
          onClick={handleClick}
          className="px-4 py-2 bg-gray-900 text-white text-xs font-semibold rounded-xl hover:bg-gray-700 transition"
        >
          {hasSvg ? (showVisual ? 'Hide Visual' : 'Show Visual') : 'Show Visual'}
        </button>
      </div>
      {showVisual && hasVisualAsset && (
        <VisualPlayer visual={visualData} autoPlay={visualData?.mode !== 'offer'} />
      )}
    </div>
  );
};

VisualOfferCard.propTypes = {
  offer: PropTypes.object,
  visualData: PropTypes.shape({
    content: PropTypes.string,
    generated: PropTypes.bool,
  }),
  topic: PropTypes.string,
  onTriggerVisual: PropTypes.func,
};

export const SuggestionList = ({ suggestions, onSelect }) => {
  if (!suggestions || !suggestions.length) {
    return null;
  }
  return (
    <div className="flex flex-wrap gap-2">
      {suggestions.map((suggestion, idx) => (
        <button
          key={`${suggestion}-${idx}`}
          onClick={() => onSelect && onSelect(suggestion)}
          className="px-4 py-2 text-sm bg-white border border-gray-200 rounded-full shadow-sm hover:border-purple-400 hover:text-purple-600 transition"
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
};

SuggestionList.propTypes = {
  suggestions: PropTypes.arrayOf(PropTypes.string),
  onSelect: PropTypes.func,
};

export default {
  MentorBlock,
  ProfessorBlock,
  StructuredBlockRenderer,
  VisualOfferCard,
  SuggestionList,
};
