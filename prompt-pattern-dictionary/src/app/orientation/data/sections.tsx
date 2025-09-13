import React from 'react';

export interface OrientationSectionMeta {
  slug: string;
  id: string; // anchor id for combined page
  title: string;
  number: number;
  description: string;
  legacyAnchors?: string[]; // potential old ids
  component: React.ReactNode; // rendered body (without outer <section>)
}

// Placeholder components – real content will be migrated incrementally.
const QuickStart = () => (
  <div>
    <p>Content pending migration from legacy Orientation page.</p>
  </div>
);
const PatternAnatomy = () => (<div><p>Content pending migration.</p></div>);
const Lifecycle = () => (<div><p>Content pending migration.</p></div>);
const Choosing = () => (<div><p>Content pending migration.</p></div>);
const Combining = () => (<div><p>Content pending migration.</p></div>);
const Adaptation = () => (<div><p>Content pending migration.</p></div>);
const AntiPatterns = () => (<div><p>Content pending migration.</p></div>);
const Evaluation = () => (<div><p>Content pending migration.</p></div>);
const AccessibilityResponsible = () => (<div><p>Content pending migration.</p></div>);
const Glossary = () => (<div><p>Content pending migration.</p></div>);
const FAQ = () => (<div><p>Content pending migration.</p></div>);
const Feedback = () => (<div><p>Content pending migration.</p></div>);
const NextSteps = () => (<div><p>Content pending migration.</p></div>);

export const ORIENTATION_SECTIONS: OrientationSectionMeta[] = [
  { slug: 'quick-start', id: 'quick-start', title: 'Quick Start', number: 1, description: 'Practical 8-step startup path for using patterns safely.', component: <QuickStart /> },
  { slug: 'what-is-a-pattern', id: 'what-is-a-pattern', title: 'What Is a Pattern', number: 2, description: 'Definition, value, and collaboration benefits.', component: <div><p>Content pending migration.</p></div> },
  { slug: 'pattern-anatomy', id: 'pattern-anatomy', title: 'Pattern Anatomy', number: 3, description: 'Schema fields, 5-Key template, usage guidance diagram.', component: <PatternAnatomy /> },
  { slug: 'lifecycle', id: 'lifecycle', title: 'Lifecycle', number: 4, description: 'From need framing through monitoring & drift detection.', component: <Lifecycle /> },
  { slug: 'choosing-patterns', id: 'choosing-patterns', title: 'Choosing Patterns', number: 5, description: 'Heuristics for selecting candidate patterns.', component: <Choosing /> },
  { slug: 'combining-patterns', id: 'combining-patterns', title: 'Combining Patterns', number: 6, description: 'Safe compositional chaining strategies.', component: <Combining /> },
  { slug: 'adaptation', id: 'adaptation', title: 'Adaptation & Remix', number: 7, description: 'Principled iteration, versioning, ethical considerations.', component: <Adaptation /> },
  { slug: 'anti-patterns', id: 'anti-patterns', title: 'Anti-Patterns', number: 8, description: 'Common failure modes and refactoring cues.', component: <AntiPatterns /> },
  { slug: 'quality-evaluation', id: 'quality-evaluation', title: 'Quality & Evaluation', number: 9, description: 'Metrics, failure taxonomy, baselining discipline.', component: <Evaluation /> },
  { slug: 'accessibility-responsible-use', id: 'accessibility-responsible-use', title: 'Accessibility & Responsible Use', number: 10, description: 'Inclusive, transparent, and safe utilization guidelines.', component: <AccessibilityResponsible /> },
  { slug: 'glossary', id: 'glossary', title: 'Glossary', number: 11, description: 'Key terms and definitions.', component: <Glossary /> },
  { slug: 'faq', id: 'faq', title: 'FAQ', number: 12, description: 'Frequently asked clarifications.', component: <FAQ /> },
  { slug: 'feedback', id: 'feedback', title: 'Feedback', number: 13, description: 'How to contribute improvements and report issues.', component: <Feedback /> },
  { slug: 'next-steps', id: 'next-steps', title: 'Next Steps', number: 14, description: 'Where to go after orienting.', component: <NextSteps /> }
];
