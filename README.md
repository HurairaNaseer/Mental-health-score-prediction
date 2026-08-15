# Mental Health Score Prediction — Frontend

React + TypeScript + Tailwind dashboard that talks to your FastAPI `/predict`
backend (from the earlier `main.py`).

## Stack
- React 18 + TypeScript, built with Vite
- Tailwind CSS for styling
- Native `fetch` for API calls (no extra HTTP library needed)
- Animation via CSS transitions/keyframes (kept dependency-free — swap in
  `framer-motion` yourself if you want spring physics; `npm i framer-motion`
  and wrap elements in `<motion.div>`)

## Setup

```bash
npm install
cp .env.example .env      # point VITE_API_URL at your backend if not localhost:8000
npm run dev
```

Open the printed local URL (usually `http://localhost:5173`). Make sure the
FastAPI backend is running on `http://localhost:8000` (or whatever you set
in `.env`) with CORS enabled for your frontend origin — add this to your
`main.py` if you haven't already:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Project structure
```
src/
  App.tsx        — main dashboard: form + result gauge + toasts
  api.ts         — typed fetch wrapper + country-grouping logic
  types.ts       — shared TypeScript types matching the backend Pydantic model
  index.css      — Tailwind entry + custom fonts
  main.tsx       — React root
```

## What's implemented against your requirements
- **UI/UX**: dark "wellbeing dashboard" theme, animated result gauge, hover/press
  micro-interactions, responsive grid (stacks to one column on mobile/tablet).
- **Input form**: every field from your spec, correctly typed as number
  input, dropdown, or segmented control. `Mental_Health_Score` is **not** an
  input (it's the model's target/output) and `Country_Grouped` is a
  read-only derived badge, not a separate field — see the note in chat for why.
- **API integration**: `predictMentalHealthScore()` in `api.ts` does the
  `fetch` POST to `/predict`, parses the JSON response, and throws a typed
  error the UI catches.
- **Result display**: animated circular gauge that sweeps to the predicted
  score with a color/label (Thriving / Steady / At risk).
- **Loading & feedback**: button + gauge switch to a loading state during
  the request; success and error toasts appear top-right and auto-dismiss.

## Notes
- This project could not be `npm install`-ed inside the sandbox that generated
  it (no network access there), so run `npm install` and `npx tsc --noEmit`
  yourself as a first check.
- The live in-chat preview (`App.jsx` artifact) uses a plain `<script>`
  Google Fonts import and a client-side fallback estimate if the API is
  unreachable, purely so you can see it working without a backend running.
  This TypeScript version (`src/App.tsx`) has that fallback removed — it
  shows a real error toast instead, which is what you want in production.
