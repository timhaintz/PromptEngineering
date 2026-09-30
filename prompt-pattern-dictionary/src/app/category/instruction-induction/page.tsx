import type { Metadata } from 'next';
import CategoryPage from '../[slug]/page';

export const metadata: Metadata = {
  title: 'Induction | Ballarat AI Prompt Taxonomy',
  alternates: { canonical: '/category/induction' },
};

export default function InstructionInductionPage() {
  return CategoryPage({ params: Promise.resolve({ slug: 'induction' }) });
}