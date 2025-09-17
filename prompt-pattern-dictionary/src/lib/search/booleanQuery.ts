// Boolean query parsing & evaluation with basic AND / OR / NOT support, quoted phrases, and fuzzy suffix.
// Fuzzy suffix syntax: term~1 (edit distance <=1), term~2, etc. Default fuzzy distance comes from caller.
// Operator precedence: NOT > AND > OR. Parentheses not supported (future enhancement).

export type TermNode = { type: 'TERM'; value: string; fuzzy?: number; phrase?: boolean };
export type NotNode = { type: 'NOT'; child: Node };
export type AndNode = { type: 'AND'; left: Node; right: Node };
export type OrNode = { type: 'OR'; left: Node; right: Node };
export type Node = TermNode | NotNode | AndNode | OrNode;

export interface ParseResult {
  root: Node | null;
  terms: TermNode[];
}

// Token representation
interface Token { type: 'AND' | 'OR' | 'NOT' | 'TERM'; raw: string; }

const OP_AND = 'AND';
const OP_OR = 'OR';
const OP_NOT = 'NOT';

export function parseBooleanQuery(input: string): ParseResult {
  const trimmed = input.trim();
  if (!trimmed) return { root: null, terms: [] };

  const tokens = tokenize(trimmed);
  if (tokens.length === 0) return { root: null, terms: [] };

  // Shunting-yard like single-pass respecting NOT > AND > OR without parentheses.
  // First handle NOT (unary) by folding into following TERM.
  const afterNot: Token[] = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.type === OP_NOT) {
      const next = tokens[i + 1];
      if (!next || next.type !== 'TERM') continue; // stray NOT ignored
      // Mark term as NOT using a pseudo token type
      afterNot.push({ type: 'TERM', raw: `!${next.raw}` });
      i++; // skip next
    } else {
      afterNot.push(t);
    }
  }

  // Reduce AND
  const andReduced: (Token | Node)[] = [];
  let i = 0;
  while (i < afterNot.length) {
    const current = afterNot[i];
    if (current.type === 'TERM') {
      let leftNode: Node = termFromRaw(current.raw);
      // Consume chains of AND
      while (i + 1 < afterNot.length && afterNot[i + 1].type === OP_AND) {
        const termTok = afterNot[i + 2];
        if (!termTok || termTok.type !== 'TERM') break;
        const rightNode = termFromRaw(termTok.raw);
        leftNode = { type: 'AND', left: leftNode, right: rightNode };
        i += 2; // skip AND and term
      }
      andReduced.push(leftNode);
    } else if (current.type === OP_AND) {
      // already consumed in chain; skip
    } else {
      andReduced.push(current);
    }
    i++;
  }

  // Reduce OR (left to right)
  let root: Node | null = null;
  i = 0;
  while (i < andReduced.length) {
    const item = andReduced[i];
    if (isNode(item)) {
      if (!root) {
        root = item;
      } else {
        // Consecutive nodes without OR -> implicit AND (already handled earlier)
        root = { type: 'AND', left: root, right: item };
      }
    } else if ((item as Token).type === OP_OR) {
      // Next must be node
      const next = andReduced[i + 1];
      if (next && isNode(next)) {
        root = { type: 'OR', left: root || next, right: next };
        i++; // skip next; will be added by assignment above
      }
    }
    i++;
  }

  // Collect term nodes
  const terms: TermNode[] = [];
  if (root) collectTerms(root, terms);
  return { root, terms };
}

function tokenize(input: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < input.length) {
    const ch = input[i];
    if (ch === ' ' || ch === '\t' || ch === '\n') { i++; continue; }
    if (ch === '"' || ch === '\'') {
      // Quoted phrase
      const quote = ch;
      let j = i + 1; let buf = '';
      while (j < input.length && input[j] !== quote) { buf += input[j]; j++; }
      if (j < input.length) {
        tokens.push({ type: 'TERM', raw: `"${buf}"` });
        i = j + 1; continue;
      } else {
        // Unterminated quote: treat remaining as single term
        tokens.push({ type: 'TERM', raw: input.slice(i) });
        break;
      }
    }
    // Normal term/operator
    let j = i; let raw = '';
    while (j < input.length && !/\s/.test(input[j])) { raw += input[j]; j++; }
    const upper = raw.toUpperCase();
    if (upper === OP_AND || upper === OP_OR || upper === OP_NOT) {
      tokens.push({ type: upper as Token['type'], raw });
    } else {
      tokens.push({ type: 'TERM', raw });
    }
    i = j;
  }
  return tokens;
}

function termFromRaw(raw: string): TermNode | NotNode {
  let negated = false;
  if (raw.startsWith('!')) { negated = true; raw = raw.slice(1); }
  let phrase = false;
  if (raw.startsWith('"') && raw.endsWith('"')) {
    phrase = true;
    raw = raw.slice(1, -1);
  }
  // Fuzzy suffix detection: word~2
  let fuzzy: number | undefined;
  const fuzzyMatch = raw.match(/^(.*)~(\d)$/);
  if (fuzzyMatch) {
    raw = fuzzyMatch[1];
    fuzzy = parseInt(fuzzyMatch[2], 10);
  }
  const node: TermNode = { type: 'TERM', value: raw.toLowerCase(), fuzzy, phrase };
  return negated ? { type: 'NOT', child: node } : node;
}

function isNode(obj: unknown): obj is Node {
  if (!obj || typeof obj !== 'object') return false;
  const t = (obj as { type?: string }).type;
  return t === 'TERM' || t === 'NOT' || t === 'AND' || t === 'OR';
}

function collectTerms(node: Node, acc: TermNode[]) {
  switch (node.type) {
    case 'TERM': acc.push(node); break;
    case 'NOT': collectTerms(node.child, acc); break;
    case 'AND': collectTerms(node.left, acc); collectTerms(node.right, acc); break;
    case 'OR': collectTerms(node.left, acc); collectTerms(node.right, acc); break;
  }
}

// Levenshtein distance with early exit if distance > max.
export function levenshtein(a: string, b: string, max: number): number {
  if (a === b) return 0;
  if (Math.abs(a.length - b.length) > max) return max + 1;
  const v0 = new Array(b.length + 1).fill(0);
  const v1 = new Array(b.length + 1).fill(0);
  for (let i = 0; i <= b.length; i++) v0[i] = i;
  for (let i = 0; i < a.length; i++) {
    v1[0] = i + 1;
    let minRow = v1[0];
    for (let j = 0; j < b.length; j++) {
      const cost = a[i] === b[j] ? 0 : 1;
      v1[j + 1] = Math.min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost);
      if (v1[j + 1] < minRow) minRow = v1[j + 1];
    }
    if (minRow > max) return max + 1; // early exit
    for (let j = 0; j <= b.length; j++) v0[j] = v1[j];
  }
  return v1[b.length];
}

export interface EvaluateOptions {
  defaultFuzzy?: number; // default max distance if term specifies none
  // Candidate text provider: returns array of strings to test for membership.
  fields: string[];
}

export function evaluateBooleanQuery(root: Node | null, opts: EvaluateOptions): boolean {
  if (!root) return true; // no query -> match (caller handles empty query logic)
  function evalNode(n: Node): boolean {
    switch (n.type) {
      case 'TERM': return termMatches(n, opts);
      case 'NOT': return !evalNode(n.child);
      case 'AND': return evalNode(n.left) && evalNode(n.right);
      case 'OR': return evalNode(n.left) || evalNode(n.right);
    }
  }
  return evalNode(root);
}

function termMatches(term: TermNode, opts: EvaluateOptions): boolean {
  const { fields, defaultFuzzy = 0 } = opts;
  const fuzzy = term.fuzzy != null ? term.fuzzy : defaultFuzzy;
  const value = term.value.toLowerCase();
  // For phrase: direct substring across fields
  if (term.phrase) {
    return fields.some(f => f.includes(value));
  }
  // Quick exact / substring check
  if (fields.some(f => f.includes(value))) return true;
  if (fuzzy <= 0) return false;
  // Fuzzy: compare against tokenized words
  const wordSet: string[] = [];
  fields.forEach(f => {
    f.split(/[^a-z0-9]+/).forEach(w => { if (w) wordSet.push(w); });
  });
  for (const w of wordSet) {
    if (Math.abs(w.length - value.length) > fuzzy) continue;
    const dist = levenshtein(value, w, fuzzy);
    if (dist <= fuzzy) return true;
  }
  return false;
}
