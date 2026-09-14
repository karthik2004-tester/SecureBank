import pandas as pd
import joblib
import numpy as np


# ==========================================
# LOAD MODEL
# ==========================================

model = joblib.load("model/fraud_model.pkl")
config = joblib.load("model/model_config.pkl")

threshold = config["threshold"]

print("Fraud detection model loaded!")
print("Model threshold:", round(threshold, 2))


# ==========================================
# TAKE TRANSACTION INPUT
# ==========================================

print("\nEnter transaction details")

transaction_id = int(input("Transaction ID: "))
customer_id = int(input("Customer ID: "))
amount = float(input("Amount: "))

transaction_type = input(
    "Transaction Type (UPI/Card/ATM/Net Banking): "
)

city = input(
    "City: "
)

device_type = input(
    "Device (Mobile/Laptop/ATM): "
)

hour = int(input("Transaction Hour (0-23): "))


# ==========================================
# CREATE FEATURES
# ==========================================

transaction_date = pd.Timestamp("2026-01-01")


data = pd.DataFrame({
    "transaction_id": [transaction_id],
    "customer_id": [customer_id],
    "transaction_date": [transaction_date],
    "amount": [amount],
    "transaction_type": [transaction_type],
    "city": [city],
    "device_type": [device_type],
    "hour": [hour]
})


data["is_night_transaction"] = (
    (data["hour"] >= 0) &
    (data["hour"] <= 5)
).astype(int)

data["is_high_value"] = (
    data["amount"] > 75000
).astype(int)

data["is_very_high_value"] = (
    data["amount"] > 100000
).astype(int)

data["is_weekend"] = 0

data["is_upi"] = (
    data["transaction_type"] == "UPI"
).astype(int)

data["is_card"] = (
    data["transaction_type"] == "Card"
).astype(int)

data["is_atm"] = (
    data["transaction_type"] == "ATM"
).astype(int)

data["is_upi_night"] = (
    (data["transaction_type"] == "UPI") &
    (data["hour"] <= 5)
).astype(int)

data["is_large_atm"] = (
    (data["transaction_type"] == "ATM") &
    (data["amount"] > 50000)
).astype(int)

data["amount_log"] = np.log1p(data["amount"])


# ==========================================
# SELECT FEATURES
# ==========================================

features = [
    "amount",
    "amount_log",
    "hour",
    "is_night_transaction",
    "is_high_value",
    "is_very_high_value",
    "is_weekend",
    "is_upi",
    "is_card",
    "is_atm",
    "is_upi_night",
    "is_large_atm",
    "transaction_type",
    "city",
    "device_type"
]

X = data[features]


# ==========================================
# PREDICTION
# ==========================================

probability = model.predict_proba(X)[0][1]

prediction = (
    probability >= threshold
)


# ==========================================
# RISK LEVEL
# ==========================================

if probability < 0.30:
    risk_level = "LOW"

elif probability < 0.50:
    risk_level = "MEDIUM"

elif probability < 0.70:
    risk_level = "HIGH"

else:
    risk_level = "CRITICAL"


# ==========================================
# RESULT
# ==========================================

print("\n================================")
print("TRANSACTION ANALYSIS")
print("================================")

print("Transaction ID :", transaction_id)
print("Customer ID    :", customer_id)
print("Amount         :", amount)
print("Fraud Probability:", round(probability * 100, 2), "%")
print("Risk Level     :", risk_level)

if prediction:
    print("Prediction     : FRAUDULENT TRANSACTION")
else:
    print("Prediction     : NORMAL TRANSACTION")

print("================================")