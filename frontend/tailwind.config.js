/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: '#131317',
        'surface-dim': '#131317',
        'surface-bright': '#39393d',
        'surface-container-lowest': '#0e0e12',
        'surface-container-low': '#1b1b20',
        'surface-container': '#1f1f23',
        'surface-container-high': '#28282c',
        'surface-container-highest': '#333337',
        'on-surface': '#e4e1e6',
        'on-surface-variant': '#c8c5d0',
        outline: '#91909a',
        'outline-variant': '#47464f',
        primary: '#b4b7ff',
        'on-primary': '#1a1d60',
        'primary-container': '#333678',
        'on-primary-container': '#dee0ff',
        secondary: '#c2c5dd',
        'on-secondary': '#2c2f42',
        'secondary-container': '#424559',
        'on-secondary-container': '#dee1f9',
        tertiary: '#e3badb',
        'on-tertiary': '#43273f',
        'tertiary-container': '#5c3d57',
        'on-tertiary-container': '#ffd7f4',
        error: '#ffb4ab',
        'on-error': '#690005',
        'error-container': '#93000a',
        'on-error-container': '#ffdad6',
        
        // Empathy-first sentiment palette
        'sentiment-positive': '#81b29a',
        'sentiment-negative': '#e07a5f',
        'sentiment-neutral': '#94a3b8',
      },
      fontFamily: {
        sans: ['Manrope', 'sans-serif'],
      },
      spacing: {
        'gutter': '16px',
        'card-padding': '20px',
        'section-gap': '32px',
        'component-gap': '12px',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '16px',
        'xl': '28px',
      },
      boxShadow: {
        'sm': '0 2px 4px rgba(0, 0, 0, 0.2)',
        'md': '0 4px 8px rgba(0, 0, 0, 0.3)',
      }
    },
  },
  plugins: [],
}
