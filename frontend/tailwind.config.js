/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F19', // Deep navy
        surface: '#1A2235', // Slightly lighter surface
        primary: {
          DEFAULT: '#3B82F6', // Blue 500
          hover: '#60A5FA', // Blue 400
        },
        secondary: '#10B981', // Emerald for positive trends
        accent: '#8B5CF6', // Purple for AI insights
        warning: '#F59E0B',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
