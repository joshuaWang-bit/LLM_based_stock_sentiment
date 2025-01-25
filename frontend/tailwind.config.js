/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#00F0FF",
        secondary: "#7B42FF",
        accent: "#FF2E6C",
        quantum: "#39FF14",
        background: {
          start: "#0B1026",
          end: "#2A2F4E",
        },
        sentiment: {
          positive: "#39FF14",
          negative: "#FF3860",
          neutral: "#FFD700",
        },
      },
      backdropBlur: {
        glass: "20px",
      },
    },
  },
  plugins: [],
}
