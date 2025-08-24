import { redirect } from 'next/navigation';

/**
 * Legacy deep pattern route: /pattern/{paperId}/{categoryIndex}/{patternIndex}
 * Redirects to unified paper-rooted route with anchors: /papers/{paperId}#p-{categoryIndex}-{patternIndex}
 */
export default async function LegacyPatternRedirect({ params }: { params: Promise<{ paperId: string; categoryIndex: string; patternIndex: string }> }) {
  const { paperId, categoryIndex, patternIndex } = await params;
  redirect(`/papers/${paperId}#p-${categoryIndex}-${patternIndex}`);
}
