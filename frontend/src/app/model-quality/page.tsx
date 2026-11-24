import Link from "next/link";
import { readFile } from "node:fs/promises";
import path from "node:path";


export const metadata = {
  title: "Model Quality | AnalyzNow AI",
  description: "Historical forecasting performance and model evaluation methodology.",
};

type Score = {
  brier: number;
  log_loss: number;
  outcome_accuracy: number;
  average_draw_probability: number;
};
type ModelName = "poisson" | "elo" | "ensemble";
type Season = {
  season: string;
  methodology: string;
  matches: number;
  models: Record<ModelName, Score>;
  poisson_halves: Record<"first_half" | "second_half", { matches: number; brier: number }>;
  actual_draw_frequency: number;
};
type Delta = { observed: number; lower: number; upper: number; includes_zero: boolean };
type Report = {
  product: string;
  report_type: string;
  seasons: Season[];
  heldout_ensemble_minus_poisson: Record<"brier_delta" | "log_loss_delta" | "accuracy_delta", Delta>;
  limitations: string;
};

const models: ModelName[] = ["poisson", "elo", "ensemble"];
const display: Record<ModelName, string> = { poisson: "Poisson", elo: "Elo", ensemble: "Ensemble" };
const percent = (value: number) => `${(value * 100).toFixed(1)}%`;
const decimal = (value: number) => value.toFixed(4);

async function readReport(): Promise<Report | null> {
  "use cache";

  try {
    const file = path.join(process.cwd(), "data", "model-quality.json");
    const data = JSON.parse(await readFile(file, "utf8")) as Report;
    if (!Array.isArray(data.seasons) || data.seasons.length !== 2 || !data.heldout_ensemble_minus_poisson) {
      return null;
    }
    return data;
  } catch {
    return null;
  }
}

export default async function ModelQualityPage() {
  const report = await readReport();
  return (
    <main className="min-h-screen bg-slate-950 px-5 py-10 text-white">
      <div className="mx-auto max-w-5xl space-y-8">
        <header>
          <Link href="/" className="text-sm text-emerald-400 underline underline-offset-4 hover:text-emerald-300">
            Back to Match Analysis
          </Link>
          <p className="mt-8 text-xs font-semibold uppercase tracking-widest text-emerald-400">AnalyzNow AI</p>
          <h1 className="mt-2 text-3xl font-bold">Model Quality</h1>
          <p className="mt-3 text-slate-300">Historical forecasting performance, evidence and limitations.</p>
        </header>
        {!report ? (
          <section className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
            <h2 className="text-lg font-semibold">No evaluation summary available</h2>
            <p className="mt-3 text-sm text-slate-300">
              From the repository root, run <code className="rounded bg-slate-800 px-2 py-1">python scripts/export_model_quality.py</code> after generating the local evaluation reports.
            </p>
          </section>
        ) : (
          <>
            <p className="rounded-xl border border-amber-800/60 bg-amber-950/30 p-4 text-sm text-amber-100">
              Historical evaluation only. These are not live match predictions or betting recommendations. The 2024/25 comparison is exploratory.
            </p>
            {report.seasons.map((season) => (
              <section key={season.season} className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <h2 className="text-2xl font-semibold">{season.season} Premier League</h2>
                  <span className="rounded-full bg-slate-800 px-3 py-1 text-sm text-slate-200">{season.matches} matches</span>
                </div>
                <p className="mt-2 text-sm text-slate-400">{season.methodology}</p>
                <div className="mt-6 overflow-x-auto">
                  <table className="w-full min-w-[500px] text-left text-sm">
                    <caption className="mb-3 text-left text-slate-400">Lower Brier and log loss indicate better probability forecasts.</caption>
                    <thead className="border-b border-slate-700 text-slate-300">
                      <tr><th scope="col" className="pb-3 pr-4">Model</th><th scope="col" className="pb-3 pr-4">Brier</th><th scope="col" className="pb-3 pr-4">Log loss</th><th scope="col" className="pb-3 pr-4">Accuracy</th><th scope="col" className="pb-3">Draw probability</th></tr>
                    </thead>
                    <tbody>
                      {models.map((name) => {
                        const row = season.models[name];
                        return <tr key={name} className="border-b border-slate-800 last:border-0">
                          <th scope="row" className="py-3 pr-4 font-medium">{display[name]}</th>
                          <td className="py-3 pr-4 tabular-nums">{decimal(row.brier)}</td>
                          <td className="py-3 pr-4 tabular-nums">{decimal(row.log_loss)}</td>
                          <td className="py-3 pr-4 tabular-nums">{percent(row.outcome_accuracy)}</td>
                          <td className="py-3 tabular-nums">{percent(row.average_draw_probability)}</td>
                        </tr>;
                      })}
                    </tbody>
                  </table>
                </div>
                <p className="mt-4 text-sm text-slate-300">Actual draw frequency: <strong>{percent(season.actual_draw_frequency)}</strong></p>
                <div className="mt-6 grid gap-3 sm:grid-cols-2">
                  {(["first_half", "second_half"] as const).map((half) => (
                    <div key={half} className="rounded-xl border border-slate-700 bg-slate-800/60 p-4">
                      <p className="text-sm text-slate-300">Poisson {half === "first_half" ? "earlier period" : "later period"}</p>
                      <p className="mt-2 text-2xl font-semibold tabular-nums">{decimal(season.poisson_halves[half].brier)}</p>
                      <p className="mt-1 text-xs text-slate-400">Brier · {season.poisson_halves[half].matches} matches</p>
                    </div>
                  ))}
                </div>
              </section>
            ))}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">Later-season comparison uncertainty</h2>
              <p className="mt-2 text-sm text-slate-400">Ensemble minus Poisson, 2025/26. Negative loss differences favor the ensemble.</p>
              <div className="mt-5 space-y-3">
                {([
                  ["Brier score", "brier_delta"],
                  ["Log loss", "log_loss_delta"],
                  ["Accuracy", "accuracy_delta"],
                ] as const).map(([label, key]) => {
                  const d = report.heldout_ensemble_minus_poisson[key];
                  const fmt = (x: number) => key === "accuracy_delta" ? `${(x * 100).toFixed(2)} pp` : x.toFixed(6);
                  return <div key={key} className="flex flex-wrap justify-between gap-x-4 gap-y-1 border-b border-slate-800 pb-3 text-sm">
                    <span>{label}</span>
                    <span className="tabular-nums text-slate-300">{fmt(d.observed)} · 95% interval [{fmt(d.lower)}, {fmt(d.upper)}]</span>
                    <span className="w-full text-xs text-slate-400">{d.includes_zero ? "Interval includes zero: difference is inconclusive." : "Interval excludes zero; further seasons are still needed."}</span>
                  </div>;
                })}
              </div>
            </section>
            <footer className="pb-8 text-sm leading-6 text-slate-400">
              <h2 className="mb-2 font-semibold text-white">Research limitations</h2>
              <p>{report.limitations}</p>
              <p className="mt-3">Data shown here contains aggregated statistics only, generated from local research reports. It contains no individual match forecasts or bookmaker prices.</p>
            </footer>
          </>
        )}
      </div>
    </main>
  );
}
