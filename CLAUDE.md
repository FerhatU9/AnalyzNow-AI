# Claude Code repository instructions

Follow AGENTS.md as the project's canonical engineering and safety conventions.
Work in one focused task at a time; explain the proposed change, make it, test it, then show diff and risks.
Use only locally supplied/licensed football CSV data; do not scrape football websites.
Never silently change or round-trip numerical forecasts through an LLM.
When doing code review, independently review data leakage, date parsing, provenance, and unit tests.
