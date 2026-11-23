# AnalysNow AI — initial research snapshot

Research date: 2026-11-18. Links/prices may change. This is a technical starting point, not legal advice or a purchase authorization.

## Competitors / positioning

- Opta Predictions: robust commercial predictions built on deep historical and live data, including tournament/match outcomes. https://www.statsperform.com/products/opta-predictions/
- Forebet: mathematically driven football predictions and betting-market value views. https://www.forebet.com/en/faq
- Touchline Atlas: public forecast/baseline/track-record transparency and locked forecasts. https://thetouchlineatlas.com/accuracy/
- Differentiation hypothesis, **not verified market gap**: combine rigorously locked pre-match numerical forecasts + independent claim verification with sources + temporal RAG + visible 'what changed' records. Validate with user research before commercial investment.

## Data provider decision matrix

| Candidate | Publicly documented starting price | Useful coverage | Key caveat | Suggested place |
| --- | --- | --- | --- | --- |
| football-data.org | €0 free, €29/month ML Pack Light; other tiers listed | Fixtures/results/league; paid history/advanced data | Historical feature depth varies by plan; require visible attribution; verify commercial rights | MVP API candidate after rights check |
| API-Football (API-SPORTS) | Free 100 requests/day, Pro $16/month excl. VAT | Matches, lineups, some injury availability; coverage depends on league and season | Features not universal; license for republication/AI training must be checked | Team availability experiment |
| StatsBomb open data | Public for football research/interest | Detailed event data/xG on selected seasons | Attribution/logo required for published analysis; commercial rights not presumed | Separate research experiments |
| Football-Data.co.uk CSV | Free for personal/academic/research in stated fair-use conditions | Long historical fixtures/results; some match stats and odds | Explicitly NOT intended for commercial or AI-training projects; manual or light ≤ twice weekly automated downloads for permitted research | Personal baseline only, if use complies |
| The Odds API | Free credits; paid historical snapshots | Bookmaker odds and historical odds | Historical odds on paid tier; bookmaker/legal use restrictions apply | Defer until matched-prediction pipeline and legality checked |
| Opta/Stats Perform, Sportradar, Wyscout | Quote / enterprise contract | Extensive professional/event/player data | Procurement, redistribution, price, rights | Advanced/commercial evaluation |

Sources:
- https://www.football-data.org/pricing
- https://www.football-data.org/documentation/faq
- https://www.api-football.com/pricing
- https://github.com/hudl/open-data
- https://football-data.co.uk/contact.php
- https://the-odds-api.com/historical-odds-data/

## Job-market evidence

- 433 Jr AI Engineer (Amsterdam): Python, SQL, APIs/JSON, LLM understanding, AI coding agents including Claude Code / Codex; Docker, Airflow, Git, cloud, RAG, AI agents and MLOps optional. Actual posting: https://careers.by433.com/o/jr-ai-engineer
- Salt GenAI Engineer (Amsterdam): LangChain/Graph/MCP, RAG, Python/FastAPI/React/Next.js/TypeScript, Docker/cloud, evaluation: https://welovesalt.com/jobs/genai-engineer-715538
- Architectural decision: teach Python/SQL/APIs and validated modeling first; introduce LangGraph, pgvector, web UI and deployment when the statistically useful flow exists.
- Career warning: 433 specifically requires independent right to work in the Netherlands without visa sponsorship; a residence permit expiration date alone is not proof of unrestricted work authorization.

## Legal / security

- Start as educational football statistics/research software, **not** real-money bet placement or gambling affiliate platform.
- Dutch Kansspelautoriteit gambling advertising restrictions: https://kansspelautoriteit.nl/belangrijkste-regels-voor-kansspelreclame
- GDPR/privacy for public website and user accounts: https://business.gov.nl/regulations/protection-personal-data/
- Content rights: a source being readable on the web does NOT grant permission to scrape, embed or redistribute it.
- Any public odds comparison, paid tips, betting affiliate service, financial claims, minors, and operator integration require country-by-country legal review.

## Development-agent accounts

- Claude Code: native Windows PowerShell install `irm https://claude.ai/install.ps1 | iex`; requires eligible paid Claude subscription or Anthropic Console/API billing, not a free Claude account. Docs: https://code.claude.com/docs/en/getting-started
- OpenAI Codex CLI: install `npm install -g @openai/codex` and sign in with ChatGPT; available depending on plan/usage. Docs: https://github.com/openai/codex and https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- Secret handling: the coding-agent CLI is separate from product LLM API, no product API keys needed for the current starter.

## Budget ranges to plan for (not price quotations)

- **Local synthetic starter**: €0 incremental required for football data / deployed services. Windows/Python/VS Code/Git free; OpenAI/Anthropic coding-agent access depends on existing plan.
- **Early real-data MVP**: €0–€60/month *potentially* for football data if required endpoints/terms fit; e.g. football-data.org ML Pack Light €29/mo or API-Football Pro $16/mo (different currencies; taxes excluded). RAG/LLM and hosting would be additional.
- **Hosted news/RAG platform**: reserve a provisional total €40–€200/month for low-traffic experiment before exact usage metering; NOT a supplier quote and excludes enterprise licensing, staff time, legal review and commercial news feeds.
- **Commercial**: no credible total cost before quotes/licensing, traffic model and legal scope. Separate recurring hosting, provider, odds, embeddings/LLMs, observability and data retention costs in a spreadsheet later.

## M1 update: open public-domain source chosen

- OpenFootball `football.json` states its JSON data and scripts are dedicated to public domain and the GitHub repository labels license CC0-1.0. The English Premier League season path is `<season>/en.1.json`, for example `2024-25/en.1.json`. Source and license: https://github.com/openfootball/football.json and https://github.com/openfootball/football.json/blob/master/LICENSE.md.
- The upstream is community maintained; autogenerated latest JSON is not necessarily current because upstream Football.TXT updates may lag. Use completed historical seasons first, preserve all downloaded JSON with hashes and later independently verify key results.
- Source snapshots and manifest are saved locally. Full real-world fetch, completeness validation and evaluation on Windows are pending, as this authoring environment has no direct access to download large raw source files.
