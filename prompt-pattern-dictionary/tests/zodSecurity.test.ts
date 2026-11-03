import { createRequire } from 'node:module';
import type { ZodType } from 'zod/v4';

// Exercise the v4 validator actually resolved by the React Hooks linter.
const requireFromHooks = createRequire(require.resolve('eslint-plugin-react-hooks'));
const { z } = requireFromHooks('zod/v4') as typeof import('zod/v4');

type Collection = 'array.max' | 'array.length' | 'set.max';

function collectionSchema(kind: Collection, element: ZodType) {
  if (kind === 'array.max') return z.array(element).max(2);
  if (kind === 'array.length') return z.array(element).length(2);
  return z.set(element).max(2);
}

function collectionInput(kind: Collection, values: unknown[]) {
  return kind === 'set.max' ? new Set(values) : values;
}

describe('Zod collection size boundary (GHSA-mrhx-c7xc-m3w5)', () => {
  it.each<Collection>(['array.max', 'array.length', 'set.max'])('%s rejects oversized input before validating elements', kind => {
    let elementVisits = 0;
    const element = z.unknown().superRefine((_value, context) => {
      elementVisits++;
      context.addIssue({ code: 'custom', message: 'invalid element' });
    });
    // A bounded input demonstrates work amplification without risking memory exhaustion.
    const values = Array.from({ length: 1_000 }, (_, index) => index);
    const result = collectionSchema(kind, element).safeParse(collectionInput(kind, values));

    expect(result.success).toBe(false);
    expect(elementVisits).toBe(0);
    expect(result.error?.issues).toEqual([expect.objectContaining({ code: 'too_big', path: [] })]);
  });

  it.each<Collection>(['array.max', 'array.length', 'set.max'])('%s preserves validation and transforms within the size limit', kind => {
    let elementVisits = 0;
    const element = z.string().transform(value => {
      elementVisits++;
      return value.trim();
    });
    const output = collectionSchema(kind, element).parse(collectionInput(kind, [' first ', ' second ']));

    expect(output).toEqual(collectionInput(kind, ['first', 'second']));
    expect(elementVisits).toBe(2);
  });
});
