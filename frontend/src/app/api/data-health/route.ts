
const noStore = { "Cache-Control": "no-store" };

export async function GET() {
  const apiUrl = process.env.FOOTBALL_API_URL?.replace(/\/+$/, "");

  if (!apiUrl) {
    return Response.json(
      { error: "The Data Health API is not configured." },
      { status: 503, headers: noStore }
    );
  }

  try {
    const response = await fetch(`${apiUrl}/v1/data-health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      return Response.json(
        { error: "Historical data health is unavailable." },
        {
          status: response.status === 503 ? 503 : 502,
          headers: noStore,
        }
      );
    }

    const data: unknown = await response.json();

    if (
      typeof data !== "object" ||
      data === null ||
      !("dataset_label" in data) ||
      typeof data.dataset_label !== "string" ||
      !("historical_matches" in data) ||
      typeof data.historical_matches !== "number" ||
      !Number.isInteger(data.historical_matches) ||
      data.historical_matches < 0 ||
      !("latest_match" in data) ||
      typeof data.latest_match !== "string" ||
      !("days_old" in data) ||
      typeof data.days_old !== "number" ||
      !Number.isInteger(data.days_old) ||
      data.days_old < 0 ||
      !("stale_after_days" in data) ||
      typeof data.stale_after_days !== "number" ||
      !Number.isInteger(data.stale_after_days) ||
      data.stale_after_days <= 0 ||
      !("is_stale" in data) ||
      typeof data.is_stale !== "boolean" ||
      data.is_stale !== (data.days_old > data.stale_after_days)
    ) {
      throw new Error("Invalid Data Health response");
    }

    return Response.json(data, { headers: noStore });
  } catch {
    return Response.json(
      { error: "Unable to retrieve reliable Data Health information." },
      { status: 502, headers: noStore }
    );
  }
}