"use client";

import { useState } from "react";

type Outcome = "home_win" | "draw" | "away_win";

type MarketFixture = {
  event_id: string;
  home_team: string;
  away_team: string;
  kickoff: string;
  bookmakers_compared: number;
  latest_odds_update: string | null;
  market_probabilities: Record<Outcome, number>;
};

type MarketResponse = {
  competition: string;
  market: string;
  fixture_count: number;
  fixtures: MarketFixture[];
  notice?: string;
};

const outcomes: { key: Outcome; label: string }[] = [
  { key: "home_win", label: "Home win" },
  { key: "draw", label: "Draw" },
  { key: "away_win", label: "Away win" },
];

function percent(value: number): string {
  if (!Number.isFinite(value) || value < 0 || value > 1) {
    return "Unavailable";
  }

  return (value * 100).toFixed(1) + "%";
}

function dateUtc(value: string | null): string {
  if (!value) return "Not supplied";

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Unavailable";

  return (
    new Intl.DateTimeFormat("en-GB", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "UTC",
    }).format(parsed) + " UTC"
  );
}

function isMarketResponse(value: unknown): value is MarketResponse {
  if (typeof value !== "object" || value === null) return false;

  const data = value as Record<string, unknown>;

  return typeof data.fixture_count === "number" && Array.isArray(data.fixtures);
}

export default function MarketOdds() {
  const [market, setMarket] = useState<MarketResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [retrievedAt, setRetrievedAt] = useState<string | null>(null);

  async function loadMarketOdds() {
    if (loading) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/market-odds", { cache: "no-store" });
      const payload: unknown = await response.json();

      if (!response.ok) {
        const message =
          typeof payload === "object" &&
          payload !== null &&
          "error" in payload &&
          typeof payload.error === "string"
            ? payload.error
            : "Market information is currently unavailable";

        throw new Error(message);
      }

      if (!isMarketResponse(payload)) {
        throw new Error("The market service returned an invalid response.");
      }

      setMarket(payload);
      setRetrievedAt(new Date().toISOString());
    } catch (caught) {
      setError(
        caught instanceof Error ? caught.message : "Unexpected market data error",
      );
      setMarket(null);
      setRetrievedAt(null);
    } finally {
      setLoading(false);
    }
  }

  const visibleFixtures = [...(market?.fixtures ?? [])]
    .filter(
      (fixture) =>
        typeof fixture.event_id === "string" &&
        typeof fixture.home_team === "string" &&
        typeof fixture.away_team === "string" &&
        typeof fixture.kickoff === "string" &&
        typeof fixture.bookmakers_compared === "number" &&
        fixture.market_probabilities != null,
    )
    .sort((a, b) => a.kickoff.localeCompare(b.kickoff))
    .slice(0, 10);

  return (
    <section
      aria-labelledby="market-odds-heading"
      className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6"
    >
      <div className="flex flex-wrap items-start justify-between gap-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-emerald-400">
            Bookmaker market
          </p>
          <h2 id="market-odds-heading" className="mt-2 text-2xl font-bold">
            Live Market Intelligence
          </h2>
          <p className="mt-3 max-w-2xl text-sm text-slate-400">
            Upcoming Premier League fixtures and bookmaker-implied 1X2
            probabilities, adjusted to remove the basic bookmaker margin.
            These are not our statistical model forecasts.
          </p>
        </div>

        <button
          type="button"
          onClick={loadMarketOdds}
          disabled={loading}
          className="rounded-lg bg-emerald-500 px-5 py-3 font-semibold text-slate-950 hover:bg-emerald-400 disabled:cursor-wait disabled:opacity-60"
        >
          {loading ? "Fetching odds..." : market ? "Refresh odds" : "Load market odds"}
        </button>
      </div>

      <p className="mt-4 text-xs text-slate-400">
        Odds load only when you request them. Each request may use provider API
        credits. No bookmaker prices are stored in the browser.
      </p>

      {error && (
        <p role="alert" className="mt-5 rounded-lg bg-red-950 p-4 text-sm text-red-200">
          {error}
        </p>
      )}

      {market && (
        <div className="mt-6 space-y-5">
          <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm text-slate-400">
            <span>{market.fixture_count} available fixtures</span>
            <span>Retrieved {dateUtc(retrievedAt)}</span>
          </div>

          {visibleFixtures.length === 0 ? (
            <p className="rounded-lg border border-slate-700 p-4 text-slate-300">
              No upcoming fixtures with complete bookmaker odds are currently available.
            </p>
          ) : (
            <>
              {visibleFixtures.map((fixture) => (
                <article
                  key={fixture.event_id}
                  className="rounded-xl border border-slate-700 bg-slate-950 p-5"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <h3 className="text-lg font-semibold">
                      {fixture.home_team} vs {fixture.away_team}
                    </h3>
                    <span className="text-sm text-slate-400">
                      {dateUtc(fixture.kickoff)}
                    </span>
                  </div>

                  <p className="mt-2 text-xs text-slate-400">
                    {fixture.bookmakers_compared} bookmakers compared
                    {" · "}
                    Odds updated: {dateUtc(fixture.latest_odds_update)}
                  </p>

                  <div className="mt-5 space-y-4">
                    {outcomes.map((outcome) => {
                      const probability =
                        fixture.market_probabilities[outcome.key];

                      const valid =
                        Number.isFinite(probability) &&
                        probability >= 0 &&
                        probability <= 1;

                      return (
                        <div key={outcome.key}>
                          <div className="mb-2 flex justify-between gap-3 text-sm">
                            <span>{outcome.label}</span>
                            <span className="font-semibold">
                              {percent(probability)}
                            </span>
                          </div>
                          <div
                            aria-hidden="true"
                            className="h-2 overflow-hidden rounded-full bg-slate-800"
                          >
                            <div
                              className="h-full rounded-full bg-emerald-400"
                              style={{
                                width: valid
                                  ? String(probability * 100) + "%"
                                  : "0%",
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </article>
              ))}

              {market.fixture_count > visibleFixtures.length && (
                <p className="text-sm text-slate-400">
                  Showing the next {visibleFixtures.length} fixtures.
                </p>
              )}
            </>
          )}

          <p className="text-xs leading-relaxed text-slate-400">
            {market.notice ??
              "Prices vary by bookmaker and time. Market probabilities are not betting advice."}
            {" "}The historical forecast dataset currently ends in 2025, so
            these live odds must not be combined with its outdated team estimates.
          </p>
        </div>
      )}
    </section>
  );
}
