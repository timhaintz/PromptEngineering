'use client';

import dynamic from 'next/dynamic';
import React from 'react';

export const ClientDecisionTree = dynamic(
  () => import('./DecisionTreeWidget').then((mod) => ({ default: mod.DecisionTreeWidget })),
  {
    ssr: false,
    loading: () => <p className="text-xs text-muted">Loading decision aid…</p>
  }
);
