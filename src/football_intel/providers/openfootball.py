"""OpenFootball CC0 public-domain historical Premier League result importer.

Original data: https://github.com/openfootball/football.json (CC0-1.0).
The fetcher downloads a small, explicitly selected set of seasons using HTTPS.
It stores original source JSON and a SHA256 provenance manifest for reproducibility.
Data quality is *not* guaranteed by a public-domain license.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from ..data import Match, load_matches, parse_date

REPO_URL = "https://github.com/openfootball/football.json"
LICENSE_URL = f"{REPO_URL}/blob/master/LICENSE.md"
RAW_ORIGIN = "https://raw.githubusercontent.com/openfootball/football.json/master"
DEFAULT_SEASONS = ("2021-22", "2022-23", "2023-24", "2024-25")
MAX_FILE_SIZE = 3_000_000  # per-season limit, guards against unexpected payloads
SEASON_RE = re.compile(r"^(20\d\d)-(\d\d)$")


@dataclass(frozen=True)
class ParsedSeason:
    matches: list[Match]
    pending: int
    future_or_today: int
    source_name: str


def check_season(value: str) -> str:
    match = SEASON_RE.fullmatch(value)
    if not match or int(match.group(2)) != (int(match.group(1)) + 1) % 100:
        raise ValueError(f"Invalid season {value!r}; use YYYY-YY, for example 2023-24")
    return value


def season_url(season: str) -> str:
    check_season(season)
    return f"{RAW_ORIGIN}/{season}/en.1.json"


def fetch_bytes(url: str) -> bytes:
    """Only allow-listed official raw paths; the source branch is not commit-pinned."""
    if not re.fullmatch(re.escape(RAW_ORIGIN) + r"/20\d{2}-\d{2}/en\.1\.json", url):
        raise ValueError("Only pinned OpenFootball Premier League source paths are permitted")
    request = Request(url, headers={"User-Agent": "AnalyzNowAI-research/0.2"})
    with urlopen(request, timeout=25) as response:
        payload = response.read(MAX_FILE_SIZE + 1)
    if len(payload) > MAX_FILE_SIZE:
        raise ValueError("Provider response exceeds expected JSON size")
    return payload


def parse_season(raw: bytes, *, season: str, as_of: date) -> ParsedSeason:
    """Accept score as {'ft':[h,a]} or [h,a]; never infer an absent score.

    On the cut-off date, ignore matches even if upstream shows scores: without
    time-aware metadata we cannot safely treat same-day data as prior outcomes.
    """
    check_season(season)
    if len(raw) > MAX_FILE_SIZE:
        raise ValueError("Season JSON is unexpectedly large")
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError(f"{season}: could not decode provider JSON") from exc
    if not isinstance(data, dict) or not isinstance(data.get("matches"), list):
        raise ValueError(f"{season}: missing matches list")
    name = data.get("name")
    first_year = int(season[:4])
    expected_label = f"{first_year}/{str(first_year + 1)[-2:]}"
    if (not isinstance(name, str) or "premier league" not in name.casefold() or
            expected_label not in name):
        raise ValueError(f"{season}: source is not labelled Premier League {expected_label}")
    matches: list[Match] = []
    pending = future_or_today = 0
    seen: set[tuple[date, str, str]] = set()
    for index, row in enumerate(data["matches"], start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{season} match #{index}: expected a JSON object")
        try:
            day = parse_date(str(row["date"]))
            home, away = row["team1"], row["team2"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{season} match #{index}: invalid date/teams") from exc
        if (not isinstance(home, str) or not isinstance(away, str) or
                not home.strip() or not away.strip() or home.casefold() == away.casefold()):
            raise ValueError(f"{season} match #{index}: invalid team names")
        if not (date(first_year, 7, 1) <= day < date(first_year + 1, 8, 1)):
            raise ValueError(f"{season} match #{index}: date outside season window")
        if day >= as_of:
            future_or_today += 1
            continue
        score = row.get("score")
        if isinstance(score, dict):
            score = score.get("ft")
        if score is None or score == []:
            pending += 1
            continue
        if (not isinstance(score, list) or len(score) != 2 or
                any(type(goal) is not int or goal < 0 for goal in score)):
            raise ValueError(f"{season} match #{index}: invalid final score {score!r}")
        signature = (day, home.strip().casefold(), away.strip().casefold())
        if signature in seen:
            raise ValueError(f"{season} match #{index}: duplicated completed fixture")
        seen.add(signature)
        matches.append(Match(day, home.strip(), away.strip(), score[0], score[1]))
    if not matches:
        raise ValueError(f"{season}: no completed matches before cutoff {as_of}")
    return ParsedSeason(sorted(matches, key=lambda x: (x.date, x.home_team)), pending, future_or_today, name)


def _csv_bytes(matches: list[Match]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"))
    for match in matches:
        writer.writerow((match.date.isoformat(), match.home_team, match.away_team, match.home_goals, match.away_goals))
    return output.getvalue().encode("utf-8")


def import_seasons(raw_seasons: dict[str, bytes], *, destination: Path, as_of: date) -> dict:
    """Validate all seasons before writing; keep byte-for-byte raw source files.

    `raw_seasons` is injected in unit tests so network access is never needed for CI.
    Data files are written only into a fresh destination (no silent overwrites).
    """
    if not raw_seasons or len(raw_seasons) > 10:
        raise ValueError("Select 1–10 Premier League seasons")
    if destination.exists():
        raise FileExistsError(f"Destination {destination} exists. Choose a new directory to preserve previous snapshots")
    parsed = [(season, raw, parse_season(raw, season=season, as_of=as_of))
              for season, raw in sorted(raw_seasons.items())]
    all_matches = sorted((m for _, _, item in parsed for m in item.matches),
                         key=lambda match: (match.date, match.home_team, match.away_team))
    if len({(m.date, m.home_team.casefold(), m.away_team.casefold()) for m in all_matches}) != len(all_matches):
        raise ValueError("Duplicate completed fixture across seasons")
    teams = sorted({m.home_team for m in all_matches} | {m.away_team for m in all_matches})
    if len(teams) < 2:
        raise ValueError("Not enough teams in imported data")
    csv_content = _csv_bytes(all_matches)
    # Naming uses the sorted seasons for deterministic metadata, regardless of CLI argument order.
    slug = "epl_" + "_".join(sorted(raw_seasons))
    csv_path = destination / "processed" / f"{slug}.csv"
    manifest_path = destination / "manifest.json"
    manifest = {
        "product": "AnalyzNow AI",
        "provider": "openfootball/football.json",
        "provider_repository": REPO_URL,
        "provider_license": "CC0-1.0 (repository declaration; review if source changes)",
        "license_url": LICENSE_URL,
        "competition": "English Premier League",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "training_data_cutoff_exclusive": as_of.isoformat(),
        "csv_path": csv_path.relative_to(destination).as_posix(),
        "csv_sha256": hashlib.sha256(csv_content).hexdigest(),
        "total_completed_matches": len(all_matches),
        "unique_teams_across_seasons": len(teams),
        "seasons": [
            {"season": s, "official_dataset_name": item.source_name, "url": season_url(s),
             "complete_season_check": (
                 "PASS_380_RESULTS" if as_of >= date(int(s[:4]) + 1, 7, 1) and len(item.matches) == 380
                 else "WARNING_EXPECTED_380" if as_of >= date(int(s[:4]) + 1, 7, 1)
                 else "IN_PROGRESS_AT_CUTOFF"
             ),
             "raw_file": f"raw/{s}.json", "raw_sha256": hashlib.sha256(raw).hexdigest(),
             "completed_matches": len(item.matches), "unplayed_missing_scores": item.pending,
             "excluded_on_or_after_cutoff": item.future_or_today}
            for s, raw, item in parsed
        ],
        "quality_warning": "Results are provider-reported, not independently cross-verified. Source points to mutable master branch; saved SHA256 and raw snapshots preserve the exact fetched bytes.",
    }
    try:
        (destination / "raw").mkdir(parents=True)
        csv_path.parent.mkdir(parents=True)
        for s, raw, _ in parsed:
            (destination / "raw" / f"{s}.json").write_bytes(raw)
        csv_path.write_bytes(csv_content)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if len(load_matches(csv_path)) != len(all_matches):
            raise ValueError("Round-trip CSV validation failed")
    except Exception:
        # Remove our own new snapshot on failure; never touch a pre-existing directory.
        import shutil
        shutil.rmtree(destination)
        raise
    return {**manifest, "manifest_path": str(manifest_path), "full_csv_path": str(csv_path)}


def download_seasons(seasons: list[str], *, destination: Path, as_of: date) -> dict:
    """Download source snapshots and import them; no third-party credentials needed."""
    if not seasons or len(seasons) > 10 or len(set(seasons)) != len(seasons):
        raise ValueError("Provide 1–10 unique seasons")
    for season in seasons:
        check_season(season)
    if destination.exists():
        raise FileExistsError(f"Destination {destination} exists; use a new snapshot name")
    raw = {season: fetch_bytes(season_url(season)) for season in seasons}
    return import_seasons(raw, destination=destination, as_of=as_of)


def verify_snapshot(directory: Path) -> dict:
    """Check downloaded source snapshots and normalized CSV match the saved manifest."""
    root = Path(directory)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("provider") != "openfootball/football.json":
        raise ValueError("Unrecognized provenance manifest")
    files = [(manifest["csv_path"], manifest["csv_sha256"])]
    files += [(source["raw_file"], source["raw_sha256"]) for source in manifest["seasons"]]
    for path, expected_sha in files:
        file = (root / path).resolve()
        if not file.is_relative_to(root.resolve()):
            raise ValueError("Unsafe file path in provenance manifest")
        actual_sha = hashlib.sha256(file.read_bytes()).hexdigest()
        if expected_sha != actual_sha:
            raise ValueError(f"SHA256 mismatch for {path}")
    matches = load_matches(root / manifest["csv_path"])
    if len(matches) != manifest["total_completed_matches"]:
        raise ValueError("Completed match count does not match provenance manifest")
    return {"verified": True, "provider": manifest["provider"],
            "completed_matches": len(matches), "seasons": len(manifest["seasons"]),
            "csv_path": str(root / manifest["csv_path"])}
