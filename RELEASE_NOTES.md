# LaRojaFan consolidated staging release — 2026-11-04

**Deploy to `analytics-integration-Copy`, not directly to `main`.**

Includes consent-gated GA4, Amazon disclosure (generic promotions remain off), player-photo and match-statistics display support, source metadata requirements, and generated pages. GA4 and Amazon IDs are configured in `config.json` and substituted into generated `docs/analytics.js`. Removes the outdated phrase-based 2026 World Cup publishing prohibition; this does **not** certify any tournament result.

**Not yet populated:** licensed player photographs, verified career records, and sourced match statistics. The site shows placeholders or unavailable notices. Do not describe these as complete.

**Before merge:** review privacy/legal text and contact channel, confirm all files are preserved, and verify Pages remains `main` `/docs`. The repository's automated daily update workflow may change generated pages; review changes after merge.

**Web upload:** GitHub's upload form may not reliably replace the complete nested `docs` tree. Prefer GitHub Desktop or a git CLI push for this large release.

**Build:** `python3 build.py && python3 validate_site.py`.
