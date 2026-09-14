import pandas as pd
from database import get_connection

print("Reading transaction data...")

# Extract
df = pd.read_csv("data/transactions.csv")

print("Data extracted successfully!")
print("Rows:", len(df))


# -------------------------
# TRANSFORM
# -------------------------

print("Cleaning and transforming data...")

# Remove duplicate transactions
df = df.drop_duplicates(
    subset=["transaction_id"]
)

# Handle missing values
df["amount"] = df["amount"].fillna(0)

df["transaction_type"] = (
    df["transaction_type"]
    .fillna("Unknown")
    .str.upper()
)

df["city"] = (
    df["city"]
    .fillna("Unknown")
    .str.title()
)

df["device_type"] = (
    df["device_type"]
    .fillna("Unknown")
)

df["fraud_type"] = (
    df["fraud_type"]
    .fillna("None")
)

# Convert transaction date
df["transaction_date"] = pd.to_datetime(
    df["transaction_date"]
).dt.date

# Remove invalid amounts
df = df[df["amount"] > 0]

print(
    "Rows after cleaning:",
    len(df)
)


# -------------------------
# LOAD INTO MYSQL
# -------------------------

print("Loading data into MySQL...")

connection = get_connection()
cursor = connection.cursor()

query = """
INSERT INTO transactions
(
    transaction_id,
    customer_id,
    transaction_date,
    amount,
    transaction_type,
    city,
    device_type,
    hour,
    is_fraud,
    fraud_type
)
VALUES
(
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s
)
ON DUPLICATE KEY UPDATE

customer_id = VALUES(customer_id),
transaction_date = VALUES(transaction_date),
amount = VALUES(amount),
transaction_type = VALUES(transaction_type),
city = VALUES(city),
device_type = VALUES(device_type),
hour = VALUES(hour),
is_fraud = VALUES(is_fraud),
fraud_type = VALUES(fraud_type)
"""

for _, row in df.iterrows():

    cursor.execute(
        query,
        (
            int(row["transaction_id"]),
            int(row["customer_id"]),
            row["transaction_date"],
            float(row["amount"]),
            row["transaction_type"],
            row["city"],
            row["device_type"],
            int(row["hour"]),
            int(row["is_fraud"]),
            row["fraud_type"]
        )
    )

connection.commit()

cursor.close()
connection.close()

print("Data loaded into MySQL successfully!")
print("ETL pipeline completed!")