import { redirect } from 'next/navigation';

export default async function PatternPaperRedirect({ params }: { params: Promise<{ paperId: string }> }) {
  const { paperId } = await params;
  redirect(`/papers/${paperId}`);
}
