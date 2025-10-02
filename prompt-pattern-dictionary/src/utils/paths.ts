const rawBasePath = process.env.NEXT_PUBLIC_BASE_PATH ?? '';
const normalizedBasePath = rawBasePath === '/' ? '' : rawBasePath;

const shouldBypass = (path: string) => {
  const trimmed = path.trim();
  return (
    trimmed === '' ||
    trimmed.startsWith('#') ||
    trimmed.startsWith('http://') ||
    trimmed.startsWith('https://') ||
    trimmed.startsWith('mailto:') ||
    trimmed.startsWith('tel:')
  );
};

const ensureLeadingSlash = (path: string) => (path.startsWith('/') ? path : `/${path}`);

export const withBasePath = (path: string) => {
  if (shouldBypass(path) || !normalizedBasePath) {
    return path;
  }

  const normalizedPath = ensureLeadingSlash(path);
  if (normalizedPath.startsWith(normalizedBasePath + '/')) {
    return normalizedPath;
  }

  return `${normalizedBasePath}${normalizedPath}`;
};

export const basePath = normalizedBasePath;
