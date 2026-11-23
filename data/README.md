# AnalyzNow AI — Data Sources and Provenance

## Included data

`synthetic_demo.csv` contains **artificial match results** used only to check application functionality. It is not evidence of forecast accuracy.

## Historical Premier League results

The data import workflow downloads completed English Premier League results from [OpenFootball](https://github.com/openfootball/football.json). The upstream repository declares CC0 for its football data. Each download records source URLs, retrieval times, SHA-256 hashes and a normalized dataset hash.

The project's local four-season dataset covers 2021/22 to 2024/25 (1,520 match results when complete). Downloaded results and generated outputs are excluded from Git tracking by default.

For instructions, see [Data Pipeline](../docs/DATA_PIPELINE.md).

## Accepted structured-data columns

| Column | Description |
| --- | --- |
| `Date` | Match date |
| `HomeTeam` | Home club name |
| `AwayTeam` | Away club name |
| `FTHG` | Full-time goals by the home team |
| `FTAG` | Full-time goals by the away team |

Do not mix leagues without an explicitly validated competition-strength model. The dataset does not contain event-level xG, team injuries, lineups or bookmaker prices.

## Data policy

- Verify permission before ingesting external datasets; public access alone does not grant commercial redistribution rights.
- Preserve the original sources, timestamps and checksums for reproducibility.
- Do not commit API keys, copyrighted provider files, local database exports or personally identifying data.
- An integrity hash verifies file consistency, **not** the correctness of every original match result.
