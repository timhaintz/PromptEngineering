export function readingTimeFromWords(wordCount: number, wpm: number = 200): string {
  if (!wordCount || wordCount <= 0) return '1 min';
  const minutes = wordCount / wpm;
  if (minutes < 1) return '1 min';
  const rounded = Math.ceil(minutes);
  return `${rounded} min`;
}
