import { createRequire } from 'node:module';
import { SourceMapConsumer, SourceNode } from 'source-map-js';

// Resolve the renderer actually used by Mermaid, including nested npm layouts.
const requireFromMermaid = createRequire(require.resolve('mermaid'));
const katex = requireFromMermaid('katex') as {
  renderToString(expression: string, options?: { trust?: boolean }): string;
};

const basicMap = { version: '3', sources: ['local.js'], sourcesContent: ['local();'], names: [], mappings: 'AAAA' };

function indexedMap(line: number, map = basicMap) {
  return { ...basicMap, sections: [{ offset: { line, column: 0 }, map }] };
}

describe('source-map-js section offset boundary (GHSA-68fv-2mgg-jv7q)', () => {
  it.each([Number.MAX_SAFE_INTEGER, Infinity, 0.5, -1])('rejects invalid offset %s before source reconstruction', line => {
    expect(() => new SourceMapConsumer(indexedMap(line))).toThrow(/Section offset/);
  });

  it('rejects excessive cumulative offsets in nested sections', () => {
    expect(() => new SourceMapConsumer(indexedMap(6_000_000, indexedMap(6_000_000))))
      .toThrow(/including offsets of nested sections/);
  });

  it('preserves ordinary indexed mappings and generated source', () => {
    const consumer = new SourceMapConsumer(indexedMap(1));
    expect(consumer.originalPositionFor({ line: 2, column: 1 }))
      .toMatchObject({ source: 'local.js', line: 1, column: 0 });
    const code = 'header\nlocal();\n';
    expect(SourceNode.fromStringWithSourceMap(code, consumer).toString()).toBe(code);
  });
});

describe('KaTeX explicit trust boundary (GHSA-238p-pmpm-9mq7)', () => {
  it.each([
    String.raw`\href{https://example.invalid/}{link}`,
    String.raw`\includegraphics{https://example.invalid/image.png}`,
  ])('ignores inherited trust for %s', expression => {
    const options = Object.create({ trust: true });
    const html = katex.renderToString(expression, options);
    expect(html).not.toMatch(/<(a|img)\b/);
  });

  it('preserves ordinary maths and explicitly trusted links', () => {
    expect(katex.renderToString(String.raw`\frac{1}{2}`)).toContain('class="katex"');
    expect(katex.renderToString(String.raw`\href{https://example.invalid/}{link}`, { trust: true }))
      .toContain('href="https://example.invalid/"');
  });
});
