
export async function POST(request: Request) {
  try {
    const body = await request.json();

    const apiUrl = process.env.FOOTBALL_API_URL;

    if (!apiUrl) {
      return Response.json(
        { error: "Backend URL is not configured" },
        { status: 503 }
      );
    }

    const response = await fetch(`${apiUrl}/v1/forecast`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    const data = await response.json();

    return Response.json(data, {
      status: response.status,
    });

  } catch {
    return Response.json(
      { error: "Unable to connect to the forecasting service" },
      { status: 502 }
    );
  }
}