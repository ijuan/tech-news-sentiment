# SCOPE.md

**Project:** Tech News Sentiment Aggregator
**Window:** Aug 5 – Sep 1, 2026 (4 weeks)
**Owner:** Ian Ang
**Status:** Week 1 — source selection

This document is the contract. If a thing isn't in "In Scope," it doesn't get built.
Changes to scope go in the Decision Log at the bottom, with a date and a reason.

---

## 1. What this is

A daily aggregator that ingests company news for a watchlist of large-cap tech
tickers, scores each article's sentiment with a model trained on hand-labeled
data, and delivers **a pre-market email digest** — a 5-minute read that lands
before the open.

The digest reports:

- per-ticker daily sentiment and article volume
- an aggregate tech-sentiment roll-up across the watchlist
- a flag when a ticker's daily sentiment deviates unusually far from its own
  30-day rolling baseline

**Primary interface is email, not a web app.** The FastAPI service is what
generates and serves the data; the email is what people actually read.

## 2. What this is NOT

- **Not a predictor.** It does not forecast price, direction, or volatility.
- **Not a trading tool.** No signals, no recommendations, no "helped people trade."
- **Not a notebook.** It ships as a deployed service with an API, tests, and CI.
- **Not an LLM wrapper.** Ground truth comes from hand-labeled articles, not from
  any vendor's sentiment score or from an LLM's output.

The framing is descriptive: *here is what tech news coverage looks like today, and
here is when it is unusual.* Users draw their own conclusions.

---

## 3. Watchlist

10–15 individual large-cap tech names (Nasdaq-100 heavyweights), rolled up into an
aggregate tech-sentiment view.

**Rationale:** individual companies have clean, company-specific news that can be
labeled unambiguously — which keeps the per-ticker anomaly detection and the
labeling work meaningful. The roll-up is what makes it useful to an NQ-trading
audience, since these names effectively drive the index.

**Rejected alternative:** covering only ES/NQ index futures. Two highly correlated
macro instruments with no company-specific news; collapses the per-ticker
machinery into one fuzzy whole-economy number.

**Watchlist (locked Aug 6) — 12 tickers:**

`NVDA` `AAPL` `MSFT` `AMZN` `GOOGL` `AVGO` `META` `TSLA` `MU` `AMD` `PLTR` `INTC`

**Selection criterion:** not "which companies will grow" — that's an investment
thesis. The test is which tickers produce enough clean, company-specific news to
support a stable 30-day baseline and an unambiguous labeled set.

**Decisions to remember:**
- **GOOGL over GOOG** — same company, two share classes. Chose one deliberately.
  If a source tags an article with both, that is *one* article, not two.
- **META is a common English word.** Any headline-matching fallback will pull
  garbage. Rely on ticker tags, not string matching, for this one.
- **CSCO cut** — enterprise networking generates too little press to support a
  meaningful deviation flag.
- **PLTR caveat** — high article volume, but much of it is retail commentary and
  "trending on WallStreetBets" filler rather than company news. Expect a noisier
  labeled set; watch it during labeling.
- **No private companies.** SpaceX and similar have no ticker and no
  symbol-tagged news.
- **WMT excluded** — retail, not tech. Different news vocabulary would add noise.

---

## 4. Stack (locked)

| Layer | Choice |
|---|---|
| Language | Python |
| API | FastAPI + Pydantic |
| Database | PostgreSQL on AWS RDS |
| Email delivery | AWS SES |
| Scheduling | EventBridge Scheduler (pre-market cron) |
| Templating | Jinja2 → inline-CSS HTML email |
| Frontend | React + TypeScript — **stretch goal only** (see §6) |
| Container | Docker → ECR → ECS Express Mode |
| Storage | S3 |
| Ops | IAM, CloudWatch |
| Testing | pytest + GitHub Actions |
| ML | scikit-learn baseline, then a small transformer |

**Explicitly excluded:** Java, Kubernetes, Kafka, Terraform, Next.js, Supabase,
MLflow, microservices, Lambda.

Note: AWS App Runner is closed to new customers as of Apr 30 2026 — ECS Express
Mode is the replacement. Fargate is not free (~$10–15/mo). **Set a billing alarm
on day one.**

---

## 5. In Scope

**Ingestion**
- 4–6 news sources, each with a real API or stable structure
- Per-source retry and backoff
- Deduplication of syndicated/wire copy
- Graceful degradation when one source fails

**Storage**
- Normalized article schema across sources
- Reliable timestamps (all baseline logic is time-based)

**ML**
- A few hundred hand-labeled articles as ground truth
- TF-IDF + logistic regression baseline
- A trained classifier measured against that baseline
- Honest error analysis: what it gets wrong and why

**Analysis**
- Per-ticker daily sentiment score
- 30-day rolling baseline + deviation flag
- Aggregate tech-sentiment roll-up
- Sentiment *dispersion* as a second metric (see §8)

**Serving**
- FastAPI endpoints with input validation (the digest consumes these)
- Deployed and publicly reachable

**Email digest**
- Scheduled pre-market send
- HTML template that renders correctly in Gmail and Apple Mail
- Plain-text fallback
- Subscribe / unsubscribe handling
- Idempotent send: a double-fired schedule must not double-send
- Bounce and complaint handling
- Send log — what went out, to whom, when, and whether it succeeded

**Quality**
- pytest suite
- GitHub Actions on every push
- Delivery metrics: subscriber count, successful sends, open rate

**Honesty module**
- A separate backtest asking whether flagged days precede abnormal returns,
  which reports a negative result if that's what it finds

---

## 6. Out of Scope

Say no to all of these. They are not "later" — they are not part of this project.

- Price prediction, direction calls, or any trading signal
- Real-time / streaming ingestion (daily batch only)
- More than ~15 tickers
- Non-tech sectors
- Options, crypto, forex
- User accounts or auth (email address + unsubscribe token is the whole identity model)
- Per-subscriber customized watchlists — everyone gets the same digest
- Mobile app
- Intraday alerts or push notifications — one scheduled send per trading day
- LLM-generated summaries or explanations
- Model architecture written from scratch
- Any second project running in parallel

**Stretch goal, week 4 only if there is room:** a static archive page the email
links to, built in React + TypeScript. Only if the core is done, tested, and
sending reliably. Not a reason to slip anything above.

---

## 7. Ground Rules

1. **I write all the code.** AI for docs, debugging, concept explanations, and
   post-hoc review. Not for generating implementation.
2. **Every decision must be interview-defensible.** If I can't narrate why X over
   Y, it doesn't ship.
3. **Deploy in week 1, not week 4.** A deployed skeleton beats an undeployed
   system.
4. **Narrow and complete over broad and half-done.**
5. **No resume number that isn't measured.** No claimed user counts without
   instrumentation.
6. **Vendor sentiment scores are features or baselines, never labels.**

---

## 8. Design notes carried in from research

**Sentiment dispersion.** A student paper (Sinha, *Oxford Journal of Student
Scholarship*, June 2026) found that sentiment *disagreement* drops during market
stress, using Twitter data pooled at market level. Everything else in it was null.
We are not replicating it — we are testing the dispersion idea on **news** rather
than tweets, at **ticker** level rather than pooled. That's a stronger claim and
it's what their own future-work section asks for.

**Not "an Oxford study."** Student journal, single author. Describe it accurately.

---

## 9. Sources

Criteria: real API or stable structure · archive depth ≥ 1 year · free tier ·
covers the watchlist · clean timestamps · terms permit storage ·
**distinct underlying provider**.

| Source | Status | Notes |
|---|---|---|
| Alpaca | Tested ✅ | Works; ≥1yr archive. **100% Benzinga** — counts as one provider |
| Finnhub | Candidate | 60 calls/min; ~1yr history on free tier |
| Alpha Vantage | Candidate | 1000 articles/call; per-ticker relevance score; 25 req/day |
| Marketaux | Candidate | Per-entity sentiment + passage highlights; ~100 req/day |
| Financial Modeling Prep | Candidate | 250 calls/day; ~5yr history |
| NewsData.io | Candidate | 200 credits/day; no ticker tagging |
| GNews | Candidate | 100 req/day; 12h delay; 10 articles/request |
| GDELT | Stretch | Unlimited, deep archive, but research-grade |
| SEC EDGAR | Stretch | Free forever, exact attribution, but filings ≠ news |

> TODO: final 5 not yet selected. Docs lie about archive depth — verify each one
> by pulling a real article from a year ago before committing.

---

## 10. Known Issues

- **Symbol over-tagging.** Sources tag mega-caps into articles that aren't about
  them (one Alpaca market-wrap was tagged with 44 tickers). This biases per-ticker
  volume toward large names and makes baselines non-comparable across tickers.
  Candidate fixes: drop articles above N symbols; require the ticker in the
  headline; use a relevance score. **Unresolved — do not solve before week 2.**
- **Empty article bodies.** Some sources return headline + summary only. Decide
  deliberately whether to label headlines or full text; don't discover it in week 3.
- **Wire duplication across sources.** If two sources resell the same wire, dedupe
  numbers will look strange. Check the provider field before adding any source.
- **SES sandbox — WEEK 1 BLOCKER.** Every new AWS account starts SES in sandbox
  mode: sending is restricted to addresses you've individually verified, so you
  cannot mail the Discord. Moving to production access is a request that takes
  roughly a day and can be rejected. **File it in week 1.** Also needed: domain
  verification with DKIM/SPF records, or the digest lands in spam.
- **HTML email is not HTML.** Email clients strip `<style>` blocks and ignore most
  modern CSS. Layouts are table-based, CSS is inline, and every client renders
  differently. Budget real time for this; do not discover it the night before the
  first send.

**Week 1 non-code checklist**
- [ ] AWS billing alarm
- [ ] SES production access request filed
- [ ] Domain verified (DKIM + SPF)
- [ ] Alpha Vantage educational/open-source quota request emailed

---

## 11. Decision Log

| Date | Decision | Reason |
|---|---|---|
| Aug 4 | Python, not Java | Raytheon is 1 of ~100 targets; not worth the project |
| Aug 4 | Descriptive, not predictive | Sentiment doesn't cleanly predict direction; honest scope |
| Aug 5 | Tech names rolled up, not ES/NQ only | Preserves per-ticker work; still relevant to NQ traders |
| Aug 5 | 4–6 sources, not 1 | Single source is fragile and removes the dedupe work |
| Aug 6 | Borrow dispersion idea, don't replicate paper | Replication collapses the system into a notebook |
| Aug 6 | Delete Dwindle from resume once this ships | An unexplainable project poisons trust in the whole resume |
| Aug 6 | Email digest replaces frontend as primary interface | Slots into an existing pre-market habit; subscriber/open-rate metrics are real and provable; scheduling, idempotency, and delivery failure are better engineering than rendering a table. Cost: gives up the React learning goal, now a stretch |
| Aug 6 | Watchlist locked at 12 tech tickers | Selected on news volume and naming clarity, not growth outlook — the criterion is whether a stable 30-day baseline is possible |