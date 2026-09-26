SecureBank – Real-Time Banking Transaction Analytics & Fraud Risk Detection

SecureBank is an end-to-end banking transaction analytics and fraud-risk detection system designed to demonstrate batch data processing, machine learning-based fraud prediction, and real-time transaction streaming.

The project combines Python, Pandas, MySQL, Scikit-learn, Apache Kafka, PySpark Structured Streaming, SQL, and Streamlit into a single workflow.

🚀 Features
Process and clean 20,000+ banking transactions
Perform ETL using Python and Pandas
Store transaction data in MySQL
Perform SQL-based transaction and fraud analytics
Engineer transaction-level ML features
Detect potential fraudulent transactions using Random Forest
Generate fraud probability and risk levels
Process new transactions through Kafka + PySpark Structured Streaming
Perform real-time ML inference on streaming transactions
Store streaming predictions in MySQL
Interactive Streamlit dashboard
Payment risk assessment
Live fraud monitoring
🏗️ System Architecture
Batch Workflow
transactions.csv
       ↓
Python + Pandas ETL
       ↓
Data Cleaning & Transformation
       ↓
MySQL
       ↓
SQL Analytics
       ↓
Machine Learning
       ↓
Streamlit Dashboard
Real-Time Workflow
New Transaction
       ↓
Kafka Producer
       ↓
Kafka Topic
       ↓
PySpark Structured Streaming
       ↓
Feature Engineering
       ↓
Random Forest Model
       ↓
Fraud Probability
       ↓
Risk Level
       ↓
MySQL
       ↓
Streamlit Live Monitoring
🤖 Machine Learning

The project uses a Random Forest Classifier for fraud-risk prediction.

Feature Engineering

The model uses engineered features including:

Night transaction indicator
High-value transaction indicator
Very-high-value transaction indicator
Weekend indicator
UPI/Card/ATM indicators
UPI night transaction indicator
Large ATM transaction indicator
Log-transformed transaction amount
Dataset

The project uses a synthetic banking transaction dataset containing:

20,000 transactions
585 fraudulent transactions
Approximately 2.92% fraud rate

Because the dataset is imbalanced, model evaluation considers precision, recall, F1-score, ROC-AUC, and PR-AUC, rather than relying only on accuracy.

⚡ Real-Time Processing

Apache Kafka is used as the transaction event ingestion layer.

A transaction is published to the:

bank_transactions

Kafka topic.

PySpark Structured Streaming continuously consumes these events, performs feature engineering, and passes the processed features to the trained Random Forest model.

The model performs inference using the already-trained model rather than retraining for every transaction.

The resulting:

Fraud probability
Fraud prediction
Risk level

are stored in MySQL and displayed through the Streamlit live monitoring interface.

🔐 Risk Classification

The system converts model probabilities into four risk levels:

Fraud Probability	Risk Level
< 0.30	LOW
0.30 – < 0.50	MEDIUM
0.50 – < 0.70	HIGH
≥ 0.70	CRITICAL

The ML classification threshold is configured separately and was tuned using validation data.

🛠️ Technology Stack
Category	Technologies
Programming	Python, SQL
Data Processing	Pandas, NumPy
Machine Learning	Scikit-learn, Random Forest
Streaming	Apache Kafka, PySpark Structured Streaming
Database	MySQL
Frontend	Streamlit
Model Persistence	Joblib
Configuration	python-dotenv
Development	Git, GitHub, VS Code
📁 Project Structure
SecureBank/
│
├── data/
│   └── transactions.csv
│
├── kafka/
│   ├── producer.py
│   └── consumer.py
│
├── model/
│   ├── fraud_model.pkl
│   ├── model_config.pkl
│   └── encoders.pkl
│
├── app.py
├── database.py
├── etl.py
├── generate_data.py
├── predict.py
├── streaming.py
├── train_model.py
├── analytics.sql
├── test_connection.py
├── requirements.txt
└── .gitignore
⚙️ Setup
1. Clone the repository
git clone https://github.com/karthik2004-tester/SecureBank.git
cd SecureBank
2. Install dependencies
pip install -r requirements.txt
3. Configure environment variables

Create a .env file:

MYSQL_PASSWORD=your_mysql_password

Do not commit .env to GitHub.

4. Configure MySQL

Create the database:

CREATE DATABASE banking_analytics;

Create the required transactions table using the SQL schema provided in the project.

5. Run ETL
python etl.py
6. Train the model
python train_model.py
7. Start Kafka

On Windows:

cd "C:\kafka\kafka_2.13-4.3.0"
.\bin\windows\kafka-server-start.bat .\config\server.properties
8. Start PySpark streaming
python streaming.py
9. Start Streamlit
python -m streamlit run app.py
10. Send a test transaction
cd kafka
python producer.py

The transaction will flow through:

Kafka
 → PySpark
 → Random Forest
 → MySQL
 → Streamlit
📊 Dashboard

The Streamlit application provides:

Home – project overview and key information
Check a Payment – interactively evaluate a transaction
Transactions – transaction-level analytics
Security – fraud and risk insights
Live Fraud Monitoring – monitor predictions coming through the Kafka/PySpark pipeline
📌 Important Note

This project uses synthetic banking transaction data and is intended as an academic/portfolio prototype demonstrating an end-to-end fraud analytics architecture.

The machine-learning results should therefore not be interpreted as production banking fraud-detection performance. A production system would require real historical transaction data, confirmed fraud labels, stronger monitoring, model retraining strategies, security controls, and scalable infrastructure.

🔮 Future Enhancements
Automated periodic model retraining
Model drift monitoring
More advanced fraud detection models
Kafka partitioning and scalable Spark deployment
Alert/notification system for critical transactions
Role-based dashboard access
Cloud deployment
Production-grade monitoring and logging
👨‍💻 Author

Karthikeya R Hegde

MCA – BMS College of Engineering, Bengaluru

GitHub: karthik2004-tester
