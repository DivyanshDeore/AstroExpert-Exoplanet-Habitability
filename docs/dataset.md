# AstroExpert dataset

## Source and coverage
- Source: NASA Exoplanet Archive, `PSCompPars` table.
- Snapshot received: 2026-11-19.
- Uploaded source file: 6,470 rows × 703 columns.
- The original CSV is preserved byte-for-byte as `backend/app/data/nasa_pscomppars_full.csv` and at project root as `DATASET.csv`.
- All 6,470 rows are mapped into the app catalogue (`backend/app/data/exoplanets.json`, `backend/app/data/exoplanets.csv`) and frontend offline fallback (`frontend/src/data/exoplanets.ts`).

## Field mapping
| AstroExpert field | NASA source column |
|---|---|
| name | `pl_name` |
| host_star | `hostname` |
| discovery_method | `discoverymethod`, fallback `disc_method` |
| discovery_year | `disc_year` |
| radius_earth | `pl_rade` |
| mass_earth | `pl_bmasse` |
| orbital_period_days | `pl_orbper` |
| semi_major_axis_au | `pl_orbsmax` |
| stellar_luminosity_solar | `10 ** st_lum` |
| stellar_temperature_k | `st_teff` |
| insolation_earth | `pl_insol` |

NASA `st_lum` is logarithmic, log10(L/Lsun), so AstroExpert converts it to linear solar luminosity for calculations. The raw source file retains the original value and every other column.

## Data quality
Blank values are retained as null in the normalized catalogue. A missing semi-major axis or luminosity prevents a corresponding orbital/HZ calculation; it is not treated as zero. This is a dated local snapshot and does not automatically update when NASA adds records.

## Official source
https://exoplanetarchive.ipac.caltech.edu/
