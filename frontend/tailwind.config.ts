import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      colors: {
        background: "#0f172a",
        surface: "#1e293b",
        "surface-2": "#293548",
        border: "#334155",
        primary: "#3b82f6",
        "primary-hover": "#2563eb",
        muted: "#64748b",
        foreground: "#f1f5f9",
        "foreground-muted": "#94a3b8",
      },
    },
  },
  plugins: [],
} satisfies Config;
