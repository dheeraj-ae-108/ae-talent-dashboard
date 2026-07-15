# Arctic Engine — Talent Pool Analytics Dashboard

An interactive, single-file dashboard over the Arctic Engine 10+ years-experience
candidate pool. Mirrors the "Helium16" talent-pool layout, adapted to the fields
that actually exist in the AE export.

## Data sources (two)
1. **Person-level CSV export** (`arctic_engines___10__years_exp_candidates_*.csv`) — truncated at 1,048,575 rows (916,607 unique candidates). Used where per-person joins or the **language filter** are needed. Panels tagged `export sample`.
2. **Distinct-count sheets** (`Arctic Engine _ Data Req.xlsx`) — authoritative frequency tables for the full **1,402,050-record** pool (sheets: Job Title, Org Name, Sub department, Spec). Used for tech stack, company tier, top employers, sub-departments, specializations, PhD-by-domain. Panels tagged `full pool`.

## Files
| File | Purpose |
|------|---------|
| `aggregate.py` | Reads the raw candidate CSV → writes compact `ae_data.json` (person-level + per-language cross-tabs). |
| `aggregate_xlsx.py` | Merges full-pool distributions from the xlsx into `ae_data.json` (adds the `full` block). Run **after** `aggregate.py`. |
| `ae_data.json` | ~40 KB pre-aggregated data (no PII, no raw rows). |
| `build_dashboard.py` | Inlines `ae_data.json` into `index.html`. |
| `index.html` | Self-contained dashboard (ECharts via CDN). This is the only file GitHub Pages needs. |

## Regenerate from new exports
```bash
python3 aggregate.py "/path/to/new_export.csv"        # -> ae_data.json (export-sample panels)
python3 aggregate_xlsx.py "/path/to/Data Req.xlsx"    # -> merges full-pool panels
python3 build_dashboard.py                            # -> index.html
```

## Theme
Matches **arcticengine.ai** — light warm off-white page (`#f4f4f2`), dark ink header bar (`#15171b`) with a teal accent border, deep-teal/emerald primary (`#0e7c72` / `#0f8a66`), mint highlight (`#2fe6af`). Chart palette and CSS vars live at the top of `build_dashboard.py` (`:root` block + the `PAL`/`AX`/`GRID` JS constants). Tags: teal = authoritative (`full pool` / `derived`), amber (`.tag.warn`) = caveat (`export sample` / `proxy`).

## View locally
```bash
python3 -m http.server 8777    # then open http://localhost:8777
```
(Opening `index.html` via `file://` also works — the data is inlined, no fetch.)

## Deploy to GitHub Pages
```bash
git init && git add index.html ae_data.json aggregate.py build_dashboard.py README.md
git commit -m "Arctic Engine talent-pool dashboard"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
Then in the repo: **Settings → Pages → Deploy from branch → main / root**.
Your live URL will be `https://<user>.github.io/<repo>/`.

> Do **not** commit the raw 130 MB CSV — `ae_data.json` is the only data the site needs.

## What the panels show
- **KPIs** — filtered candidate count, median/avg experience, PhD network size, tech pool size.
- **Language filter** — re-slices every filterable panel live (candidate spec requirement).
- **Domain segment share vs. median experience** — verticals derived from `department`.
- **Qualification levels** — highest degree per candidate.
- **Experience distribution / multi-lingual pool.**
- **PhD network** — by domain + top specializations (14.6K PhDs).
- **Tech / coding sub-cut** — department, **role-inferred stack/discipline**, **company tier**, experience band.
- **Company landscape** — whole-pool company tier + top employers in premium tiers.
- **Supporting context** — top departments + elite-institute keyword signal.

## Derived columns (added on top of the raw export)
- **Stack / discipline** — inferred per candidate from `job_title`. Explicit-language titles (Java/Python/.NET/PHP…) are counted directly; generic titles map to the nearest discipline (Backend, Data & Analytics, QA, Cloud/DevOps, Networking, Systems/IT Admin, ERP/SAP, Embedded, Mobile, Front-end). Mapping lives in `stack_bucket()` in `aggregate.py`.
- **Company tier** — assigned from `organization_name` via keyword lists: FAANG/global big-tech, Indian IT/consulting, unicorn/funded startup, BFSI/large enterprise, else Other. Editable in `company_tier()` / `_TIER_PATS` in `aggregate.py`.

## Data caveats (also shown in-page)
- **Source truncated** at the 1,048,575-row export cap → real pool is larger than the 916,607 unique candidates shown.
- **Stack is role-inferred, not self-reported** — ~57% of tech titles are generic and land in "Other/Unspecified"; treat language-level counts as directional.
- **Company tier is name-matched** — unmatched employers (incl. self-employed/govt/SMEs) fall to "Other".
- **Institute name is ~98% blank** → IIT/NIT/IIM figures are directional keyword matches, not a census.
- **No active-status field** → that cut is omitted.
- Only **10 regional languages** captured; Hindi/Urdu/Punjabi are absent from this export.
