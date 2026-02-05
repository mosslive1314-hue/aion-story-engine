/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'cosmic-blue': '#0B1426',
        'nebula-purple': '#1E1B3E',
        'star-white': '#E8E9F3',
        'plasma-pink': '#FF00AA',
        'quantum-green': '#00FF88',
      },
      backgroundImage: {
        'cosmic-gradient': 'linear-gradient(135deg, #0B1426 0%, #1E1B3E 100%)',
        'plasma-gradient': 'linear-gradient(90deg, #FF00AA 0%, #00FF88 100%)',
      },
    },
  },
  plugins: [],
}
