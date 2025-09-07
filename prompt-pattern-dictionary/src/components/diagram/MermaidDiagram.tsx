"use client";
import React, { useEffect, useRef, useState } from 'react';

interface MermaidDiagramProps {
  chart: string;
  describedById?: string; // id of textual description element
  className?: string;
  ariaLabel?: string; // fallback label when no description id provided
}

export default function MermaidDiagram({ chart, describedById, className, ariaLabel }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const mermaid = (await import('mermaid')).default; // dynamic import
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'strict',
          theme: 'base',
          themeVariables: {
            primaryColor: '#1e3a8a',
            primaryTextColor: '#ffffff',
            primaryBorderColor: '#1e3a8a',
            lineColor: '#4338ca',
            secondaryColor: '#eef2ff',
            tertiaryColor: '#ffffff'
          },
          flowchart: { useMaxWidth: true }
        });
        if (cancelled) return;
        if (containerRef.current) {
          const { svg } = await mermaid.render(`mermaid-diagram-${Math.random().toString(36).slice(2)}`, chart);
          containerRef.current.innerHTML = svg;
          setIsReady(true);
        }
      } catch (e: unknown) {
        if (!cancelled) {
          const msg = typeof e === 'object' && e && 'message' in e ? String((e as { message?: unknown }).message) : 'Failed to render diagram';
          setError(msg);
        }
      }
    })();
    return () => { cancelled = true; };
  }, [chart]);

  const imgLabelProps = describedById ? { 'aria-describedby': describedById } : { 'aria-label': ariaLabel || 'Mermaid diagram' };
  return (
    <div className={className} {...imgLabelProps} role="group">
      {!isReady && !error && (
        <pre className="text-xs text-gray-500 whitespace-pre-wrap" aria-label="Mermaid source fallback">{chart}</pre>
      )}
      {error && (
        <div className="text-sm text-red-600" role="alert">Diagram error: {error}</div>
      )}
      <div ref={containerRef} className="overflow-x-auto" />
    </div>
  );
}
