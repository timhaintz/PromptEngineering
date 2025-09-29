declare module 'jest-axe' {
  import { AxeResults, RunOptions } from 'axe-core';
  export const axe: (container: HTMLElement, options?: RunOptions) => Promise<AxeResults>;
  export const toHaveNoViolations: {
    (results: AxeResults): {
      pass: boolean;
      message: () => string;
    };
  };
}

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace jest {
    interface Matchers<R, T = {}> {
      toHaveNoViolations(): R;
    }
  }
}
