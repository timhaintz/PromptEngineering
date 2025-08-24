"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

type Crumb = { href: string; label: string };

function toTitle(slug: string) {
  return slug.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' ');
}

export default function Breadcrumbs({ manual }: { manual?: Crumb[] }) {
  const pathname = usePathname();
  const parts = pathname.split('/').filter(Boolean);

  const crumbs: Crumb[] = manual ?? parts.map((_, i) => {
    const href = '/' + parts.slice(0, i + 1).join('/');
    const label = toTitle(parts[i]);
    return { href, label };
  });

  // Adjust root segment links to valid listing pages
  if (!manual && crumbs.length > 0) {
    const firstSeg = parts[0];
    if (firstSeg === 'category') {
      crumbs[0] = { href: '/categories', label: 'Categories' };
    } else if (firstSeg === 'pattern') {
      crumbs[0] = { href: '/patterns', label: 'Patterns' };
    } else if (firstSeg === 'papers') {
      crumbs[0] = { href: '/papers', label: 'Papers' };
    }
  }

  if (crumbs.length <= 1) return null; // hide on shallow routes

  return (
    <nav aria-label="Breadcrumb" className="mb-4">
      <ol className="flex flex-wrap items-center gap-1 text-sm" itemScope itemType="https://schema.org/BreadcrumbList">
        <li itemProp="itemListElement" itemScope itemType="https://schema.org/ListItem">
          <Link href="/" itemProp="item" className="text-blue-700 hover:text-blue-900">Home</Link>
          <meta itemProp="position" content="1" />
        </li>
        {crumbs.map((c, idx) => (
          <li key={c.href} className="flex items-center gap-1" itemProp="itemListElement" itemScope itemType="https://schema.org/ListItem">
            <span className="text-gray-400">/</span>
            {idx === crumbs.length - 1 ? (
              <span className="text-gray-700" itemProp="name">{c.label}</span>
            ) : (
              <Link href={c.href} className="text-blue-700 hover:text-blue-900" itemProp="item">
                <span itemProp="name">{c.label}</span>
              </Link>
            )}
            <meta itemProp="position" content={(idx + 2).toString()} />
          </li>
        ))}
      </ol>
    </nav>
  );
}
