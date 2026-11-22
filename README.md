# AstroExpert — Offline Exoplanet Catalogue Edition

AstroExpert is a React + TypeScript frontend with a FastAPI backend and SQLite persistence. It provides a searchable local exoplanet catalogue and explainable, rule-based habitability screening.

## Included
- Dashboard, searchable exoplanet explorer and planet profiles.
- Compare up to three planets.
- Favorites and assessment history.
- Rule-based habitability screening with fired-rule explanations.
- Methodology and scientific limitations.
- Bundled JSON/CSV catalogue; no live NASA API search or import endpoint.

## Dataset scope and provenance
- Snapshot date: **2026-11-22** (the date this uploaded export was supplied).
- Source: **NASA Exoplanet Archive — PSCompPars**.
- The supplied export contains **6,470 planet rows and 703 columns** (verified from the attached CSV).
- The original full export is preserved unchanged at `DATASET.csv` and `backend/app/data/nasa_pscomppars_full.csv`.
- The application catalogue is derived from all 6,470 rows and is bundled in `backend/app/data/exoplanets.json` and `backend/app/data/exoplanets.csv`.
- The frontend offline fallback also contains all 6,470 normalized records.
- The normalized application fields are mapped from NASA columns: `pl_name`, `hostname`, `discoverymethod`/`disc_method`, `disc_year`, `pl_rade`, `pl_bmasse`, `pl_orbper`, `pl_orbsmax`, `st_lum`, `st_teff`, and `pl_insol`.
- NASA `st_lum` is log10(L/Lsun); AstroExpert converts it to solar luminosity with `10 ** st_lum`. The original `st_lum` remains intact in the full raw CSV.
- Missing source measurements remain null. The app does not invent missing values.
- No live NASA connection is required at runtime; the supplied snapshot is bundled locally.

Official source: https://exoplanetarchive.ipac.caltech.edu/

## Scientific limitations
AstroExpert is an educational screening tool, not a validated habitability model. The habitable-zone approximation uses inner = 0.95√L AU and outer = 1.67√L AU. This is a simplified luminosity-scaled interval, not a temperature-dependent climate model. It cannot establish surface water, atmosphere, or life. Unknown measurements remain unknown. Radius alone does not prove rocky composition. Equilibrium temperature is not surface temperature. Some reported masses may be minimum masses or M sin(i); check the original source and uncertainty before academic use.

## Requirements
- Python 3.11+
- Node.js 20+

## Windows setup — backend
Open PowerShell in `AstroExpert_Complete`:

```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend docs: http://127.0.0.1:8000/docs

SQLite `astroexpert.db` is created automatically. No database server, account, API key or live NASA connection is required. On startup the app merges the bundled catalogue into SQLite while preserving favorites and assessment history.

## Windows setup — frontend
Open a second terminal at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, usually http://localhost:5173.

## Tests
From `backend` with the virtual environment active:

```powershell
python -m pytest -v
```

## Frontend production build

```powershell
cd frontend
npm install
npm run build
```
