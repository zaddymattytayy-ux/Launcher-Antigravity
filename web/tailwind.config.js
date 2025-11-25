/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'mu-dark': '#0a0a0a',
        'mu-panel': '#1a1a1a',
        'mu-accent': '#d4af37', // Gold
        'mu-text': '#e0e0e0',
      },
    },
  },
  plugins: [],
};
