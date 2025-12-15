/**
 * 🔮 NETRA v4.0 Demo Page
 * =======================
 * 
 * Demo page for testing the Visual Intelligence Engine.
 * Shows the complete flow from question to generated visual.
 */

import React, { useState } from 'react';
import { NetraEngineV4 } from '../netra/v4';

const SAMPLE_QUESTIONS = [
  "Explain how photosynthesis works in plants",
  "Show me Newton's third law with a rocket",
  "Compare mitosis and meiosis",
  "How does the water cycle work?",
  "Explain the structure of an atom",
  "Show the process of protein synthesis",
  "How does electricity flow in a circuit?",
  "Explain the concept of supply and demand",
];

const NetraV4Demo = () => {
  const [question, setQuestion] = useState('');
  const [submittedQuestion, setSubmittedQuestion] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim()) {
      setSubmittedQuestion(question.trim());
      setResult(null);
      setError(null);
    }
  };

  const handleSampleClick = (sample) => {
    setQuestion(sample);
    setSubmittedQuestion(sample);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <span className="text-3xl">🔮</span>
            NETRA v4.0 - Visual Intelligence Demo
          </h1>
          <p className="text-white/60 mt-1">
            AI-powered unique educational visuals
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Input Section */}
        <section className="mb-8">
          <form onSubmit={handleSubmit} className="flex gap-4">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask any educational question..."
              className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <button
              type="submit"
              disabled={!question.trim()}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-medium transition-colors"
            >
              Generate Visual
            </button>
          </form>

          {/* Sample Questions */}
          <div className="mt-4">
            <p className="text-sm text-white/60 mb-2">Try these examples:</p>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_QUESTIONS.map((sample) => (
                <button
                  key={sample}
                  onClick={() => handleSampleClick(sample)}
                  className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-sm text-white/80 transition-colors"
                >
                  {sample.length > 40 ? sample.slice(0, 40) + '...' : sample}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Visual Display */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Visual */}
          <div className="lg:col-span-2">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl overflow-hidden">
              <div className="p-4 border-b border-white/10">
                <h2 className="font-semibold">Generated Visual</h2>
                {submittedQuestion && (
                  <p className="text-sm text-white/60 mt-1">
                    "{submittedQuestion}"
                  </p>
                )}
              </div>
              <div className="aspect-video">
                <NetraEngineV4
                  question={submittedQuestion}
                  width="100%"
                  height="100%"
                  onGenerated={(res) => {
                    console.log('Generated:', res);
                    setResult(res);
                  }}
                  onError={(err) => {
                    console.error('Error:', err);
                    setError(err.message);
                  }}
                />
              </div>
            </div>
          </div>

          {/* Metadata Panel */}
          <div className="space-y-4">
            {/* Status */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <span>📊</span> Status
              </h3>
              {result ? (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-white/60">Status</span>
                    <span className={result.success ? 'text-green-400' : 'text-red-400'}>
                      {result.success ? '✓ Success' : '✗ Failed'}
                    </span>
                  </div>
                  {result.generation_info && (
                    <div className="flex justify-between">
                      <span className="text-white/60">Generation Time</span>
                      <span>{result.generation_info.time_ms}ms</span>
                    </div>
                  )}
                </div>
              ) : error ? (
                <div className="text-red-400 text-sm">{error}</div>
              ) : (
                <div className="text-white/40 text-sm">No visual generated yet</div>
              )}
            </div>

            {/* Metadata */}
            {result?.metadata && (
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <span>🏷️</span> Metadata
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-white/60">Concept</span>
                    <span className="text-right max-w-[150px] truncate">{result.metadata.concept}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">Intent</span>
                    <span className="capitalize">{result.metadata.intent?.replace('_', ' ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">Style</span>
                    <span className="capitalize">{result.metadata.style?.replace('_', ' ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">Complexity</span>
                    <span className="capitalize">{result.metadata.complexity}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Teaching Info */}
            {result?.teaching && (
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <span>📚</span> Teaching
                </h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-white/60">Title:</span>
                    <p className="mt-1">{result.teaching.title}</p>
                  </div>
                  <div>
                    <span className="text-white/60">Hotspots:</span>
                    <span className="ml-2">{result.teaching.hotspots?.length || 0}</span>
                  </div>
                  <div>
                    <span className="text-white/60">Steps:</span>
                    <span className="ml-2">{result.teaching.steps?.length || 0}</span>
                  </div>
                  {result.teaching.key_takeaways?.length > 0 && (
                    <div>
                      <span className="text-white/60 block mb-1">Key Takeaways:</span>
                      <ul className="list-disc list-inside text-xs text-white/80 space-y-1">
                        {result.teaching.key_takeaways.slice(0, 3).map((t, i) => (
                          <li key={i}>{t}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Debug Info */}
            {result?.generation_info && (
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <span>🔧</span> Debug
                </h3>
                <div className="text-xs space-y-1 text-white/60">
                  <div>Model: {result.generation_info.model}</div>
                  <div>Request ID: {result.generation_info.request_id?.slice(0, 8)}...</div>
                  <details className="mt-2">
                    <summary className="cursor-pointer hover:text-white/80">View Prompt</summary>
                    <pre className="mt-2 p-2 bg-black/30 rounded text-xs overflow-auto max-h-40">
                      {result.generation_info.prompt_used}
                    </pre>
                  </details>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Architecture Info */}
        <section className="mt-12 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <span>🏗️</span> Architecture
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-center text-sm">
            {[
              { icon: '❓', label: 'Question', desc: 'User input' },
              { icon: '🧠', label: 'Strategy Resolver', desc: 'Gemini 1.5 Flash' },
              { icon: '🎨', label: 'Image Generator', desc: 'Gemini 2.0 Flash' },
              { icon: '📚', label: 'Teaching Layer', desc: 'Metadata + Hotspots' },
              { icon: '🖼️', label: 'Renderer', desc: 'React Component' },
            ].map((step, i) => (
              <div key={step.label} className="flex flex-col items-center">
                <div className="text-3xl mb-2">{step.icon}</div>
                <div className="font-medium">{step.label}</div>
                <div className="text-white/50 text-xs">{step.desc}</div>
                {i < 4 && (
                  <div className="hidden md:block absolute right-0 top-1/2 -translate-y-1/2 text-white/30">
                    →
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-12">
        <div className="max-w-6xl mx-auto px-6 py-4 text-center text-white/40 text-sm">
          NETRA v4.0 - Visual Intelligence Orchestrator • Powered by Gemini
        </div>
      </footer>
    </div>
  );
};

export default NetraV4Demo;

