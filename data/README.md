# Data policy

Only `synthetic_demo.csv` is included. It is ARTIFICIAL and is exclusively for smoke testing.
Do not use synthetic results as evidence that the forecasting model is useful.

To use real results, manually obtain data that you have rights to use, retain a record of
license/permission and provenance, and place it at a local path outside version control.
Accepted columns: Date, HomeTeam, AwayTeam, FTHG, FTAG. ISO or UK day/month dates.
The starter does not support reliable multi-league inference, xG, or lineup features yet.

## OpenFootball CC0 snapshots (v0.2)

`analysnow fetch-openfootball --as-of 2025-07-01` obtains four completed English Premier League seasons from [openfootball/football.json](https://github.com/openfootball/football.json) (source repository declares CC0-1.0) and stores an exact snapshot under `data/openfootball/`. No provider key is required; raw downloads only occur when you explicitly run the command. External files are ignored by Git by default.

The manifest stores original URLs, SHA-256 hashes, UTC retrieval time, normalized CSV hash, complete-season count checks, and license/source attribution. OpenFootball data has **not** been independently cross-checked for accuracy and is not an xG or player-injury source. See `docs/M1_REAL_DATA_GUIDE.md`.
