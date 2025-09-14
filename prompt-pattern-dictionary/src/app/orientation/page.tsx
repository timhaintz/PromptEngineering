import Link from 'next/link';
import { ORIENTATION_SECTIONS } from './data/sections';
import OrientationNav from './components/OrientationNav';

export const metadata = {
  title: 'Orientation | Prompt Pattern Dictionary',
  description: 'Hub for Orientation sections, quick start, and consolidated view.'
};

export default function OrientationHubPage() {
  return (
    <div>
      <h1 className="text-4xl font-bold tracking-tight text-slate-900 mb-6">Orientation</h1>
      <p className="text-slate-700 max-w-3xl leading-relaxed mb-6">Use this hub to jump into focused sections or view the full consolidated page. Each section is deliberately concise and accessible; the <em>All Sections</em> view preserves original anchor stability.</p>
      <div className="mb-10">
        <OrientationNav variant="inline" />
      </div>
      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
        {ORIENTATION_SECTIONS.map(sec => (
          <div key={sec.slug} className="border rounded-lg p-4 bg-white shadow-sm hover:shadow transition-shadow">
            <h2 className="font-semibold text-slate-900 text-lg flex items-baseline gap-2"><span className="text-slate-600 tabular-nums">{sec.number}.</span>{sec.title}</h2>
            <p className="text-sm text-slate-600 mt-1 mb-3">{sec.description}</p>
            <Link href={`/orientation/${sec.slug}`} className="text-indigo-600 text-sm font-medium hover:underline">Open Section →</Link>
          </div>
        ))}
        <div className="border rounded-lg p-4 bg-indigo-50 shadow-sm hover:shadow transition-shadow">
          <h2 className="font-semibold text-slate-900 text-lg flex items-baseline gap-2">All Sections</h2>
          <p className="text-sm text-slate-700 mt-1 mb-3">Read the complete Orientation content in one scrollable page (original format with anchors).</p>
            <Link href="/orientation/all" className="text-indigo-700 text-sm font-medium hover:underline">View All →</Link>
        </div>
        <div className="border rounded-lg p-4 bg-white shadow-sm hover:shadow transition-shadow">
          <h2 className="font-semibold text-slate-900 text-lg flex items-baseline gap-2">Cheat Sheet</h2>
          <p className="text-sm text-slate-600 mt-1 mb-3">Condensed printable reference (5‑Key template, lifecycle, evaluation metrics, anti‑patterns, responsible use).</p>
            <Link href="/orientation/cheatsheet" className="text-indigo-600 text-sm font-medium hover:underline">Open Cheat Sheet →</Link>
        </div>
      </div>
    </div>
  );
}
