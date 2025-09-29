import React from 'react';
import clsx from 'clsx';

export interface StatChipProps extends React.HTMLAttributes<HTMLDivElement> {
  label: React.ReactNode;
  value: React.ReactNode;
  tone?: 'neutral' | 'accent';
  size?: 'sm' | 'md';
}

const base = 'inline-flex items-center gap-1 rounded-full border border-border-subtle font-medium';
const sizeCls = { sm: 'text-[10px] px-2 py-0.5', md: 'text-xs px-3 py-1' };

export const StatChip: React.FC<StatChipProps> = ({ label, value, tone = 'neutral', size = 'sm', className, ...rest }) => {
  return (
    <div
      className={clsx(base, sizeCls[size], tone === 'accent' && 'bg-accent/10 border-[var(--color-accent)] text-secondary', className)}
      {...rest}
    >
      <span className="font-semibold">{value}</span>
      <span className="text-muted font-normal">{label}</span>
    </div>
  );
};

export default StatChip;
