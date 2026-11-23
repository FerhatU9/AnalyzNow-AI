const noStore = { "Cache-Control": "no-store" };

export async function GET() {
  const backendUrl = process.env.FOOTBALL_API_URL?.replace(/\/+$/, "");

  if (!backendUrl) {
    return Response.json(
      { error: "The football service is not configured." },
      { status: 503, headers: noStore },
    );
  }

  try {
    const response = await fetch(backendUrl + "/v1/market-odds", {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(20000),
    });

    if (!response.ok) {
      return Response.json(
        {
          error:
            response.status === 503
              ? "Market data is unavailable. Check the backend odds configuration."
              : "The bookmaker data provider is currently unavailable.",
        },
        {
          status: response.status === 503 ? 503 : 502,
          headers: noStore,
        },
      );
    }

    const payload: unknown = await response.json();

    if (
      typeof payload !== "object" ||
      payload === null ||
      !("fixtures" in payload) ||
      !Array.isArray(payload.fixtures)
    ) {
      throw new Error("Invalid market data response");
    }

    return Response.json(payload, { headers: noStore });
  } catch {
    return Response.json(
      { error: "Unable to retrieve bookmaker market data." },
      { status: 502, headers: noStore },
    );
  }
}
