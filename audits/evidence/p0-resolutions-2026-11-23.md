# Resolutions of earlier-wave issues, 23 November 2026

Written before Wave 1.1 began, at John's request ("resolve issues with the previous waves").

## Wave 0.1 to 0.3 items closed here

| Item | Result | Evidence |
|---|---|---|
| K / C-23: five required checks or six? | Settled by reading the repository settings with `gh api repos/johnsajeeve/Earnings-Surprise-Predictor/branches/main/protection`: exactly five were required (pins, lint and types, tests, secret scan, vulnerabilities). The sixth CI job, "Requirements consistency (DO-03, DO-05)", was not required, so a failure there would not have blocked a merge (DR-13). John approved requiring it (C-45). Applied with `gh api -X PATCH .../required_status_checks`; the six contexts were read back. | command output in the session; decision C-45 |
| EQ-04 clean build | A fresh clone of commit `1f9fcf1` was built in a separate Compose project (`cleancheck`) with its own volume and ports: `docker compose up --build -d --wait` took 1 min 44 s, `migrate` exited 0 from an empty database, health returned `ok` for postgres, redis and worker, the CI-style tests gave 51 passed, 586 skipped, 2 expected failures, 0 failed, and the worker's start-up catch-up stored 10 snapshots in the clean database. The project was then removed with `down -v`; its volume is gone. The real project database was untouched (10 snapshots before and after). | this file; EQ-04 changes from PARTIAL to PASS for the clean-build half |
| DR-05 (D-38 values) | Closed earlier by C-44. | decision log |

## Items still open (need John or a later day)

- D-35 (the `ProsusAI/finbert` licence is CC BY-NC-SA 4.0).
- DR-10 (no fallback for the announcement time), DR-06 (CIK succession rule), D-46 (supervisor agreement).
- DR-08 (CI test job skips 20 checks): John did not approve a new CI job.
- The second observation of the SEC bulk-file refresh, the second day of consensus capture, the Finnhub spike (needs a key).
- Not run on GitHub Actions: the `build/wave-0-1` branch has not been pushed. Earlier CI runs on `build/docker-skeleton` passed.
