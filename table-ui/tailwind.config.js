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
        mag: "#FF3D8A",
        cy: "#26D7F4",
      },
    },
  },
  plugins: [],
};
