"""`analysnow` / `python -m football_intel` commands."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from .data import load_matches, teams_in, parse_date
from .model import train, forecast
from .backtest import backtest
from .providers.openfootball import DEFAULT_SEASONS, download_seasons, verify_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="AnalysNow AI local research starter")
    subs = parser.add_subparsers(dest="command", required=True)
    validate = subs.add_parser("validate", help="Validate a match results CSV")
    validate.add_argument("csv", type=Path)
    predict = subs.add_parser("predict", help="Produce a statistical match forecast")
    predict.add_argument("csv", type=Path)
    predict.add_argument("home_team")
    predict.add_argument("away_team")
    predict.add_argument("--as-of", default=date.today().isoformat(), help="Cutoff ISO date; excludes that date and later")
    check = subs.add_parser("backtest", help="Run walk-forward historical evaluation")
    check.add_argument("csv", type=Path)
    check.add_argument("--min-training", type=int, default=80)
    check.add_argument("--output", type=Path, default=None, help="Save full journal to JSON")
    check.add_argument("--test-from", type=str, default=None, help="Only evaluate on/after YYYY-MM-DD (still train on prior dates)")
    fetch = subs.add_parser("fetch-openfootball", help="Download CC0 Premier League result snapshots with provenance")
    fetch.add_argument("--seasons", nargs="+", default=list(DEFAULT_SEASONS), help="Seasons like 2021-22 2022-23")
    fetch.add_argument("--dest", type=Path, default=Path("data/openfootball/epl_2021_2025"), help="NEW destination directory; will never overwrite")
    fetch.add_argument("--as-of", default=date.today().isoformat(), help="Exclude results on/after this date (YYYY-MM-DD)")
    verify = subs.add_parser("verify-snapshot", help="Verify content SHA256 hashes and CSV match count")
    verify.add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.command == "fetch-openfootball":
        result = download_seasons(args.seasons, destination=args.dest, as_of=parse_date(args.as_of))
        print(json.dumps({k: v for k, v in result.items() if k != "seasons"}, indent=2))
        print("Per-season source hashes and row counts are in", result["manifest_path"])
        return
    if args.command == "verify-snapshot":
        print(json.dumps(verify_snapshot(args.directory), indent=2))
        return
    matches = load_matches(args.csv)
    if args.command == "validate":
        print(json.dumps({"valid": True, "matches": len(matches), "teams": teams_in(matches),
                          "first_match": matches[0].date.isoformat() if matches else None,
                          "last_match": matches[-1].date.isoformat() if matches else None}, indent=2))
    elif args.command == "predict":
        cut = parse_date(args.as_of)
        model = train(matches, as_of=cut)
        print(json.dumps(forecast(model, args.home_team, args.away_team), indent=2))
    else:
        result = backtest(matches, min_training_matches=args.min_training, test_from=parse_date(args.test_from) if args.test_from else None)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"Full forecast journal saved to {args.output}")
        print(json.dumps({k: v for k, v in result.items() if k != "individual_forecasts"}, indent=2))


if __name__ == "__main__":
    main()
