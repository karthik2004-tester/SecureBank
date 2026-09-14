from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "bank_transactions",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    group_id="bank-fraud-group",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("Waiting for transactions...")

for message in consumer:
    transaction = message.value

    print("\nTransaction received:")
    print(transaction)