import React from 'react';
import clsx from 'clsx';

type NativeDivProps = Omit<React.HTMLAttributes<HTMLDivElement>, 'title'>;

export interface PageHeaderProps extends NativeDivProps {
  heading: React.ReactNode;
  subtitle?: React.ReactNode;
  actions?: React.ReactNode;
  compact?: boolean;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ heading, subtitle, actions, compact = false, className, ...rest }) => {
  return (
    <div className={clsx('mb-8', compact && 'mb-4', className)} {...rest}>
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className={clsx('font-bold text-primary', compact ? 'text-2xl' : 'text-3xl')}>{heading}</h1>
          {subtitle && <p className={clsx('text-secondary max-w-3xl', compact ? 'mt-1 text-sm' : 'mt-2 text-base')}>{subtitle}</p>}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
};

export default PageHeader;
