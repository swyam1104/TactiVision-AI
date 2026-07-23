/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d10",
        card: "#12181d",
        border: "#1e293b",
        pitch: {
          dark: "#0b2612",
          lines: "rgba(255, 255, 255, 0.4)",
          grass: "#164e26",
          goal: "#22c55e"
        },
        primary: {
          DEFAULT: "#22c55e",
          foreground: "#ffffff"
        },
        muted: {
          DEFAULT: "#64748b",
          foreground: "#94a3b8"
        }
      },
    },
  },
  plugins: [],
}
