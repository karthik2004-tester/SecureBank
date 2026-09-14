SecureBank – Real-Time Banking Transaction Analytics & Fraud Risk Detection

SecureBank is an end-to-end banking transaction analytics and fraud-risk detection system that combines data engineering, machine learning, real-time streaming, SQL analytics, and an interactive banking dashboard.

The system supports both batch transaction processing and real-time transaction monitoring. It analyzes transaction behavior, generates fraud probability and risk levels, stores prediction results in MySQL, and presents actionable insights through a Streamlit-based banking interface.

## 🚀 Key Features

- Batch processing of 20,000+ banking transactions
- Data cleaning and transformation using Python and Pandas
- MySQL database for transaction storage and analytics
- Random Forest-based fraud-risk prediction
- Probability-based risk classification
- Apache Kafka for real-time transaction streaming
- PySpark Structured Streaming for real-time processing
- Real-time ML prediction and database persistence
- Interactive Streamlit banking dashboard
- Payment risk assessment
- Transaction analytics
- Live fraud monitoring
- City-wise fraud analytics
- Risk levels: LOW, MEDIUM, HIGH, and CRITICAL

## 🏗️ System Architecture

```text
Customer Input
      ↓
SecureBank Streamlit UI
      ↓
Kafka Producer
      ↓
Kafka Topic: bank_transactions
      ↓
PySpark Structured Streaming
      ↓
Feature Engineering
      ↓
Random Forest ML Model
      ↓
Fraud Probability + Risk Level
      ↓
MySQL Database
      ↓
SecureBank Analytics & Live Fraud Monitoring

🔄 Data Processing Pipelines
Batch Pipeline
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
Streamlit Dashboard
Real-Time Pipeline
Customer Transaction
      ↓
Kafka Producer
      ↓
Kafka Topic
      ↓
PySpark Structured Streaming
      ↓
Feature Engineering
      ↓
Random Forest ML Model
      ↓
Fraud Probability
      ↓
Risk Classification
      ↓
MySQL
      ↓
Live Fraud Monitoring
🧠 Machine Learning

SecureBank uses a Random Forest Classifier to estimate the probability that a transaction is fraudulent.

Engineered Features

The model uses transaction-derived features including:

Night transaction indicator
High-value transaction indicator
Very-high-value transaction indicator
Weekend indicator
UPI indicator
Card indicator
ATM indicator
UPI + night transaction indicator
Large ATM transaction indicator
Log-transformed transaction amount
Risk Classification
Fraud Probability	Risk Level
< 0.30	LOW
0.30 – < 0.50	MEDIUM
0.50 – < 0.70	HIGH
≥ 0.70	CRITICAL

The ML fraud classification threshold is 0.60.

📊 Model Evaluation

The dataset contains 20,000 synthetically generated banking transactions with rule-based fraud labels.

Metric	Score
Accuracy	97.9%
Precision	97.14%
Recall	29.06%
F1 Score	44.74%
ROC-AUC	64.85%
PR-AUC	32.96%

Note: The dataset is synthetic and rule-generated, so these results should not be interpreted as real-world banking fraud detection performance. The relatively low recall also indicates that the model does not detect all fraudulent cases.

🗄️ Database

The project uses MySQL with the database:

banking_analytics

The main transactions table stores:

Transaction ID
Customer ID
Transaction date
Transaction amount
Transaction type
City
Device type
Transaction hour
Fraud status
Fraud type
Fraud probability
Risk level
Prediction source

The database supports both transaction storage and analytical SQL queries.

⚡ Real-Time Streaming

Apache Kafka is used as the messaging layer for real-time transactions.

Kafka topic:

bank_transactions

PySpark Structured Streaming consumes transactions from Kafka and performs:

Transaction parsing
Data transformation
Feature engineering
ML prediction
Fraud probability calculation
Risk classification
MySQL persistence

Streaming prediction results are stored with the prediction source:

KAFKA_PYSPARK
🖥️ Streamlit Dashboard

The SecureBank dashboard provides the following modules:

🏦 Home

Provides an overview of the SecureBank transaction monitoring system.

💳 Check a Payment

Allows a user to enter transaction details and receive:

Fraud probability
Risk level
Transaction assessment
Security decision
📊 Transactions

Provides transaction information and analytics for banking transactions.

🔐 Security

Provides security-focused fraud-risk information.

🚨 Live Fraud Monitoring

Displays transactions processed through the real-time Kafka and PySpark pipeline and highlights their fraud-risk levels.

📁 Project Structure
Banking_Fraud_Analytics/
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
│   ├── encoders.pkl
│   └── model_config.pkl
│
├── analytics.sql
├── app.py
├── database.py
├── etl.py
├── generate_data.py
├── predict.py
├── requirements.txt
├── streaming.py
├── test_connection.py
├── train_model.py
├── .gitignore
└── README.md
🛠️ Technology Stack
Programming & Data
Python
Pandas
NumPy
Machine Learning
Scikit-learn
Random Forest
Joblib
Database
MySQL
SQL
mysql-connector-python
Streaming
Apache Kafka
PySpark
Spark Structured Streaming
kafka-python
Frontend
Streamlit
Configuration
python-dotenv
⚙️ Installation

Clone the repository:

git clone https://github.com/karthik2004-tester/SecureBank.git

Navigate to the project:

cd SecureBank

Install the required Python packages:

pip install -r requirements.txt
🔐 Environment Variables

Create a .env file in the project root:

MYSQL_PASSWORD=your_mysql_password

The .env file is excluded from Git using .gitignore.

Never commit your actual database password to GitHub.

🗄️ Database Setup

Create the database in MySQL:

CREATE DATABASE banking_analytics;

Use the SQL statements in:

analytics.sql

to create and configure the required transaction table.

▶️ Running the Application
1. Start Kafka

From the Kafka installation directory:

cd "C:\kafka\kafka_2.13-4.3.0"
.\bin\windows\kafka-server-start.bat .\config\server.properties

Keep the Kafka terminal running.

2. Start PySpark Streaming

Open another terminal:

cd "C:\Users\Karthik Hegde\Desktop\Banking_Fraud_Analytics"
python streaming.py

Keep the streaming process running.

3. Start Streamlit

Open another terminal:

cd "C:\Users\Karthik Hegde\Desktop\Banking_Fraud_Analytics"
python -m streamlit run app.py

The SecureBank dashboard will start locally.

🧪 Testing Real-Time Transactions

The Kafka producer can be used to send a transaction to the Kafka topic:

cd "C:\Users\Karthik Hegde\Desktop\Banking_Fraud_Analytics\kafka"
python producer.py

The transaction is consumed by PySpark, processed by the ML model, assigned a risk level, and stored in MySQL.

📈 Example Risk Assessment

Example transaction:

Transaction Amount : ₹75,000
Transaction Type   : UPI
City               : Bangalore
Device             : Mobile
Transaction Hour   : 2 AM

The system analyzes transaction characteristics, generates a fraud probability, and assigns an appropriate risk level.

🎯 Project Objective

The objective of SecureBank is to demonstrate how a banking organization can combine:

Data Engineering
       +
SQL Analytics
       +
Machine Learning
       +
Real-Time Streaming
       +
Risk Monitoring

into an end-to-end transaction monitoring system.

💡 Business Value

SecureBank demonstrates a technical approach for processing banking transactions and identifying potentially suspicious activity.

The system:

Processes and cleans transaction data systematically.
Stores transactions for analytical querying.
Uses machine learning for probability-based fraud-risk scoring.
Uses Kafka for real-time transaction ingestion.
Uses PySpark for streaming data processing.
Stores prediction results in MySQL.
Provides a dashboard for payment assessment and fraud monitoring.

This architecture can serve as a foundation for more advanced fraud detection systems using real-world banking data and richer behavioral features.

⚠️ Limitations

This project is an academic and portfolio implementation.

Current limitations include:

The transaction dataset is synthetic.
Fraud labels are generated using predefined rules.
The model has limited fraud recall.
The system is not connected to a real banking network.
Production-grade authentication and authorization are not implemented.
Real-world fraud detection would require richer customer behavioral and historical features.
🚀 Future Enhancements
Real banking transaction datasets
Customer behavioral profiling
Transaction velocity analysis
Geographic anomaly detection
Device fingerprinting
Advanced anomaly detection
XGBoost / LightGBM model comparison
Model monitoring and drift detection
Authentication and role-based access
Cloud deployment
Alert notifications
Advanced fraud investigation workflows
👨‍💻 Author

Karthikeya R Hegde

MCA – BMS College of Engineering

GitHub: https://github.com/karthik2004-tester

📄 License

This project is intended for educational, academic, and portfolio purposes.
