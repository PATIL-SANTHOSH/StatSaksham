/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          sidebar: "#0C1E38",
          sidebarHover: "#162B4C",
          sidebarActive: "#2563EB",
          primary: "#0B1F3F",
          accent: "#2563EB",
          accentHover: "#1D4ED8",
          bg: "#F8FAFC",
          card: "#FFFFFF",
          border: "#E2E8F0",
          textMain: "#0F172A",
          textMuted: "#64748B",
        },
        gov: {
          navy: "#0C1E38",
          navyDark: "#081528",
          blue: "#1E3A8A",
          lightBlue: "#EFF6FF",
          accent: "#2563EB",
          gold: "#D97706",
          goldLight: "#FEF3C7",
          green: "#059669",
          greenLight: "#D1FAE5",
          red: "#DC2626",
          redLight: "#FEE2E2",
          grayBg: "#F8FAFC",
          cardBg: "#FFFFFF",
          border: "#E2E8F0"
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
