import React from 'react';
import clsx from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  interactive?: boolean;
  href?: string;
  as?: 'div' | 'a';
  header?: React.ReactNode;
  meta?: React.ReactNode;
  footer?: React.ReactNode;
  dense?: boolean;
}

export const Card: React.FC<CardProps> = ({
  interactive = true,
  href,
  as = href ? 'a' : 'div',
  header,
  meta,
  footer,
  dense = false,
  className,
  children,
  ...rest
}) => {
  const padding = dense ? 'p-3' : 'p-4';
  const base = 'block focus-ring surface-card';
  const interactiveClass = interactive ? 'surface-card-interactive' : '';
  const componentProps: Record<string, unknown> = { className: clsx(base, interactiveClass, padding, className), ...rest };
  if (href && as === 'a') componentProps.href = href;
  const Comp = (as === 'a' ? 'a' : 'div');
  return (
    <Comp {...componentProps}>
      {(header || meta) && (
        <div className="flex items-start justify-between gap-2 mb-1">
          {header && <div className="font-semibold text-secondary min-w-0 break-words">{header}</div>}
          {meta && <div className="text-[10px] text-muted font-mono">{meta}</div>}
        </div>
      )}
      {children}
      {footer && <div className="mt-2 text-xs text-muted">{footer}</div>}
    </Comp>
  );
};

export const CardGrid: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...rest }) => (
  <div className={clsx('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4', className)} {...rest} />
);

export default Card;
