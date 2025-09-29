import React from 'react';
import clsx from 'clsx';

type BadgeVariant = 'category' | 'ai' | 'generic';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  as?: 'span' | 'div';
}

const variantClass: Record<BadgeVariant, string> = {
  category: 'badge-category',
  ai: 'badge-ai',
  generic: 'badge-generic'
};

export const Badge: React.FC<BadgeProps> = ({ variant = 'generic', as = 'span', className, ...rest }) => {
  const Component = as === 'div' ? 'div' : 'span';
  return <Component className={clsx(variantClass[variant], className)} {...rest} />;
};

export default Badge;
