import pandas as pd

# ======================================
# EXTRACT
# ======================================

print("Loading raw dataset...")

orders = pd.read_csv("../data/raw/orders.csv")

print("Dataset loaded successfully!")

# ======================================
# TRANSFORM
# ======================================

print("Starting data transformation...")

# Clean column names
orders.columns = orders.columns.str.strip()

# Remove duplicate rows
orders.drop_duplicates(inplace=True)

# Convert Order_Date to datetime
orders["Order_Date"] = pd.to_datetime(
    orders["Order_Date"],
    dayfirst=True,
    errors="coerce"
)

# Clean Delivery Person Age
orders["Delivery_person_Age"] = pd.to_numeric(
    orders["Delivery_person_Age"],
    errors="coerce"
)

# Clean Delivery Ratings
orders["Delivery_person_Ratings"] = pd.to_numeric(
    orders["Delivery_person_Ratings"],
    errors="coerce"
)

# Clean multiple deliveries
orders["multiple_deliveries"] = pd.to_numeric(
    orders["multiple_deliveries"],
    errors="coerce"
)

# Extract numeric delivery time
orders["Time_taken(min)"] = (
    orders["Time_taken(min)"]
    .astype(str)
    .str.extract(r'(\d+)')[0]
)

orders["Time_taken(min)"] = pd.to_numeric(
    orders["Time_taken(min)"],
    errors="coerce"
)

# Fill missing categorical values
orders["Weatherconditions"] = orders[
    "Weatherconditions"
].fillna("Unknown")

orders["Road_traffic_density"] = orders[
    "Road_traffic_density"
].fillna("Unknown")

# Create KPI column
orders["Delivery_Performance"] = orders[
    "Time_taken(min)"
].apply(
    lambda x: "Fast"
    if x <= 30 else "Delayed"
)

# Create Weekend Indicator
orders["Is_Weekend"] = orders[
    "Order_Date"
].dt.dayofweek.apply(
    lambda x: "Yes"
    if x >= 5 else "No"
)

print("Transformation completed!")

# ======================================
# LOAD
# ======================================

print("Saving transformed dataset...")

orders.to_csv(
    "../data/processed/clean_orders.csv",
    index=False
)

print("ETL Pipeline Executed Successfully!")