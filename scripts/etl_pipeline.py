"""
ZestRoute ETL Pipeline
Extracts raw delivery orders, cleans/transforms them, and loads a
processed dataset for S3 / Snowflake / Power BI analytics.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "orders.csv"
PROCESSED_PATH = ROOT / "data" / "processed" / "clean_orders.csv"

STRING_COLUMNS = [
    "ID",
    "Delivery_person_ID",
    "Weatherconditions",
    "Road_traffic_density",
    "Type_of_order",
    "Type_of_vehicle",
    "Festival",
    "City",
]


def extract(path: Path) -> pd.DataFrame:
    print(f"Loading raw dataset from {path}...")
    return pd.read_csv(path)


def _clean_string_series(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.strip()
        .replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "NaN": pd.NA,
                "None": pd.NA,
                "null": pd.NA,
            }
        )
    )
    return cleaned


def transform(orders: pd.DataFrame) -> pd.DataFrame:
    print("Starting data transformation...")

    orders = orders.copy()
    orders.columns = orders.columns.str.strip()

    for column in STRING_COLUMNS:
        if column in orders.columns:
            orders[column] = _clean_string_series(orders[column])

    orders = orders.drop_duplicates(subset=["ID"])

    orders["Order_Date"] = pd.to_datetime(
        orders["Order_Date"],
        dayfirst=True,
        errors="coerce",
    )

    for column in [
        "Delivery_person_Age",
        "Delivery_person_Ratings",
        "multiple_deliveries",
        "Vehicle_condition",
    ]:
        orders[column] = pd.to_numeric(orders[column], errors="coerce")

    # Ratings outside the expected 1–5 range are treated as missing.
    orders.loc[
        (orders["Delivery_person_Ratings"] < 1)
        | (orders["Delivery_person_Ratings"] > 5),
        "Delivery_person_Ratings",
    ] = pd.NA

    orders["Time_taken_min"] = (
        orders["Time_taken(min)"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
    )
    orders["Time_taken_min"] = pd.to_numeric(
        orders["Time_taken_min"],
        errors="coerce",
    )
    orders = orders.drop(columns=["Time_taken(min)"])

    # Raw weather values look like "conditions Sunny".
    orders["Weatherconditions"] = (
        orders["Weatherconditions"]
        .str.replace(r"^conditions\s+", "", regex=True)
        .str.strip()
    )
    orders["Weatherconditions"] = orders["Weatherconditions"].fillna("Unknown")
    orders.loc[
        orders["Weatherconditions"].isin(["NaN", "nan", ""]),
        "Weatherconditions",
    ] = "Unknown"

    for column in [
        "Road_traffic_density",
        "Festival",
        "City",
        "Type_of_order",
        "Type_of_vehicle",
    ]:
        orders[column] = orders[column].fillna("Unknown")
        orders.loc[
            orders[column].isin(["NaN", "nan", ""]),
            column,
        ] = "Unknown"

    # Common dataset misspelling.
    orders["City"] = orders["City"].replace(
        {"Metropolitian": "Metropolitan"}
    )

    orders["Delivery_Performance"] = orders["Time_taken_min"].apply(
        lambda minutes: "Fast"
        if pd.notna(minutes) and minutes <= 30
        else ("Delayed" if pd.notna(minutes) else "Unknown")
    )

    orders["Is_Weekend"] = orders["Order_Date"].dt.day_of_week.map(
        lambda day: "Yes" if pd.notna(day) and day >= 5 else "No"
    )

    orders["Order_Month"] = orders["Order_Date"].dt.to_period("M").astype(str)
    orders["Order_Day"] = orders["Order_Date"].dt.day_name()

    # Pickup lag in minutes when both timestamps are parseable.
    order_time = pd.to_datetime(
        orders["Time_Orderd"],
        format="%H:%M:%S",
        errors="coerce",
    )
    picked_time = pd.to_datetime(
        orders["Time_Order_picked"],
        format="%H:%M:%S",
        errors="coerce",
    )
    lag_minutes = (picked_time - order_time).dt.total_seconds() / 60
    # Handle overnight wrap-around.
    lag_minutes = lag_minutes.where(lag_minutes >= 0, lag_minutes + 24 * 60)
    orders["Pickup_Lag_min"] = lag_minutes

    column_order = [
        "ID",
        "Delivery_person_ID",
        "Delivery_person_Age",
        "Delivery_person_Ratings",
        "Restaurant_latitude",
        "Restaurant_longitude",
        "Delivery_location_latitude",
        "Delivery_location_longitude",
        "Order_Date",
        "Order_Month",
        "Order_Day",
        "Time_Orderd",
        "Time_Order_picked",
        "Pickup_Lag_min",
        "Weatherconditions",
        "Road_traffic_density",
        "Vehicle_condition",
        "Type_of_order",
        "Type_of_vehicle",
        "multiple_deliveries",
        "Festival",
        "City",
        "Time_taken_min",
        "Delivery_Performance",
        "Is_Weekend",
    ]
    orders = orders[column_order]

    print("Transformation completed!")
    return orders


def load(orders: pd.DataFrame, path: Path) -> None:
    print(f"Saving transformed dataset to {path}...")
    path.parent.mkdir(parents=True, exist_ok=True)
    orders.to_csv(path, index=False)
    print(f"Saved {len(orders):,} clean rows.")


def main() -> None:
    orders = extract(RAW_PATH)
    cleaned = transform(orders)
    load(cleaned, PROCESSED_PATH)
    print("ETL Pipeline Executed Successfully!")


if __name__ == "__main__":
    main()
