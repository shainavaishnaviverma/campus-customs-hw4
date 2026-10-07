# Campus Customs — Yale Bulldog Blue

A Yale apparel storefront with an AI shopping assistant. React + Vite + TypeScript
front end, FastAPI + PydanticAI back end, SQLite catalogue.

The chat agent (four files under `backend/`): `prompts/prompt.md` (system prompt),
`agent.py` (wiring), `tools.py` (tools), `models.py` (structured types).

## What's not in this repo

To keep the repo clean and private data out of git, these are **excluded** and
must be provided locally (the "data pack"):

- `data/campus_customs.db` — the catalogue / inventory / users / chat database
- `data/products/` — the product images referenced by the catalogue
- `.env` — your real secrets (see `.env.example`)

After cloning, create the `data/` folder and drop in the data pack so the layout is:

```
hw4/
├── data/
│   ├── campus_customs.db
│   └── products/            # product images referenced by the catalogue
├── backend/
├── frontend/
└── output/
```

## 1. Configure the key

Copy the template and add your key (routes `gpt-5.6-luna` through Portkey → OpenAI):

```bash
cp .env.example .env
# edit .env and set PORTKEY_API_KEY=your-real-key
```

`.env` is git-ignored and must never be committed.

## 2. Run the back end (FastAPI, port 8000)

From `hw4/backend/`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r ../requirements.txt
.venv/bin/uvicorn main:app --reload --port 8000
```

API docs at http://127.0.0.1:8000/docs.

## 3. Run the front end (Vite, port 5173)

From `hw4/frontend/`:

```bash
npm install
npm run dev
```

Open http://127.0.0.1:5173. Vite proxies `/api` and `/media` to the backend on
port 8000, so start the back end first.

Seeded test login (from the data pack): `test@campuscustoms.yale.edu` / `password`.

## Docs

See `output/` for the build notes: `harness.md` (how the system works),
`design.md`, `usability.md`, `app_check.html` (screenshots), and the append-only
`audit_trail.json` of agent activity.
