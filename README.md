# Tech News Sentiment Aggregator

A daily pre-market email digest summarizing news sentiment across 12 large-cap technology stocks.

**Status:** In active development (August–September 2026). Not yet deployed.

---

## What this is

Every morning before the US market opens, this pipeline ingests financial news for a fixed watchlist of tech companies, scores each article's sentiment with a model trained on hand-labeled data, aggregates those scores into per-ticker and sector-wide views, and emails a five-minute digest to subscribers.

## What this is not

This is a **descriptive** tool, not a predictive one. It reports what the news sentiment *was*, not what prices *will do*. It does not generate trade signals, and it is not investment advice.

A separate backtest evaluates whether the sentiment measures carry any relationship to subsequent returns. Results of that backtest are reported honestly, including negative results.

---

## Watchlist

NVDA · AAPL · MSFT · AMZN · GOOGL · AVGO · META · TSLA · MU · AMD · PLTR · INTC

Tickers were selected for **news volume**, not investment thesis — each needs enough clean company-specific coverage to support a stable 30-day sentiment baseline.

---

## Data sources

Two news APIs, each fulfilling a distinct role. Three were tested live; the probe scripts used to evaluate them are preserved in `explore/`. Alpha Vantage was dropped in October 2026 when its news endpoint became premium-only.

| Source | Role | Why |
|---|---|---|
| **Alpaca** | Historical backfill + Benzinga feed | Deep archive, real publisher URLs, ISO-8601 timestamps, multi-symbol tagging. Mostly Benzinga. |
| **Finnhub** | Daily incremental pull | Genuine multi-publisher aggregator. Redirect URLs and noisy symbol tagging limit its use for deduplication. |

### Findings from source evaluation

- **Relevance filtering is a required pipeline stage, not a per-source patch.** Every source tested over-tags articles with tickers they barely mention. During evaluation, Alpha Vantage's `relevance_score` discriminates meaningfully only above roughly **0.85** — genuine company articles cluster in 0.85–1.00 while off-topic articles cluster in 0.55–0.75. The default 0.5 cutoff is far too permissive.
- **Vendor-supplied sentiment scores are heavily compressed toward neutral-positive** and are not used as training labels. Ground truth for this project is hand-labeled.
- **Timestamp formats differ across all three sources** (ISO-8601, Unix epoch, and a compact string with no timezone marker), which is why normalization to timezone-aware UTC happens at ingestion.
- **Alpaca and Finnhub both carry Benzinga content**, so cross-source deduplication cannot rely on URL matching alone.

---

## Architecture

```
News APIs → Ingestion → Normalization → Relevance filter → Sentiment model
                                                                  ↓
                              Email digest ← Aggregation ← PostgreSQL
```

## Stack

| Layer | Technology |
|---|---|
| Language | Python |
| API | FastAPI, Pydantic |
| Database | PostgreSQL (AWS RDS) |
| ML | scikit-learn baseline, then transformer fine-tuning |
| Email | AWS SES, EventBridge Scheduler, Jinja2 |
| Deployment | Docker → ECR → ECS |
| Storage / Ops | S3, IAM, CloudWatch |
| Testing | pytest, GitHub Actions |

---

## Machine learning approach

**Ground truth is hand-labeled.** A few hundred articles are annotated manually against a written rubric. Vendor sentiment scores and LLM-generated labels are deliberately not used as training targets, since both introduce systematic bias the model would simply learn to reproduce.

**Two-stage modeling:**

1. **Baseline** — TF-IDF features with logistic regression, plus naive Bayes and linear SVM for comparison. Evaluated against a majority-class baseline.
2. **Transformer** — fine-tuned DistilBERT or FinBERT, *only if* it measurably beats the baseline on the same held-out set.

If the classical baseline wins, that result is reported as-is. On a few-hundred-example dataset it is a plausible outcome.

**Evaluation** uses macro-averaged precision, recall, and F1 rather than raw accuracy, since the label distribution is imbalanced toward neutral. Train/test splits are **temporal**, never random — random splitting a time series leaks future information into training.

---

## Repository layout

```
├── explore/        # Source evaluation scripts (kept as documentation)
├── src/            # Pipeline code
├── tests/          # pytest suite
├── SCOPE.md        # Full project scope, decisions, and known issues
└── main.py         # Entry point
```

See [SCOPE.md](SCOPE.md) for the complete specification, decision log, and current known issues.

---

## Requirements

- Python 3.11+
- PostgreSQL
- API keys for Alpaca and Finnhub (stored in `.env`, never committed)

## License

MIT