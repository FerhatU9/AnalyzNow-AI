# AnalysNow AI — Technical Research

This document records sources and architectural considerations gathered during project planning. Provider prices, API coverage and legal requirements change; **verify current terms directly before purchase, publication or commercial use**.

## Product position

AnalysNow AI aims to connect statistically evaluated football forecasts with traceable data and, later, verified team/player news. The intended differentiator is transparent forecasts with reproducible historical records, not unverified claims of prediction accuracy.

Relevant products and reference approaches include [Opta Predictions](https://www.statsperform.com/products/opta-predictions/), [Forebet](https://www.forebet.com/en/faq), and source-attributed football analytics tools. Competitive differentiation is a hypothesis, not a proven market gap.

## Data and market providers

| Source | Potential use | Important constraint |
| --- | --- | --- |
| [OpenFootball](https://github.com/openfootball/football.json) | Completed match results | Community-maintained, declared CC0; scores still require quality checks |
| [football-data.org](https://www.football-data.org/) | Fixtures and league results | API plan coverage, attribution and commercial rights vary |
| [API-Football](https://www.api-football.com/) | Fixtures, squad availability, some injuries | Per-competition coverage and licensing must be verified |
| [StatsBomb Open Data](https://github.com/statsbomb/open-data) | Selected event-level football analytics | Attribution requirements; do not assume unrestricted commercial rights |
| [The Odds API](https://the-odds-api.com/) | Current bookmaker market prices | API quota, data-use restrictions and historical-odds availability depend on plan |
| Professional data vendors | Rich event and player tracking | Separate commercial contracts and redistribution permissions |

The current application uses OpenFootball historical results and The Odds API for current market data. These streams are deliberately **not blended** until fixture identities, timestamps and predictive validity can be evaluated.

## Statistical research priorities

- Compare independent-Poisson forecasts with Elo, Dixon-Coles and other relevant baselines.
- Measure walk-forward log loss, multiclass Brier score and probability calibration by season.
- Avoid training on any data published after a historical forecast cutoff.
- Evaluate statistical and bookmaker probabilities independently before training any combined model.
- Treat bookmaker-margin removal as an approximation, not a guarantee that normalized prices represent true odds.

## Engineering and career relevance

The project provides practical experience with Python, SQL, data ingestion, probability models, FastAPI, PostgreSQL, React, Next.js, TypeScript, Docker, automated testing and Git. LangGraph, RAG, MLflow and advanced cloud operations remain future capabilities, not claims about the working code.

## Legal and commercial considerations

Commercial publication requires further review of football-data licenses, bookmaker-data terms, Dutch gambling regulations, GDPR where personal information is collected, and applicable consumer protection obligations. The product currently offers research and probability comparisons, **not real-money bet placement or guaranteed winnings**.

Background sources: [Dutch Gambling Authority](https://kansspelautoriteit.nl/), [Business.gov.nl GDPR guidance](https://business.gov.nl/regulations/protection-personal-data/), and the official policies of each data provider.
