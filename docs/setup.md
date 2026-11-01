# Setup & Run Guide

## 1. Local environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Run the ETL pipeline

```bash
python scripts/etl_pipeline.py
```

This reads `data/raw/orders.csv` and writes `data/processed/clean_orders.csv`.

Optional inspection:

```bash
python scripts/inspect_data.py
```

## 3. Upload to AWS S3

Configure AWS credentials (CLI profile, env vars, or IAM role), then:

```bash
export AWS_REGION=ap-south-1
export S3_BUCKET=your-zestroute-data-lake-bucket
python scripts/upload_to_s3.py
```

Expected lake layout:

```text
s3://<bucket>/
  raw/orders.csv
  processed/clean_orders.csv
```

## 4. Snowflake analytics

1. Open Snowsight and set role/warehouse/database/schema to `ZESTROUTE_*` objects.
2. Run `sql/01_setup.sql` (replace the S3 bucket placeholder).
3. Load data with `sql/02_load_orders.sql` (stage `COPY` or UI upload of `clean_orders.csv`).
4. Create analytics views with `sql/03_main_analytics.sql`.

## 5. Power BI dashboard

1. Open `dashboards/ZestRoute_Delivery_Analytics.pbix` in Power BI Desktop.
2. Connect to Snowflake views (`delivery_agent_view`, `festival_impact_view`, etc.) or import `clean_orders.csv`.
3. Publish to the Power BI service workspace for sharing.

## Project artifacts

- Screenshots live in `screenshots/`
- Architecture notes live in `docs/architecture.md`
