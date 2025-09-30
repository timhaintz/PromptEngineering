'use client';

import { useRouter } from 'next/navigation';
import { Card, CardGrid } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';

export interface PaperSummary {
  paperId: string;
  title: string;
  authors: string[];
  url: string;
  count: number;
}

interface PapersGridProps {
  papers: PaperSummary[];
}

export default function PapersGrid({ papers }: PapersGridProps) {
  const router = useRouter();

  const handleNavigate = (paperId: string) => {
    router.push(`/papers/${paperId}`);
  };

  return (
    <CardGrid>
      {papers.map(paper => {
        const authorLine = paper.authors.slice(0, 4).join(', ') + (paper.authors.length > 4 ? ' et al.' : '');

        return (
          <Card
            key={paper.paperId}
            role="link"
            tabIndex={0}
            onClick={() => handleNavigate(paper.paperId)}
            onKeyDown={event => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                handleNavigate(paper.paperId);
              }
            }}
            className="surface-card-interactive cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
            header={
              <span className="block leading-tight break-words" title={paper.title}>
                {paper.title}
              </span>
            }
          >
            <div className="text-xs text-muted mb-2 truncate" title={authorLine}>
              {authorLine}
            </div>
            <div className="flex items-center gap-2 text-xs">
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-secondary hover:text-primary focus-ring rounded-sm px-1"
                onClick={event => event.stopPropagation()}
                onKeyDown={event => event.stopPropagation()}
              >
                Source Paper
              </a>
              <Badge variant="generic" className="badge-id ml-auto">
                Patterns: {paper.count}
              </Badge>
            </div>
          </Card>
        );
      })}
    </CardGrid>
  );
}
