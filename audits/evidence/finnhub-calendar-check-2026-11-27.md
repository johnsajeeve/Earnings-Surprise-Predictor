# Finnhub earnings calendar check (27 November 2026)

Run while answering what should replace Yahoo (decision C-61). No plan was written before the run, unlike Spikes C and C2, so this is a first look and not a gate result. Nothing was stored. The key was read from `.env`, sent only to finnhub.io in a header and not printed.

Endpoint: `/api/v1/calendar/earnings?from=&to=` on the free key. "Ours" means a ticker in `capture_universe.csv`.

| Window | Status | Rows | Ours | Ours with estimate | Ours with actual |
|---|---|---|---|---|---|
| 2026-11-27 to 2026-12-27 | 200 | 377 | 7 | 7 | 0 |
| 2026-12-01 to 2026-12-15 | 200 | 272 | 5 | 5 | 0 |
| 2027-01-11 to 2027-01-31 (rows returned up to 01-29) | 200 | 718 | 32 | 32 | 0 |
| 2026-11-01 to 2026-11-26 (rows returned from 11-10) | 200 | 1500 | 6 | 6 | 5 |

Fields: `date`, `epsActual`, `epsEstimate`, `hour`, `quarter`, `revenueActual`, `revenueEstimate`, `symbol`, `year`.

## Reading

- Spike C2 found Finnhub not usable after testing `/stock/eps-estimate` (403) and `/stock/earnings`. It did not test this endpoint. Statements that the free plan is not usable were broader than that test.
- The free calendar returns an upcoming estimate and, after the announcement, an actual from the same source, which is the shape LB-07 asks for.
- No analyst count, spread or EPS basis. Not tested: whether estimates change after the announcement, or the basis of the actual (AE-03, VL-07). A window of 1,500 rows was cut, so short windows are needed.
- Terms (read 23 November 2026, source register): personal use only; no sharing of data or derived results without written approval. Not adopted. Nothing is collected until John decides (D-50).
