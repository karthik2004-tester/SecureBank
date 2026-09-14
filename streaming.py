import os
import json
from dotenv import load_dotenv
from datetime import date

load_dotenv()

os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["hadoop.home.dir"] = "C:\\hadoop"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    DoubleType,
    StringType
)

import joblib
import pandas as pd
import mysql.connector


# --------------------------------------------------
# 1. Load ML model
# --------------------------------------------------

model = joblib.load("model/fraud_model.pkl")
model_config = joblib.load("model/model_config.pkl")

threshold = model_config.get("threshold", 0.5)
feature_columns = model_config.get("features", [])


# --------------------------------------------------
# 2. Create Spark session
# --------------------------------------------------

spark = SparkSession.builder \
    .appName("BankingFraudStreaming") \
    .master("local[*]") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"
    ) \
    .getOrCreate()


spark.sparkContext._jsc.hadoopConfiguration().set(
    "io.native.lib.available", "false"
)

spark.sparkContext._jsc.hadoopConfiguration().set(
    "hadoop.native.lib", "false"
)

spark.sparkContext.setLogLevel("WARN")


# --------------------------------------------------
# 3. Define Kafka transaction structure
# --------------------------------------------------

schema = StructType([
    StructField("transaction_id", IntegerType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("amount", DoubleType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("city", StringType(), True),
    StructField("device_type", StringType(), True),
    StructField("hour", IntegerType(), True)
])


# --------------------------------------------------
# 4. Read from Kafka
# --------------------------------------------------

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "bank_transactions") \
    .option("startingOffsets", "latest") \
    .load()


# --------------------------------------------------
# 5. Convert Kafka JSON into columns
# --------------------------------------------------

transactions = df.select(
    from_json(
        col("value").cast("string"),
        schema
    ).alias("data")
).select("data.*")


# --------------------------------------------------
# 6. Process each micro-batch
# --------------------------------------------------

def process_batch(batch_df, batch_id):

    rows = batch_df.collect()

    if not rows:
        return

    print("\n========================================")
    print("Processing Batch:", batch_id)
    print("Transactions:", len(rows))
    print("========================================")

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="banking_analytics"
    )

    cursor = connection.cursor()

    for row in rows:

        transaction = {
            "transaction_id": row.transaction_id,
            "customer_id": row.customer_id,
            "amount": row.amount,
            "transaction_type": row.transaction_type,
            "city": row.city,
            "device_type": row.device_type,
            "hour": row.hour
        }

        # ------------------------------------------
        # Create ML features
        # ------------------------------------------

        transaction_type = transaction["transaction_type"].upper()

        amount = transaction["amount"]
        hour = transaction["hour"]

        features = {
            "amount": amount,
            "transaction_type": transaction_type,
            "city": transaction["city"].title(),
            "device_type": transaction["device_type"],
            "hour": hour,

            "is_night_transaction": int(0 <= hour <= 4),
            "is_high_value": int(amount > 50000),
            "is_very_high_value": int(amount > 100000),

            # Kafka transaction does not contain date,
            # so this is set to 0 for streaming.
            "is_weekend": 0,

            "is_upi": int(transaction_type == "UPI"),
            "is_card": int(transaction_type == "CARD"),
            "is_atm": int(transaction_type == "ATM"),

            "is_upi_night": int(
                transaction_type == "UPI" and 0 <= hour <= 5
            ),

            "is_large_atm": int(
                transaction_type == "ATM" and amount > 60000
            ),

            "amount_log": __import__("numpy").log1p(amount)
        }

        # Convert to DataFrame
        input_df = pd.DataFrame([features])

        # Use exactly the features expected by the model
        if feature_columns:
            input_df = input_df.reindex(
                columns=feature_columns,
                fill_value=0
            )

        # ------------------------------------------
        # Fraud probability
        # ------------------------------------------

        probability = model.predict_proba(input_df)[0][1]

        prediction = int(probability >= threshold)

        # ------------------------------------------
        # Risk level
        # ------------------------------------------

        if probability >= 0.70:
            risk = "CRITICAL"
        elif probability >= 0.50:
            risk = "HIGH"
        elif probability >= 0.30:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        # ------------------------------------------
        # Display result
        # ------------------------------------------

        print("\nTransaction ID:", transaction["transaction_id"])
        print("Amount: ₹", transaction["amount"])
        print("Customer:", transaction["customer_id"])
        print("City:", transaction["city"])
        print("Fraud Probability:", round(probability * 100, 2), "%")
        print("Risk Level:", risk)

        if prediction == 1:
            print("Prediction: FRAUDULENT TRANSACTION")
        else:
            print("Prediction: NORMAL TRANSACTION")

        # ------------------------------------------
        # Save to MySQL
        # ------------------------------------------

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
            fraud_type,
            fraud_probability,
            risk_level,
            prediction_source
        )
        VALUES
        (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            fraud_probability = VALUES(fraud_probability),
            risk_level = VALUES(risk_level),
            is_fraud = VALUES(is_fraud),
            prediction_source = VALUES(prediction_source)
        """

        values = (
            transaction["transaction_id"],
            transaction["customer_id"],
            date.today(),
            transaction["amount"],
            transaction_type,
            transaction["city"].title(),
            transaction["device_type"],
            transaction["hour"],
            prediction,
            "ML_PREDICTED" if prediction == 1 else "NORMAL",
            round(probability, 4),
            risk,
            "KAFKA_PYSPARK"
        )

        cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()

    print("\nBatch saved to MySQL successfully!")


# --------------------------------------------------
# 7. Start Structured Streaming
# --------------------------------------------------

query = transactions.writeStream \
    .foreachBatch(process_batch) \
    .outputMode("append") \
    .option(
        "checkpointLocation",
        "C:/temp/spark-checkpoint"
    ) \
    .start()


print("\n========================================")
print("PySpark Fraud Streaming Started!")
print("Kafka → PySpark → ML → MySQL")
print("Waiting for transactions...")
print("========================================")

query.awaitTermination()