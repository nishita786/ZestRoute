# ZestRoute Architecture

## Data Flow

```text
data/raw/orders.csv
        │
        ▼
scripts/etl_pipeline.py   (Python + Pandas)
        │
        ▼
data/processed/clean_orders.csv
        │
        ├──► scripts/upload_to_s3.py ──► AWS S3 data lake
        │                                   (raw/ + processed/)
        │                                         │
        │                                         ▼
        │                               Snowflake stage + ORDERS table
        │                                         │
        │                                         ▼
        │                               SQL analytics views
        │                               (sql/03_main_analytics.sql)
        │                                         │
        └─────────────────────────────────────────┴──► Power BI dashboard
```

## Layers

1. **Ingestion** — Raw food-delivery orders land in `data/raw/`.
2. **ETL** — Python cleans nulls, strips prefixes/whitespace, derives KPI columns.
3. **Data lake** — Processed CSV is uploaded to S3 under `processed/`.
4. **Warehouse** — Snowflake loads the processed file and exposes analytics views.
5. **BI** — Power BI connects to Snowflake views / processed CSV for KPIs and agent performance.

## Key Analytics Views

| View | Purpose |
|------|---------|
| `delivery_kpis_view` | Headline KPIs (orders, avg time, avg rating) |
| `delivery_agent_view` / `delivery_performance_view` | Per-agent rating, time, volume |
| `festival_impact_view` | Festival vs non-festival delivery impact |
| `traffic_impact_view` | Traffic density vs delivery time |
| `weather_impact_view` | Weather vs delivery time |
| `city_performance_view` | City-level operational summary |
| `weekend_impact_view` | Weekend vs weekday comparison |
