# API Observability

AnalyzNow AI uses structured application access logs and optional **OpenTelemetry** spans for local diagnostics. This is a modest engineering improvement for later Azure deployment, **not** production-grade monitoring or cloud tracing.

## Structured HTTP logs

The FastAPI middleware emits one JSON log event per incoming request. Logged fields are limited to:

- `event`: `http_request`
- `request_id`: a new random UUID-style ID generated for each request
- `method`: HTTP verb
- `route`: matched FastAPI route template or `<unmatched>`
- `status_code`: HTTP response code
- `duration_ms`: server-side elapsed milliseconds

Each HTTP response includes the `X-Request-ID` header so a developer can identify its corresponding log. Supplied `X-Request-ID` headers are **not trusted or reflected**. Headers, request and response bodies, full URLs, query parameters, IP addresses, model probabilities and API keys are not logged.

Example event (illustrative, not a measured request):

```json
{"event":"http_request","request_id":"a28fd8b00f9343e49a767d16cba3e41d","method":"GET","route":"/health","status_code":200,"duration_ms":3.2}
```

## Optional OpenTelemetry console spans

OpenTelemetry SDK is installed with the backend. Tracing is **disabled by default**. To enable console-only spans, set:

```powershell
$env:ANALYZNOW_TRACE_CONSOLE = "1"
```

before launching the FastAPI process. The middleware then emits local spans with method, route template, HTTP status, and a generic error marker, without request bodies or credentials. It does **not** export spans to Azure, a third-party platform, or any remote collector.

In the Docker demonstration, tracing remains off by default. Its stdout JSON logs can be inspected with:

```powershell
docker compose -f compose.demo.yaml logs --tail=50 api
```

## Validation

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q tests/test_observability.py
```

The tests validate a success response, a 503 response, a 404 route, request ID behavior, and the omission of example sensitive values from the recorded log object.

## Limits

- No hosted telemetry backend, alerting, SLO dashboard, or end-to-end distributed trace propagation is implemented.
- Console span export is for local troubleshooting; it is not a persistent, secured production telemetry destination.
- Logs are metadata about API traffic, **not** evidence of forecasting accuracy.
- Local stdout logging and manual observation do not replace authentication, rate limits, secret management, audit review, or deployment safeguards.
