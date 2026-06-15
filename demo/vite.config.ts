import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Netlify / local preview: default base '/'
// GitHub Pages project site: set VITE_BASE_PATH=/<repo-name>/ in CI
const base = process.env.VITE_BASE_PATH || '/';

// https://vitejs.dev/config/
export default defineConfig({
  base,
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});
