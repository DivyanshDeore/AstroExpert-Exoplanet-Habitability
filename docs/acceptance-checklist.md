# AstroExpert acceptance checklist

- [x] Raw NASA PSCompPars CSV retained unchanged.
- [x] 6,470 rows and 703 columns verified from the supplied file.
- [x] Full normalized 6,470-planet catalogue bundled.
- [x] SQLite-backed catalogue and assessment history.
- [x] Deterministic rule engine with forward chaining.
- [x] Unknown values are retained as null.
- [x] Offline operation; no NASA API calls.
- [x] Dashboard summary, search, compare, rules, metadata, and health endpoints.
- [ ] Frontend production build should be run on the target machine after `npm install`.
