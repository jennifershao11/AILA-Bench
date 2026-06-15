/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#f6f3ee',
        ink: '#162132',
        muted: '#5f6774',
        line: 'rgba(22, 33, 50, 0.12)',
        card: 'rgba(255, 255, 255, 0.78)',
        accent: {
          DEFAULT: '#3f4f86',
          soft: '#54639c',
          tint: 'rgba(63, 79, 134, 0.10)',
        },
        teal: {
          DEFAULT: '#0f6c78',
          tint: 'rgba(15, 108, 120, 0.10)',
        },
      },
      fontFamily: {
        serif: ['Spectral', 'Iowan Old Style', 'Palatino Linotype', 'Georgia', 'serif'],
        sans: ['Inter', 'Avenir Next', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      boxShadow: {
        soft: '0 16px 44px rgba(22, 33, 50, 0.07)',
        card: '0 8px 24px rgba(22, 33, 50, 0.05)',
        lift: '0 22px 60px rgba(22, 33, 50, 0.12)',
      },
      borderRadius: {
        '2xl': '18px',
        '3xl': '24px',
      },
      letterSpacing: {
        eyebrow: '0.22em',
      },
    },
  },
  plugins: [],
};
