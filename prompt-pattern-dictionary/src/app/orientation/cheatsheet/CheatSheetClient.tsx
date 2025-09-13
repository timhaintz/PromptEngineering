"use client";
import React from 'react';
import Link from 'next/link';

interface Block { title: string; items: string[] }
interface Props { blocks: Block[] }

export default function CheatSheetClient({ blocks }: Props) {
  return (
    <div className="min-h-screen bg-white print:bg-white">
      <div className="container mx-auto px-4 py-8 lg:py-12">
        <div className="no-print mb-6 flex items-center justify-between flex-wrap gap-4">
          <h1 className="text-3xl font-bold text-gray-900">Orientation Cheat Sheet</h1>
          <div className="flex gap-3 text-sm">
            <Link href="/orientation" className="text-indigo-600 hover:underline">Full Orientation</Link>
            <PrintButton />
          </div>
        </div>
        <p className="text-sm text-gray-600 max-w-3xl mb-8">Concise reference for day-to-day prompt pattern work. See full Orientation for rationale and extended guidance.</p>
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6 print:grid-cols-3">
          {blocks.map(block => (
            <div key={block.title} className="border rounded-lg p-4 bg-white shadow-sm break-inside-avoid print:shadow-none">
              <h2 className="text-sm font-semibold tracking-wide text-gray-800 mb-2 uppercase">{block.title}</h2>
              <ul className="text-xs space-y-1 leading-snug">
                {block.items.map((it, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-gray-400">•</span>
                    <span className="text-gray-800">{it}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <FooterMeta />
      </div>
    </div>
  );
}

function PrintButton() {
  return (
    <button
      type="button"
      onClick={() => window.print()}
      className="px-3 py-1 rounded border bg-gray-50 hover:bg-gray-100 text-gray-800"
    >
      Print
    </button>
  );
}

function FooterMeta() {
  return (
    <div className="mt-10 text-xs text-gray-500 no-print">
      Generated: {new Date().toISOString().slice(0,10)} • Feedback welcome – open an issue with suggestions.
    </div>
  );
}
