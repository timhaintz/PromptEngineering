import { redirect } from 'next/navigation';
import { getAllPatternTriples } from '@/lib/data/papers';

export const dynamicParams = false;

export function generateStaticParams() {
  return getAllPatternTriples().map(({ paperId, categoryIndex, patternIndex }) => ({
    paperId,
    categoryIndex,
    patternIndex,
  }));
}

/**
 * Legacy deep pattern route: /pattern/{paperId}/{categoryIndex}/{patternIndex}
 * Redirects to unified paper-rooted route with anchors: /papers/{paperId}#p-{categoryIndex}-{patternIndex}
 */
export default async function LegacyPatternRedirect({ params }: { params: Promise<{ paperId: string; categoryIndex: string; patternIndex: string }> }) {
  const { paperId, categoryIndex, patternIndex } = await params;
  redirect(`/papers/${paperId}#p-${categoryIndex}-${patternIndex}`);
}
