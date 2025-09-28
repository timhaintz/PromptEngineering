import React from 'react';
import clsx from 'clsx';

/**
 * PageShell
 * Consistent page wrapper applying:
 *  - background via token class (bg-base)
 *  - top padding to compensate for fixed nav
 *  - responsive horizontal padding
 *  - optional max-width control
 *  - optional variant for reading (narrow) vs application (wide)
 */
export interface PageShellProps {
  children: React.ReactNode;
  className?: string;
  /** width variant */
  variant?: 'default' | 'narrow' | 'wide' | 'full';
  /** disable vertical spacing wrapper if page supplies its own */
  noContainer?: boolean;
  /** optional semantic main flag */
  as?: 'main' | 'div';
}

const widthClasses: Record<NonNullable<PageShellProps['variant']>, string> = {
  default: 'max-w-7xl',
  narrow: 'max-w-4xl',
  wide: 'max-w-[1600px]',
  full: 'max-w-none'
};

export function PageShell({
  children,
  className,
  variant = 'default',
  noContainer,
  as = 'main'
}: PageShellProps) {
  const Comp = as;
  return (
    <div className={clsx('min-h-screen bg-base text-primary transition-colors', className)}>
      <Comp className={clsx(!noContainer && 'pt-8 pb-16 px-4 sm:px-6 lg:px-8')}> 
        <div className={clsx(!noContainer && widthClasses[variant], !noContainer && 'mx-auto space-y-10')}>
          {children}
        </div>
      </Comp>
    </div>
  );
}

export default PageShell;
