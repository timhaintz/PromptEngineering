import { redirect } from 'next/navigation';
import { getAllPaperIds } from '@/lib/data/papers';

export const dynamicParams = false;

export function generateStaticParams() {
  return getAllPaperIds().map((paperId) => ({ paperId }));
}

export default async function PatternPaperRedirect({ params }: { params: Promise<{ paperId: string }> }) {
  const { paperId } = await params;
  redirect(`/papers/${paperId}`);
}
