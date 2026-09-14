import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    classification_report,
    confusion_matrix
)

print("Loading dataset...")

df = pd.read_csv("data/transactions.csv")

print("Rows:", len(df))


# ==========================================
# FEATURE ENGINEERING
# ==========================================

print("\nCreating fraud detection features...")

df["transaction_date"] = pd.to_datetime(df["transaction_date"])

# Night transaction
df["is_night_transaction"] = (
    (df["hour"] >= 0) & (df["hour"] <= 5)
).astype(int)

# High value transaction
df["is_high_value"] = (
    df["amount"] > 75000
).astype(int)

# Very high value transaction
df["is_very_high_value"] = (
    df["amount"] > 100000
).astype(int)

# Weekend transaction
df["is_weekend"] = (
    df["transaction_date"].dt.dayofweek >= 5
).astype(int)

# Transaction type indicators
df["is_upi"] = (
    df["transaction_type"] == "UPI"
).astype(int)

df["is_card"] = (
    df["transaction_type"] == "Card"
).astype(int)

df["is_atm"] = (
    df["transaction_type"] == "ATM"
).astype(int)

# Suspicious combinations
df["is_upi_night"] = (
    (df["transaction_type"] == "UPI") &
    (df["hour"] <= 5)
).astype(int)

df["is_large_atm"] = (
    (df["transaction_type"] == "ATM") &
    (df["amount"] > 50000)
).astype(int)

# Log transformation of amount
df["amount_log"] = np.log1p(df["amount"])


# ==========================================
# FEATURES
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

X = df[features]
y = df["is_fraud"]


# ==========================================
# TRAIN / VALIDATION / TEST SPLIT
# ==========================================

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.4,
    random_state=42,
    stratify=y
)

X_validation, X_test, y_validation, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.5,
    random_state=42,
    stratify=y_temp
)

print("\nDataset split:")
print("Training   :", len(X_train))
print("Validation :", len(X_validation))
print("Testing    :", len(X_test))


# ==========================================
# PREPROCESSING
# ==========================================

categorical_features = [
    "transaction_type",
    "city",
    "device_type"
]

numeric_features = [
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
    "is_large_atm"
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


# ==========================================
# RANDOM FOREST MODEL
# ==========================================

model = RandomForestClassifier(
    n_estimators=250,
    max_depth=15,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ==========================================
# TRAIN
# ==========================================

print("\nTraining improved Random Forest model...")

pipeline.fit(X_train, y_train)

print("Training completed!")


# ==========================================
# VALIDATION
# ==========================================

validation_probabilities = pipeline.predict_proba(
    X_validation
)[:, 1]


# Find best threshold using F1 score

best_threshold = 0.5
best_f1 = 0

for threshold in np.arange(0.10, 0.91, 0.01):

    validation_predictions = (
        validation_probabilities >= threshold
    ).astype(int)

    score = f1_score(
        y_validation,
        validation_predictions,
        zero_division=0
    )

    if score > best_f1:
        best_f1 = score
        best_threshold = threshold


print("\nBest threshold:", round(best_threshold, 2))
print("Validation F1:", round(best_f1, 4))


# ==========================================
# FINAL TEST
# ==========================================

test_probabilities = pipeline.predict_proba(
    X_test
)[:, 1]

test_predictions = (
    test_probabilities >= best_threshold
).astype(int)


accuracy = accuracy_score(
    y_test,
    test_predictions
)

precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    test_probabilities
)

pr_auc = average_precision_score(
    y_test,
    test_probabilities
)


# ==========================================
# RESULTS
# ==========================================

print("\n================================")
print("IMPROVED MODEL PERFORMANCE")
print("================================")

print("Accuracy :", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall   :", round(recall, 4))
print("F1 Score :", round(f1, 4))
print("ROC-AUC  :", round(roc_auc, 4))
print("PR-AUC   :", round(pr_auc, 4))

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        test_predictions,
        zero_division=0
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        test_predictions
    )
)


# ==========================================
# SAVE MODEL
# ==========================================

os.makedirs("model", exist_ok=True)

joblib.dump(
    pipeline,
    "model/fraud_model.pkl"
)

joblib.dump(
    {
        "threshold": best_threshold,
        "features": features
    },
    "model/model_config.pkl"
)

print("\n================================")
print("MODEL SAVED SUCCESSFULLY")
print("================================")

print("model/fraud_model.pkl")
print("model/model_config.pkl")