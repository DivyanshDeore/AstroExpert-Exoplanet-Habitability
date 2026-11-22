# Architecture

React + TypeScript + Tailwind frontend → FastAPI REST API → SQLAlchemy → SQLite.
The inference layer loads JSON IF–THEN rules and uses forward chaining. The catalogue is bundled locally in `backend/app/data/exoplanets.json`; no live NASA API integration is present.

## Main endpoints
- `GET /api/overview`
- `GET /api/planets?q=`
- `GET /api/planets/{id}`
- `POST /api/planets/{id}/favorite`
- `GET /api/favorites`
- `POST /api/assess`
- `GET /api/assessments`

SQLite tables: `planets`, `assessments`.
