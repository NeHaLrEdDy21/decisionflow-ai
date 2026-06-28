/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b1020",
        panel: "#11182e",
        card: "#161f3a",
        accent: "#6366f1",
        muted: "#94a3b8",
      },
    },
  },
  plugins: [],
};
