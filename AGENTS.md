# AGENTS.md — Team Sign-Off

## Stack
- **Backend**: FastAPI + SQLAlchemy async + SQLite (aiosqlite) + Pydantic-settings, Python 3.12, uv
- **Frontend**: Vue 3 + Pinia + Vue Router + Element Plus (zh-CN) + TypeScript, Vite, npm
- **Auth**: Keycloak OIDC (RS256 JWT), oidc-client-ts (frontend), jose + httpx JWKS fetch (backend)

## Entrypoints
- Backend app: `backend/app/main.py` (imported as `backend.app.*`)
- Frontend app: `frontend/src/main.ts`, alias `@` → `src/`
- Root `main.py` is a stub, not used at runtime

## Key commands
```sh
# Backend
uv sync                           # install deps (uv, not pip)
uv run uvicorn backend.app.main:app --reload   # dev server on :8000

# Frontend (in frontend/)
npm ci                            # install (use ci, not install)
npm run dev                       # vite dev on :5173
npm run build                     # vue-tsc -b && vite build
```

## Architecture notes
- All API routes require JWT auth (`get_current_user` dependency). Backend fetches JWKS from OIDC issuer at startup & caches.
- Users are auto-provisioned on first login (created from JWT claims).
- DB tables auto-created on startup via `Base.metadata.create_all` (no Alembic migrations applied — alembic.ini + env.py exist but `versions/` is empty).
- Dev mode: frontend proxies `/api` → `:8000` and `/realms` → external Keycloak (see `vite.config.ts`).
- Docker compose runs backend (uvicorn, multi-stage uv build) + frontend (nginx static).
- `.env` uses `APP_` prefix for backend settings. `frontend/.env` uses `VITE_` prefix.

## Gotchas
- ⚠️ `.env` and `.env.docker` both contain a real OIDC client secret — do not commit.
- No tests, no linter/formatter config anywhere in the repo.
- `backend/app/models/`, `schemas/`, `services/`, `middleware/` are each a single file (`__init__.py`), not split into modules.
- `frontend/src/composables/` is empty.
- `uv.lock` points to a Chinese PyPI mirror (`mirrors.ustc.edu.cn`).
