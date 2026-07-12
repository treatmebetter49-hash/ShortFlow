/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      colors: {
        ink: "#060608",
        "ink-2": "#0A0A0C",
        gold: "#CFA347",
        silver: "#9A9AA4",
      },
    },
  },
  plugins: [],
};
