import React from 'react';
import clsx from 'clsx';

type BaseProps = {
  /** Visual heading content, not the native title attribute */
  heading?: React.ReactNode;
  meta?: React.ReactNode;
  interactive?: boolean;
  className?: string;
  children?: React.ReactNode;
};

type DivTile = BaseProps & Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> & { as?: 'div'; href?: undefined };
type AnchorTile = BaseProps & Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, 'title'> & { as?: 'a'; href: string };

export type TileProps = DivTile | AnchorTile;

/**
 * Tile component
 * Unified surface used across category, logic and other listing pages.
 * Consumes global .tile utility classes (theme.css). Additional classes extend spacing or layout only.
 */
export const Tile: React.FC<TileProps> = (props) => {
  if (props.as === 'a') {
    const { heading, meta, interactive = true, className, children, href, ...rest } = props as AnchorTile;
    return (
      <a
        href={href}
        className={clsx('tile', interactive && 'focus-ring', className)}
        {...rest}
      >
        {(heading || meta) && (
          <div className="flex items-center justify-between mb-0">
            {heading && <span className="tile-title">{heading}</span>}
            {meta && <span className="tile-meta">{meta}</span>}
          </div>
        )}
        {children}
      </a>
    );
  }
  const { heading, meta, interactive = true, className, children, ...divRest } = props as DivTile;
  return (
    <div
      className={clsx('tile', interactive && 'focus-ring', className)}
      {...divRest}
    >
      {(heading || meta) && (
        <div className="flex items-center justify-between mb-0">
          {heading && <span className="tile-title">{heading}</span>}
          {meta && <span className="tile-meta">{meta}</span>}
        </div>
      )}
      {children}
    </div>
  );
};

export default Tile;
