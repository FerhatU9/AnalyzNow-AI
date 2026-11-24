# Historical Model Reproducibility

This procedure reproduces the 2024/25 exploratory and 2025/26 later-season evaluations behind the AnalyzNow AI **Model Quality** page. It is separate from the synthetic browser demonstration in [DEMO.md](DEMO.md).

**Status (2026-11-24):** The developer independently downloaded and SHA-256-verified a new five-season OpenFootball snapshot (1,900 matches), and reran the 2025/26 Poisson backtest and frozen Elo/ensemble comparison on it. All 2025/26 aggregate measures and uncertainty intervals matched previous results. The 2024/25 exploratory comparison was rerun using a separate four-season local snapshot and matched previously reported model scores. On 2026-11-24, `verify-snapshot` independently confirmed `verified: true`, four seasons and 1,520 completed matches. Both research seasons' local snapshot-integrity checks and model comparisons are now reproduced. This does not verify every upstream match result or production predictive skill. Passing the normal GitHub Actions workflow does not execute these external-data research steps.

## Requirements and data boundaries

- A checkout of the reviewed research branch, Python 3.11+ and an HTTPS connection to OpenFootball.
- From the repository root, install dependencies: `py -3 -m venv .venv` followed by `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`.
- Historical match results come from [OpenFootball football.json](https://github.com/openfootball/football.json), which declares the dataset under [CC0-1.0](https://github.com/openfootball/football.json/blob/master/LICENSE.md). The imported sources are third-party records and should be checked for correctness. The downloader uses the source repository's **mutable master branch**; saved hashes document the bytes obtained but do not ensure a later download is identical.
- The commands download locally to Git-ignored `data/openfootball/` paths and save individual forecasts in Git-ignored `outputs/`. **Do not commit these files or any provider key.**
- These steps require no PostgreSQL service, betting odds API, or frontend server.

The commands below are for a **fresh clone** where the two snapshot directories do not already exist. The downloader deliberately refuses to overwrite an existing snapshot. For an existing workspace, **do not delete or overwrite prior snapshots**: use them after checking their manifest hashes, or use fresh destination names and supply matching explicit `--matches` paths to the evaluation scripts.

## 1. Download and verify the four-season historical snapshot

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m football_intel fetch-openfootball --seasons 2021-22 2022-23 2023-24 2024-25 --dest data/openfootball/epl_2021_2025 --as-of 2025-07-01
.\.venv\Scripts\python.exe -m football_intel verify-snapshot data/openfootball/epl_2021_2025
```

Inspect `data/openfootball/epl_2021_2025/manifest.json` for source URLs, retrieval time, SHA-256 hashes and match totals. A complete 2021/22–2024/25 dataset contains **1,520 finished league matches**.

## 2. Generate the exploratory 2024/25 results

```powershell
.\.venv\Scripts\python.exe -m football_intel backtest "data\openfootball\epl_2021_2025\processed\epl_2021-22_2022-23_2023-24_2024-25.csv" --min-training 760 --test-from 2024-08-01 --output outputs\epl_2024_25_evaluation.json
.\.venv\Scripts\python.exe -m scripts.evaluate_ensemble
```

These are **380** evaluated Premier League fixtures if the snapshot is complete. The Poisson forecasts are walk-forward by match date. The ensemble is a fixed 50% Elo / 50% Poisson blend; the 2024/25 model comparison is **exploratory**, not an untouched confirmation.

**Local rerun evidence (2026-11-24):** The developer ran the Poisson backtest on `data/openfootball/epl_release_check_2025/processed/epl_2021-22_2022-23_2023-24_2024-25.csv` with `--min-training 760 --test-from 2024-08-01`, saving to `outputs/epl_release_check_2025_evaluation.json`. Running `scripts.evaluate_ensemble` against the same source and journal, saved separately to `outputs/ensemble_release_check_2025.json`, reproduced the previously reported 380 matches over 109 dates. Brier scores: Poisson **0.594368**, Elo **0.590903**, 50/50 ensemble **0.587464**; log losses **0.996779**, **0.990428**, **0.986054**; accuracy **52.1%**, **53.4%**, **52.6%**, respectively. The 95% interval for ensemble-minus-Poisson Brier difference was **[-0.015628, +0.001663]**, which includes zero. A subsequent `verify-snapshot data/openfootball/epl_release_check_2025` run returned `verified: true`, `seasons: 4` and `completed_matches: 1520`. This verifies the local snapshot against its recorded hashes, not the accuracy of every upstream score.

Optional detail diagnostics: `.\.venv\Scripts\python.exe scripts\compare_elo.py` and `.\.venv\Scripts\python.exe scripts\evaluate_elo_uncertainty.py`.

## 3. Download and verify the five-season snapshot

```powershell
.\.venv\Scripts\python.exe -m football_intel fetch-openfootball --seasons 2021-22 2022-23 2023-24 2024-25 2025-26 --dest data/openfootball/epl_2021_2026 --as-of 2026-07-01
.\.venv\Scripts\python.exe -m football_intel verify-snapshot data/openfootball/epl_2021_2026
```

A complete five-season dataset contains **1,900** finished matches. It is a separate snapshot, not a PostgreSQL migration.

**Verified independent local rerun (2026-11-24):** The developer downloaded a fresh copy to the non-overwriting `data/openfootball/epl_release_check_2026` folder. The importer reported `verified: true`, 1,900 completed matches, five seasons, 27 distinct club names, and processed CSV SHA-256 `dab0e9c6638bcf1808dbcb7ceed9787dac0fb4f16152d7d79c3ccf2e6d425776`. The downloaded snapshot is ignored by Git and is not included in repository commits.

## 4. Reproduce the 2025/26 later-season evaluation and drift report

```powershell
.\.venv\Scripts\python.exe -m football_intel backtest "data\openfootball\epl_2021_2026\processed\epl_2021-22_2022-23_2023-24_2024-25_2025-26.csv" --min-training 760 --test-from 2025-08-01 --output outputs\epl_2025_26_evaluation.json
.\.venv\Scripts\python.exe -m scripts.evaluate_heldout
.\.venv\Scripts\python.exe scripts\evaluate_model_drift.py
```

The later-season model evaluation should contain **380 fixtures** with frozen Elo settings `K=32`, `home_advantage=40` and an equal-weight ensemble. A better score in one season does not prove future superiority. The drift report is descriptive, not evidence of a causal change.

**Verified new-snapshot rerun (2026-11-24):** The developer reran the Poisson backtest with `--matches` input `data/openfootball/epl_release_check_2026/processed/epl_2021-22_2022-23_2023-24_2024-25_2025-26.csv`, `--min-training 760` and `--test-from 2025-08-01`, writing a new journal to `outputs/epl_release_check_evaluation.json`. The model reported 380 fixtures, Poisson Brier 0.618784 and log loss 1.031207. Passing that journal and the fresh match CSV to `scripts.evaluate_heldout` reproduced Elo Brier 0.627743, ensemble Brier 0.618067, and the published 95% paired intervals (ensemble minus Poisson Brier [-0.009735, +0.008487]). This confirms reproducibility for the later season; the four-season exploratory evaluation and snapshot integrity were also subsequently reproduced (see section 2).

## 5. Rebuild and compare the aggregate dashboard report

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_model_quality_export.py
.\.venv\Scripts\python.exe scripts\export_model_quality.py --output outputs\recomputed_model_quality.json
.\.venv\Scripts\python.exe -c "import json, pathlib, sys; original=json.loads(pathlib.Path('frontend/data/model-quality.json').read_text(encoding='utf-8')); rebuilt=json.loads(pathlib.Path('outputs/recomputed_model_quality.json').read_text(encoding='utf-8')); ok=(original==rebuilt); print('Model Quality aggregate comparison:', 'MATCH' if ok else 'DIFFERENT'); sys.exit(0 if ok else 1)"
```

A **MATCH** means the aggregate JSON agrees exactly with the committed `frontend/data/model-quality.json`; it does not establish that the underlying records are independently fact-checked. A **DIFFERENT** result is a release-review finding: retain both reports and snapshot manifests, investigate any changed upstream source bytes, changed code or differing evaluation configuration, and do not overwrite the committed dashboard report automatically.

Expected published 2025/26 Brier scores (rounded to six decimals): Poisson **0.618784**, Elo **0.627743**, ensemble **0.618067**. The ensemble improvement over Poisson is small and its uncertainty interval includes zero.

After reproduction, keep the data and reports local. Check `git status --short` to ensure no unplanned files are staged. Record only verified source hashes and aggregate results in reviewed documentation.

## Publication boundary

These procedures evaluate **historical** outcomes. They do not verify current-season predictions, commercial betting performance, independently supplied match truth, or the right to redistribute third-party bookmaker feeds. Do not combine live odds with historical-only team models as if they are time-aligned.
