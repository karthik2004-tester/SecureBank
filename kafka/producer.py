from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

transaction = {
    "transaction_id": 999999,
    "customer_id": 1058,
    "amount": 75000,
    "transaction_type": "UPI",
    "city": "Bangalore",
    "device_type": "Mobile",
    "hour": 2
}

producer.send("bank_transactions", transaction)
producer.flush()

print("Transaction sent to Kafka successfully!")