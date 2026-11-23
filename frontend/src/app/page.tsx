
"use client";

import { useState, type FormEvent } from "react";
import MarketOdds from "@/components/market-odds";

type Forecast = {
  home_team: string;
  away_team: string;
  as_of: string;
  expected_goals: {
    home: number;
    away: number;
  };
  probabilities: {
    home_win: number;
    draw: number;
    away_win: number;
    over_2_5: number;
    both_teams_score: number;
  };
  top_scorelines: {
    score: string;
    probability: number;
  }[];
  notice?: string;
};

export default function Home() {
  const [homeTeam, setHomeTeam] = useState("Arsenal FC");
  const [awayTeam, setAwayTeam] = useState("Chelsea FC");
  const [date, setDate] = useState("2025-07-01");

  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function generateForecast(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setForecast(null);

    try {
      const response = await fetch("/api/forecast", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          home_team: homeTeam.trim(),
          away_team: awayTeam.trim(),
          as_of: date,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.error ?? result.detail ?? "Forecast failed"
        );
      }

      setForecast(result as Forecast);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unexpected error"
      );
    } finally {
      setLoading(false);
    }
  }

  const formatPercent = (value: number) =>
    `${(value * 100).toFixed(1)}%`;

  const outcomes = forecast
    ? [
        { label: "Home win", value: forecast.probabilities.home_win },
        { label: "Draw", value: forecast.probabilities.draw },
        { label: "Away win", value: forecast.probabilities.away_win },
      ]
    : [];

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-12 text-white">
      <div className="mx-auto max-w-4xl">

        <header className="mb-10">
          <p className="text-sm font-semibold uppercase tracking-widest text-emerald-400">
            Football Intelligence Platform
          </p>
          <h1 className="mt-3 text-4xl font-bold">
            AnalyzNow AI
          </h1>
          <p className="mt-3 text-slate-400">
            Football statistics and evidence-based match forecasting.
          </p>
        </header>

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="mb-6 text-xl font-semibold">
            Match Analysis
          </h2>

          <form onSubmit={generateForecast} className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="space-y-2">
                <span>Home Team</span>
                <input
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 p-3"
                  value={homeTeam}
                  onChange={(e) => setHomeTeam(e.target.value)}
                  required
                />
              </label>

              <label className="space-y-2">
                <span>Away Team</span>
                <input
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 p-3"
                  value={awayTeam}
                  onChange={(e) => setAwayTeam(e.target.value)}
                  required
                />
              </label>
            </div>

            <label className="block space-y-2">
              <span>Forecast Cutoff Date</span>
              <input
                type="date"
                className="block w-full rounded-lg border border-slate-700 bg-slate-800 p-3"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-emerald-500 p-3 font-semibold text-slate-950 hover:bg-emerald-400 disabled:opacity-50"
            >
              {loading ? "Calculating..." : "Generate Forecast"}
            </button>
          </form>

          <p className="mt-4 text-xs text-slate-400">
            Historical dataset: Premier League, 2021–2025.
            Enter club names exactly as stored in the database.
          </p>
        </section>

        {error && (
          <p role="alert" className="mt-6 rounded-lg bg-red-950 p-4 text-red-200">
            {error}
          </p>
        )}

        {forecast && (
          <section className="mt-8 space-y-6">

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">
                Model forecast as of {forecast.as_of}
              </p>
              <h2 className="mt-2 text-2xl font-bold">
                {forecast.home_team} vs {forecast.away_team}
              </h2>

              <h3 className="mt-6 font-semibold">Expected Goals</h3>

              <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="rounded-xl bg-slate-800 p-5">
                  <p className="text-sm text-slate-400">Home</p>
                  <p className="mt-2 text-3xl font-bold">
                    {forecast.expected_goals.home.toFixed(2)}
                  </p>
                </div>
                <div className="rounded-xl bg-slate-800 p-5">
                  <p className="text-sm text-slate-400">Away</p>
                  <p className="mt-2 text-3xl font-bold">
                    {forecast.expected_goals.away.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-6 text-xl font-semibold">
                Match Outcome Probabilities
              </h3>

              {outcomes.map((item) => (
                <div key={item.label} className="mb-5">
                  <div className="mb-2 flex justify-between">
                    <span>{item.label}</span>
                    <span>{formatPercent(item.value)}</span>
                  </div>

                  <div className="h-3 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-emerald-400"
                      style={{
                        width: `${Math.min(100, Math.max(0, item.value * 100))}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl bg-slate-900 p-6">
                <p className="text-slate-400">Over 2.5 Goals</p>
                <p className="mt-2 text-3xl font-bold">
                  {formatPercent(forecast.probabilities.over_2_5)}
                </p>
              </div>

              <div className="rounded-xl bg-slate-900 p-6">
                <p className="text-slate-400">Both Teams to Score</p>
                <p className="mt-2 text-3xl font-bold">
                  {formatPercent(forecast.probabilities.both_teams_score)}
                </p>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-xl font-semibold">
                Most Likely Scorelines
              </h3>
              {forecast.top_scorelines.map((item) => (
                <div
                  key={item.score}
                  className="flex justify-between border-b border-slate-800 py-3"
                >
                  <span>{item.score}</span>
                  <span>{formatPercent(item.probability)}</span>
                </div>
              ))}
            </div>

            <p className="text-sm text-slate-400">
              {forecast.notice ??
                "Historical statistical forecasts are uncertain and are not betting recommendations."}
            </p>

          </section>
        )}
        <MarketOdds />
      </div>
    </main>
  );
}