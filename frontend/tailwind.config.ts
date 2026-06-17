import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0e6ff',
          100: '#d9c2ff',
          200: '#c099ff',
          300: '#a670ff',
          400: '#8c47ff',
          500: '#7c3aed',
          600: '#6d28d9',
          700: '#5b21b6',
          800: '#4c1d95',
          900: '#3b0d7a',
          DEFAULT: '#7c3aed',
        },
        secondary: {
          50: '#e6f0ff',
          100: '#c2d9ff',
          200: '#99bfff',
          300: '#70a4ff',
          400: '#478aff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          DEFAULT: '#3b82f6',
        },
        accent: {
          50: '#f0fafb',
          100: '#ccf2f4',
          200: '#99e6ea',
          300: '#66d9e0',
          400: '#33ccd6',
          500: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
          DEFAULT: '#06b6d4',
        },
        dark: {
          50: '#f8f9fa',
          100: '#e9ecef',
          200: '#dee2e6',
          300: '#adb5bd',
          400: '#6c757d',
          500: '#495057',
          600: '#343a40',
          700: '#212529',
          800: '#1a1a2e',
          900: '#0f0f0f',
          DEFAULT: '#1a1a2e',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
    },
  },
  plugins: [],
}

export default config
