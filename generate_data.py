import pandas as pd
import numpy as np
import os

np.random.seed(42)

n = 20000

cities = [
    "Bangalore",
    "Mumbai",
    "Delhi",
    "Chennai",
    "Hyderabad",
    "Pune",
    "Kolkata",
    "Ahmedabad"
]

transaction_types = [
    "UPI",
    "Card",
    "ATM",
    "Net Banking"
]

devices = [
    "Mobile",
    "Laptop",
    "ATM"
]

fraud_types = [
    "Unauthorized Transaction",
    "Card Fraud",
    "UPI Fraud",
    "Account Takeover",
    "Suspicious Transfer"
]

data = {
    "transaction_id": range(1, n + 1),

    "customer_id": np.random.randint(
        1001,
        5001,
        n
    ),

    "amount": np.round(
        np.random.lognormal(
            mean=8.5,
            sigma=1.0,
            size=n
        ),
        2
    ),

    "transaction_type": np.random.choice(
        transaction_types,
        n,
        p=[0.45, 0.30, 0.10, 0.15]
    ),

    "city": np.random.choice(
        cities,
        n
    ),

    "device_type": np.random.choice(
        devices,
        n,
        p=[0.65, 0.25, 0.10]
    ),

    "hour": np.random.randint(
        0,
        24,
        n
    )
}

df = pd.DataFrame(data)

# Limit transaction amount
df["amount"] = df["amount"].clip(
    100,
    200000
)

# Start with normal transactions
df["is_fraud"] = 0

df["fraud_type"] = "None"

# Fraud conditions
condition1 = df["amount"] > 100000

condition2 = (
    (df["hour"] >= 0) &
    (df["hour"] <= 4) &
    (df["amount"] > 30000)
)

condition3 = (
    (df["transaction_type"] == "UPI") &
    (df["amount"] > 50000) &
    (df["hour"] <= 5)
)

condition4 = (
    (df["device_type"] == "ATM") &
    (df["amount"] > 60000)
)

fraud_condition = (
    condition1 |
    condition2 |
    condition3 |
    condition4
)

df.loc[fraud_condition, "is_fraud"] = 1

# Add additional random fraud
normal_indices = df[
    df["is_fraud"] == 0
].index

additional_fraud = np.random.choice(
    normal_indices,
    size=int(n * 0.02),
    replace=False
)

df.loc[
    additional_fraud,
    "is_fraud"
] = 1

# Assign fraud types
fraud_indices = df[
    df["is_fraud"] == 1
].index

df.loc[
    fraud_indices,
    "fraud_type"
] = np.random.choice(
    fraud_types,
    len(fraud_indices)
)

# Add date
dates = pd.date_range(
    start="2026-01-01",
    periods=180,
    freq="D"
)

df["transaction_date"] = np.random.choice(
    dates,
    n
)

# Arrange columns
df = df[
    [
        "transaction_id",
        "customer_id",
        "transaction_date",
        "amount",
        "transaction_type",
        "city",
        "device_type",
        "hour",
        "is_fraud",
        "fraud_type"
    ]
]

os.makedirs(
    "data",
    exist_ok=True
)

df.to_csv(
    "data/transactions.csv",
    index=False
)

print("Dataset created successfully!")
print("Rows:", len(df))

print(
    "Fraud transactions:",
    df["is_fraud"].sum()
)

print(
    "Fraud percentage:",
    round(
        df["is_fraud"].mean() * 100,
        2
    ),
    "%"
)

print("\nSample:")
print(df.head())