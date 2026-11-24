
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type DataHealth = {
  dataset_label: string;
  historical_matches: number;
  latest_match: string;
  days_old: number;
  stale_after_days: number;
  is_stale: boolean;
};

export default function DataHealthPage() {
  const [data, setData] = useState<DataHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadHealth() {
      try {
        const response = await fetch("/api/data-health", {
          cache: "no-store",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Unable to load data health");
        }

        const result: DataHealth = await response.json();

        if (!controller.signal.aborted) {
          setData(result);
        }
      } catch {
        if (!controller.signal.aborted) {
          setError("Cannot connect to the Data Health API.");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadHealth();
    return () => controller.abort();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-white">
      <div className="mx-auto max-w-4xl">

        <Link href="/" className="text-emerald-400">
          Back to Match Analysis
        </Link>

        <h1 className="mt-8 text-3xl font-bold">
          Data Health
        </h1>

        <p className="mt-3 text-slate-400">
          Historical football data freshness and coverage.
        </p>

        {loading && (
          <p className="mt-8">Checking data health...</p>
        )}

        {error && (
          <p role="alert" className="mt-8 text-red-400">
            {error}
          </p>
        )}

        {data && (
          <div className="mt-8 space-y-6">

            <div className="grid gap-4 sm:grid-cols-2">

              <div className="rounded-xl bg-slate-900 p-6">
                <p className="text-slate-400">
                  Historical Matches
                </p>
                <p className="mt-3 text-3xl font-bold">
                  {data.historical_matches}
                </p>
              </div>

              <div className="rounded-xl bg-slate-900 p-6">
                <p className="text-slate-400">
                  Data Age
                </p>
                <p className="mt-3 text-3xl font-bold">
                  {data.days_old} days
                </p>
              </div>

            </div>

            <div className="rounded-xl bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">
                Data Freshness
              </h2>

              <p
                role="status"
                className={`mt-4 font-semibold ${
                  data.is_stale
                    ? "text-amber-400"
                    : "text-emerald-400"
                }`}
              >
                {data.is_stale
                  ? "Historical data is outdated"
                  : "Data is within the freshness threshold"}
              </p>

              <p className="mt-4 text-slate-300">
                Latest match: {data.latest_match}
              </p>

              <p className="mt-2 text-slate-300">
                Dataset: {data.dataset_label}
              </p>

              <p className="mt-2 text-slate-400">
                Freshness threshold: {data.stale_after_days} days
              </p>
            </div>

            <p className="text-sm text-slate-400">
              A freshness check measures how old the
              historical data is. It does not establish
              predictive accuracy or current team form.
            </p>

          </div>
        )}
      </div>
    </main>
  );
}