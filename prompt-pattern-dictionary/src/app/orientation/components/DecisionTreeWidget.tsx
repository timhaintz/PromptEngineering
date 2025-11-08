"use client";
import React, { useState } from 'react';

interface NodeSuggestion { goal: string; categories: string[]; patterns: string[]; }

const SUGGESTIONS: NodeSuggestion[] = [
  { goal: 'Extract structured fields', categories: ['structured extraction','classification'], patterns: ['Structured Extraction','Consistency / Critique'] },
  { goal: 'Compare two texts', categories: ['comparison','logical reasoning'], patterns: ['Comparison Evaluation','Justified Answer'] },
  { goal: 'Improve clarity of content', categories: ['refactoring','prompt improvement'], patterns: ['Refactor / Clarify','Task Breakdown / Decomposition'] },
  { goal: 'Generate defensive insights', categories: ['assessment','prediction'], patterns: ['Risk Scoring','Threat Categorization'] },
  { goal: 'Validate output quality', categories: ['error identification','evaluation'], patterns: ['Consistency / Critique','Chain / Justified Answer'] }
];

export function DecisionTreeWidget() {
  const [selected, setSelected] = useState<string>('');
  const current = SUGGESTIONS.find(s => s.goal === selected);
  return (
    <section className="mt-6 border border-muted rounded-lg p-4 bg-surface-1 shadow-sm" aria-labelledby="decision-tree-heading">
      <h3 id="decision-tree-heading" className="text-sm font-semibold mb-2 flex items-center gap-2">
        <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-accent/10 text-accent text-[10px] font-bold">P2</span>
        Decision Tree (Goal → Suggestions)
      </h3>
      <p className="text-xs text-secondary mb-3">Select your immediate goal to view recommended categories and example patterns. Feature-flag controlled; exploratory.</p>
      <div role="radiogroup" aria-label="Prompt engineering goal" className="grid sm:grid-cols-2 gap-2 mb-3">
        {SUGGESTIONS.map(s => (
          <button
            key={s.goal}
            type="button"
            role="radio"
            aria-checked={selected === s.goal}
            onClick={() => setSelected(s.goal)}
            className={`text-left text-xs rounded border px-2 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent transition ${selected === s.goal ? 'bg-accent/10 border-accent' : 'bg-surface-2 border-muted'}`}
          >
            {s.goal}
          </button>
        ))}
      </div>
      {current ? (
        <div className="text-xs" aria-live="polite">
          <p className="font-medium mb-1">Suggested Categories:</p>
          <ul className="list-disc pl-5 mb-2">
            {current.categories.map(c => <li key={c}>{c}</li>)}
          </ul>
          <p className="font-medium mb-1">Example Patterns:</p>
          <ul className="list-disc pl-5">
            {current.patterns.map(p => <li key={p}>{p}</li>)}
          </ul>
        </div>
      ) : (
        <p className="text-xs text-muted" aria-live="polite">Choose a goal to see suggestions.</p>
      )}
    </section>
  );
}
