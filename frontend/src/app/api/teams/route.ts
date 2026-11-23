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
    const response = await fetch(backendUrl + "/v1/teams", {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      return Response.json(
        { error: "The team catalog is temporarily unavailable." },
        { status: response.status === 503 ? 503 : 502, headers: noStore },
      );
    }

    const body: unknown = await response.json();

    if (
      typeof body !== "object" ||
      body === null ||
      !("teams" in body) ||
      !Array.isArray(body.teams) ||
      !body.teams.every((team) => typeof team === "string")
    ) {
      throw new Error("Invalid team catalog response");
    }

    return Response.json(body, { headers: noStore });
  } catch {
    return Response.json(
      { error: "Unable to load available teams." },
      { status: 502, headers: noStore },
    );
  }
}
