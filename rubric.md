# Day 18 Lab — Grading Rubric (100 pts)

Maps 1-to-1 với slide deliverable (4 bullets). Track-2 Daily Lab weight = 30%.

| # | Notebook | Criterion | Pts |
|---|---|---|---:|
| 1 | `01_delta_basics` | Delta table created in MinIO; `_delta_log/` visible | 10 |
| 1 | `01_delta_basics` | Schema enforcement blocks invalid write | 5 |
| 1 | `01_delta_basics` | Schema evolution adds column via `mergeSchema=true` | 5 |
| 2 | `02_optimize_zorder` | Reproduce small-file problem (≥ 100 files before) | 5 |
| 2 | `02_optimize_zorder` | OPTIMIZE+ZORDER speedup ≥ 3× (point-query benchmark) | 15 |
| 2 | `02_optimize_zorder` | `numFiles` decreased meaningfully after OPTIMIZE | 5 |
| 3 | `03_time_travel` | DESCRIBE HISTORY shows ≥ 5 versions | 5 |
| 3 | `03_time_travel` | MERGE upsert 100K rows succeeds | 10 |
| 3 | `03_time_travel` | RESTORE rolls back bad data in < 30 s | 10 |
| 4 | `04_medallion`    | Bronze, Silver, Gold tables all exist in MinIO | 10 |
| 4 | `04_medallion`    | Silver dedup removes duplicates correctly | 5 |
| 4 | `04_medallion`    | Gold aggregations correct (p50/p95, cost, error_rate) | 10 |
| — | All notebooks     | Code is reproducible from clean `docker compose up` | 5 |
|   |                   | **Total** | **100** |

## Submission

Push your work to: `<your-username>/Day18-Track2-Lakehouse-Lab` (fork) and open a
PR back to the upstream. Include:

1. The 4 executed notebooks (committed with output cells)
2. A `submission/screenshots/` folder: MinIO console showing `_delta_log/` + buckets
3. A short `submission/REFLECTION.md` (≤ 200 words): which anti-pattern from slide §5
   would you be most at risk of in your team's data, and why?

## Late policy / regrade

Standard Track-2 policy applies — see `INDEX-Track2.md`.
