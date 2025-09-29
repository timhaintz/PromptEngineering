import React from 'react';
import clsx from 'clsx';

export interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'accent' | 'subtle';
}

const sizeMap = {
  sm: 'h-4 w-4 border-2',
  md: 'h-6 w-6 border-2',
  lg: 'h-8 w-8 border-2'
};

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', variant = 'accent', className, ...rest }) => {
  return (
    <div
      className={clsx('animate-spin rounded-full border-b-transparent', sizeMap[size], variant === 'accent' ? 'spinner-accent' : 'border-border-muted', className)}
      {...rest}
    />
  );
};

export default Spinner;
