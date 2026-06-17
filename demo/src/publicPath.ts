/** Public asset URL that works on root hosting (Netlify) and subpath hosting (GitHub Pages). */
export function publicPath(relativePath: string): string {
  const normalized = relativePath.replace(/^\//, '');
  return `${import.meta.env.BASE_URL}${normalized}`;
}
