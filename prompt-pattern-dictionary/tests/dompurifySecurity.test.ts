import { createRequire } from 'node:module';
import type { DOMPurify } from 'dompurify';

// Exercise the sanitizer resolved by the production Mermaid renderer.
const createDOMPurify = createRequire(require.resolve('mermaid'))('dompurify') as DOMPurify;

describe('DOMPurify security boundaries', () => {
  it.each(['{{probe}}', '${probe}', '<%probe%>'])('scrubs split shadow-root template %s (GHSA-cg2g-xh64-v4q7)', expression => {
    const host = document.createElement('div');
    const shadow = host.attachShadow({ mode: 'open' });
    for (const character of expression) {
      shadow.append(document.createTextNode(character), document.createElement('object'));
    }
    const label = document.createElement('span');
    label.textContent = 'safe label';
    shadow.append(label);

    createDOMPurify(window).sanitize(host, { IN_PLACE: true, SAFE_FOR_TEMPLATES: true });

    expect(shadow.textContent).not.toContain(expression);
    expect(shadow.textContent).toContain('safe label');
  });

  it.each(['parent', 'sibling'])('neutralizes a hook-detached %s (GHSA-mrv2-3pqr-j5jr)', mode => {
    const sanitizer = createDOMPurify(window);
    const root = document.createElement('div');
    root.innerHTML = '<section><img data-remove="1"><img data-target="1" onerror="void(0)"></section><p>safe label</p>';
    const target = root.querySelector('[data-target]')!;
    sanitizer.addHook('afterSanitizeAttributes', node => {
      if (node.getAttribute('data-remove') === '1') {
        if (mode === 'parent') node.parentElement?.remove();
        else node.nextElementSibling?.remove();
      }
    });

    sanitizer.sanitize(root, { IN_PLACE: true });

    expect(target.hasAttribute('onerror')).toBe(false);
    expect(root.textContent).toBe('safe label');
  });

  it.each(['text/html', 'application/xhtml+xml'] as const)('rejects SMIL href mutation in %s (GHSA-c6gr-qvv4-5v3f)', mediaType => {
    const output = createDOMPurify(window).sanitize(
      '<svg xmlns="http://www.w3.org/2000/svg"><a><animate attributeName="href" values="safe;javascript:void(0)"/><text>safe label</text></a></svg>',
      { PARSER_MEDIA_TYPE: mediaType, ADD_TAGS: ['animate'], ADD_ATTR: ['attributeName'] },
    );
    expect(output).not.toMatch(/attributeName="href"/i);
    expect(output).toContain('safe label');
    expect(output).toContain('<svg');
  });

  it('preserves normal diagram SVG while removing script and event handlers', () => {
    const output = createDOMPurify(window).sanitize('<svg><script>void(0)</script><g onclick="void(0)"><text>diagram</text></g></svg>');
    expect(output).not.toMatch(/<script|onclick/);
    expect(output).toContain('<text>diagram</text>');
  });
});
