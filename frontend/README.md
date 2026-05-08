# Chinook Insights — Frontend

React + Vite + TypeScript frontend for the Chinook Insights dashboard generator.

## Prerequisites

- Node.js 18 or higher
- npm or pnpm
- The **backend** running on `http://localhost:8000` (see `../backend/README.md`)

## Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Run the development server

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

The Vite dev server automatically proxies `/api/*` requests to `http://localhost:8000`, so the backend and frontend work together without any CORS issues.

## How it works

1. Enter KPI keywords (e.g. "revenue", "top customers", "sales by country") — press Enter after each one to add them as chips
2. Optionally set a Session ID and toggle Verbose mode
3. Click **Generate Dashboard** — the request is sent to the backend API
4. The AI agent queries the Chinook database and returns a complete HTML dashboard
5. The dashboard is rendered in a sandboxed `<iframe>` directly in the browser

## Build for production

```bash
npm run build
```

Output is in the `dist/` folder. Serve it with any static file server. Make sure to point your web server to proxy `/api` requests to your backend.

Example with `nginx`:
```nginx
location /api/ {
    proxy_pass http://localhost:8000/;
}

location / {
    root /path/to/frontend/dist;
    try_files $uri $uri/ /index.html;
}
```

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx        # App entry point, React Query setup
│   ├── App.tsx         # Root component, dark mode setup
│   ├── index.css       # Tailwind base styles
│   └── pages/
│       └── Home.tsx    # Main page — input panel + dashboard preview
├── index.html          # HTML entry point
├── package.json        # Dependencies
├── vite.config.ts      # Vite config + API proxy
├── tailwind.config.ts  # Tailwind theme (dark navy palette)
├── tsconfig.json       # TypeScript config
└── postcss.config.js   # PostCSS config
```

## Tech Stack

- **React 18** — UI library
- **Vite** — build tool and dev server
- **TypeScript** — type safety
- **Tailwind CSS** — utility-first styling
- **TanStack Query** — async state management for the API call
- **Framer Motion** — animations for KPI chips and toast notifications
- **Lucide React** — icons
