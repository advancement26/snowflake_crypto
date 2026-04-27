cap |

---

## dbt Model Architecture

### Staging Layer — `models/staging/`

One model per source. Cleans raw data, standardises column names, casts types, handles NULLs. No business logic at this layer.

### Mart Layer — `models/marts/`

Business logic, cross-currency calculations, aggregations, and classification. Serves directly as the Looker Studio data source.

| Mart | Description |
|------|-------------|
| `mart_coin_performance` | Top coins by market cap with ZAR/EUR cross-currency pricing, performance categorisation (Strong Gainer → Strong Loser), and supply metrics |
| `mart_market_sentiment` | Price dominance by coin, 24h momentum signals, EUR pricing table, coin-level sentiment classification |
| `mart_fx_crypto_correlation` | BTC/ETH dominance vs Fear & Greed index over time, market risk signal (High Capitulation Risk vs Normal Conditions) |

---

## Data Quality

dbt generic tests implemented across staging and mart layers:

```yaml
models:
  - name: mart_coin_performance
    columns:
      - name: coin_id
        tests:
          - not_null
          - unique
      - name: current_price_usd
        tests:
          - not_null
      - name: market_cap_usd
        tests:
          - not_null
```

Two-layer validation approach:
- **Automated** — dbt not_null and unique tests run on every pipeline execution
- **Visual** — dashboard KPIs manually verified against Snowflake source data before delivery

---

## Orchestration — Apache Airflow

The pipeline runs automatically every day at 06:00 UTC via an Airflow DAG (`dags/crypto_pipeline_dag.py`):

```
[Fetch APIs] → [Load to Snowflake] → [dbt run] → [dbt test] → [Dashboard refreshes]
```

Zero manual intervention required after deployment.

---

## Containerisation — Docker

The full pipeline is containerised using Docker and Docker Compose for complete portability:

```bash
# Start the pipeline
docker-compose up
```

Runs identically on any machine — no environment setup, no dependency conflicts.

---

## Project Structure

```
crypto-analytics-snowflake/
├── models/
│   ├── staging/
│   │   ├── sources.yml
│   │   ├── schema.yml
│   │   ├── stg_coingecko_markets.sql
│   │   ├── stg_exchange_rates.sql
│   │   ├── stg_fear_greed_index.sql
│   │   └── stg_global_markets.sql
│   └── marts/
│       ├── mart_coin_performance.sql
│       ├── mart_market_sentiment.sql
│       └── mart_fx_crypto_correlation.sql
├── dags/
│   └── crypto_pipeline_dag.py
├── dbt_project.yml
├── docker-compose.yml
├── Dockerfile
├── ingest.py
├── requirements.txt
└── .gitignore
```

---

## Dashboard

Live Looker Studio executive dashboard — 3 report pages:

| Page | Key Insights |
|------|-------------|
| **Coin Performance** | Top 10 coins by market cap (USD & ZAR), performance category distribution, supply analysis |
| **Market Sentiment** | BTC price dominance at 96.2%, EUR coin prices, 24h momentum by coin |
| **FX Crypto Correlation** | Fear & Greed index trend, BTC dominance over time, market risk signal classification |

---

## Key Engineering Decisions

**Marts separated by domain** — performance, sentiment, and FX correlation serve distinct analytical purposes. Forced joins across unrelated domains were deliberately avoided to preserve mart integrity and query performance.

**Staging models kept thin** — all cleaning at staging, all business logic at marts. Clean separation makes debugging and testing straightforward.

**ZAR cross-currency pricing** — built natively into `mart_coin_performance` via a cross join with `stg_exchange_rates`, reflecting real-world multi-currency reporting requirements.

**Two-layer data quality** — automated dbt tests catch structural issues at ingestion; human visual validation on the dashboard catches aggregation logic errors. Neither replaces the other.

---

## Author

**Proud Kudzai Ndlovu** — Data Engineer | Analytics Engineer
- GitHub: [ApostolicDA](https://github.com/ApostolicDA)
- LinkedIn: [proud-ndlovu-89070854](https://linkedin.com/in/proud-ndlovu-89070854)
- Open to remote roles globally · SAST (UTC+2)
