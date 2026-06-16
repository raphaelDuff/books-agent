# books-agent frontend

Minimal React + Vite UI for the Book Recommender Agent.

## Run

```bash
npm install
npm run dev
```

Opens on http://localhost:5173. API calls to `/books/recommendations` are
proxied to the FastAPI backend on http://localhost:8000 (see `vite.config.js`),
so start the backend first.

## What it shows

- A query box plus example chips.
- The classified intent (STRUCTURED / SEMANTIC / HYBRID).
- The generated SQL (transparency panel) when the structured branch ran.
- A ranked list: cover, title, author/year/rating, and the one-line "why".

`thread_id` from the response is sent back on the next request (conversation
plumbing; follow-up reference resolution is a later extension).
