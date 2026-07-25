# DevPort Dashboard (Frontend)

A minimal React dashboard wired to the DevPort backend: login/register, workspaces,
API key management, and usage analytics.

## Setup

This is a single component file (`DevPortDashboard.jsx`) built for a React +
Tailwind + `lucide-react` + `recharts` environment (e.g. Vite or Create React App).

1. Create a new React app (Vite recommended):
   ```bash
   npm create vite@latest devport-dashboard -- --template react
   cd devport-dashboard
   npm install lucide-react recharts
   ```
2. Set up Tailwind CSS (see https://tailwindcss.com/docs/guides/vite).
3. Copy `DevPortDashboard.jsx` into `src/`, and render it from `src/App.jsx`:
   ```jsx
   import DevPortDashboard from "./DevPortDashboard";
   export default function App() {
     return <DevPortDashboard />;
   }
   ```
4. Update `API_BASE` at the top of `DevPortDashboard.jsx` to point at your running
   backend (`http://localhost:8000` locally, or your Railway URL in production).
5. **Important:** the `useApi()` hook's token storage is stubbed out (see the comment
   in the code) because it was built inside an environment that blocks real browser
   storage. Swap the stub for real `window.localStorage.getItem` / `setItem` calls so
   login sessions persist across page refreshes in your actual deployment.
6. Make sure your FastAPI backend's CORS settings (`app/main.py`) include this
   frontend's origin (e.g. `http://localhost:5173` for Vite's default dev server).

## Run

```bash
npm run dev
```
