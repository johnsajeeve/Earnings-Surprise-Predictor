# As-of reads (Database DB-09)

Written 23 November 2026. This explains a rule; it defines no requirement.

A prediction for an event announced at time D may use only what was known strictly before D. Facts that can be corrected or replaced are stored as new rows with a later knowledge time (Database DB-08), so a read for date D has to pick the latest version known before D, never a later one.

## The pattern

- Each versioned fact table has one function named `<table>_as_of(entity, as_of_time)` that returns, for the entity, the latest version whose knowledge time is strictly before `as_of_time`.
- Feature code reads a versioned table only through that function. A test scans the feature code for a direct `FROM` or `JOIN` of such a table (`earnings.schema.AS_OF_FUNCTIONS` lists them).
- "Strictly before" is deliberate: a row stamped exactly at D is not known before D.

## Instances

| Table | Knowledge time | Function |
|---|---|---|
| `estimate_snapshot` | `captured_at` | `estimate_snapshot_as_of(company_id, as_of)`: latest per source and period |
| `actual_eps`, `eps_history`, `fundamentals_filing` | their release or filing time | added with the migration that creates each table (Waves 1.4 and later) |

Validity periods (ticker history, index membership) are not versions. They are half-open date ranges with a database constraint against overlap, read with `company_for_ticker(ticker, date)` (Database DB-10).
