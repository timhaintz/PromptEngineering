import { redirect } from 'next/navigation';

export default async function PaperAliasRedirect({ params }: { params: Promise<{ paperId: string }> }) {
  const { paperId } = await params;
  redirect(`/papers/${paperId}`);
}
