# ADR 0004: Label route is the time-series SUE

Status: **Accepted by John on 18 November 2026** (decision C-25, which closes D-01), written 23 November 2026. **Not complete under SC-07:** SC-07 asks for the supervisor's agreement to be recorded with it, and C-25 says no written agreement exists (see D-46). This ADR says so instead of claiming it.

Requirement: Project-Wide SC-07. Related: Data LB-01 to LB-08, CE-05, Section 4A; Project-Wide conflict C19; decisions C-03, C-25.

ADR numbering: 0003 is left for the deployment ADR that Deployment DP-11 names.

## Context

- The proposal defines the label as the surprise against the analyst consensus, standardised by the standard deviation of estimates (SSOT Section 4).
- No free source gives historical point-in-time consensus. John decided on 14 November 2026 that the primary route must be free (C-03). Licensed sources (I/B/E/S, Capital IQ Estimates, Zacks) are optional upgrades that may not be available (Data Section 4, 4A.2; library enquiry D-21 is not yet answered).
- The proposal's Section 5.1 label therefore cannot be built for 2015 to 2024 on the free route. Project-Wide conflict C19 records this.

## Decision

The historical label is the time-series SUE: the change in EPS from the same quarter a year earlier, divided by the standard deviation of the prior seasonal differences, built from first-filed EDGAR diluted EPS (Data LB-01 to LB-05). Analyst consensus is captured forward from the start date, as dated snapshots, and used only as a check on the prospective set (LB-07, LB-08). The two label routes are never mixed in one training set (CE-05). If a licensed consensus source becomes available, the route is decided again by a new ADR.

Class cut-offs are set during EDA on the 2015 to 2021 training window and frozen before the validation and test years are read (LB-06). They are not set here.

## Alternatives not chosen

- **Consensus label from a licensed source.** It is the proposal's definition and would give the strongest result, but no free route exists and access is not confirmed.
- **Forward-only consensus label.** About 500 events in one earnings season (Data 4A.2), too few for a 2015 to 2021 training window.
- **A vendor estimate beside each past actual** (Alpha Vantage, EODHD, yfinance `get_earnings_dates`). Nothing documents when the stored estimate was taken, so it cannot be shown to be pre-announcement. It is allowed only if the 30-event test VL-12 passes.

## Evidence so far (Wave 0.1, 23 November 2026)

- EPS depth: 9 of 10 sampled companies have at least 10 quarters of diluted EPS before 2015. Fourth-quarter EPS has to be derived. First-filed and restated values can be told apart by filing date (Spike B, `audits/evidence/wave-0.1-spikes.md`).
- Forward consensus: yfinance returns a mean, low, high and analyst count for the current quarter, no standard deviation, and an EPS basis that differs by ticker (Spike C).
- The XOM case shows that a company identifier can change: the history sits under a former CIK (Spike B).

## Consequences and open points

- The label is not the proposal's consensus surprise. The dissertation says so (ASM-05, ASM-06), and no claim of agreement with consensus-based studies is made.
- Agreement between the two routes is reported on the prospective set whatever it shows (LB-08).
- The supervisor's written agreement is not on file. John decides whether to ask for it. Until then SC-07 is PARTIAL.
- The success of this route depends on EPS depth for every company in the 100-company subset, not only the 10 sampled. Wave 1.6 measures it and reports the events excluded under LB-02.
- If this decision changes, SC-07, the Data requirements Section 4A and the evaluation page wording (FR-23) change with it.
