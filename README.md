# SecureBank – Real-Time Banking Transaction Analytics & Fraud Risk Detection

SecureBank is an end-to-end banking transaction analytics and fraud-risk detection system that combines **data processing, SQL analytics, machine learning, and real-time transaction streaming**.

The system processes banking transactions, performs data cleaning and transformation, analyzes transaction patterns, predicts fraud probability using a **Random Forest classifier**, and supports real-time transaction processing using **Apache Kafka and PySpark Structured Streaming**.

The project also provides an interactive **Streamlit dashboard** for payment risk assessment, transaction analytics, and live fraud monitoring.

---

## 🚀 Key Features

- Process and analyze **20,000+ banking transactions**
- Perform ETL using **Python and Pandas**
- Store and query transaction data using **MySQL**
- Perform SQL-based fraud and transaction analytics
- Engineer transaction-level features for machine learning
- Detect potential fraudulent transactions using **Random Forest**
- Generate fraud probability for new transactions
- Classify transactions into **LOW, MEDIUM, HIGH, and CRITICAL** risk levels
- Ingest new transactions using **Apache Kafka**
- Process streaming transactions using **PySpark Structured Streaming**
- Perform real-time ML inference on incoming transactions
- Store streaming predictions and risk information in MySQL
- Provide an interactive **Streamlit dashboard**
- Monitor streaming predictions through a **Live Fraud Monitoring** page

---

# 🏗️ System Architecture

SecureBank consists of two main processing workflows:

## 1. Batch Data Processing Workflow

```text
Transaction Dataset
        ↓
Python + Pandas
        ↓
ETL
        ↓
Data Cleaning & Transformation
        ↓
MySQL
        ↓
SQL Analytics
        ↓
Feature Engineering
        ↓
Random Forest Model
        ↓
Model Evaluation
        ↓
Streamlit Dashboard

Real-Time Transaction Processing Workflow
New Transaction
        ↓
Kafka Producer
        ↓
Kafka Topic
bank_transactions
        ↓
PySpark Structured Streaming
        ↓
Transaction Parsing
        ↓
Feature Engineering
        ↓
Trained Random Forest Model
        ↓
Fraud Probability
        ↓
Risk Level
        ↓
MySQL
        ↓
Streamlit Live Fraud Monitoring

The real-time workflow performs inference using the already-trained model. The model is not retrained for every incoming transaction.

📊 Dataset

The project uses a synthetic banking transaction dataset containing:

20,000 transactions
585 fraudulent transactions
Approximately 2.92% fraud cases

Each transaction contains information such as:

Transaction ID
Customer ID
Transaction date
Transaction amount
Transaction type
City
Device type
Transaction hour
Fraud label
Fraud type

The target variable is:

is_fraud

where:

0 → Normal transaction
1 → Fraudulent transaction

Because fraud represents only a small percentage of the dataset, the project treats fraud detection as an imbalanced classification problem.

🔄 ETL Pipeline

The project uses Python and Pandas to implement an ETL pipeline.

Extract

Transaction data is read from:

data/transactions.csv
Transform

The pipeline performs operations such as:

Removing duplicate transaction IDs
Handling missing values
Normalizing transaction information
Converting transaction dates
Validating transaction amounts
Preparing data for database storage and analysis
Load

The cleaned transaction data is loaded into the MySQL database:

banking_analytics

The main table is:

transactions
🤖 Machine Learning

SecureBank uses a Random Forest Classifier for fraud-risk prediction.

Feature Engineering

The following transaction features are generated for the model:

is_night_transaction
is_high_value
is_very_high_value
is_weekend
is_upi
is_card
is_atm
is_upi_night
is_large_atm
amount_log

These features capture transaction characteristics such as transaction timing, amount, payment method, and potentially suspicious combinations of attributes.

🧠 Model Training

The dataset is divided into:

Training Set   → 12,000
Validation Set → 4,000
Test Set       → 4,000

A stratified split is used to maintain the class distribution across the datasets.

The Random Forest model is trained on the training set and evaluated using the validation and test sets.

The classification threshold is tuned using the validation data, with 0.60 selected based on F1-score.

📈 Model Evaluation

The latest test results are:

Metric	Result
Accuracy	97.9%
Precision	97.14%
Recall	29.06%
F1-Score	44.74%
ROC-AUC	64.85%
PR-AUC	32.96%

Because the dataset is highly imbalanced, accuracy is not considered sufficient on its own. Precision, recall, F1-score, ROC-AUC, and PR-AUC are also considered when evaluating the model.

Note: The dataset is synthetic, so these metrics represent the performance of this project prototype and should not be interpreted as production banking fraud-detection performance.

⚠️ Risk Classification

The system converts fraud probabilities into business-friendly risk levels:

Fraud Probability	Risk Level
< 0.30	LOW
0.30 – < 0.50	MEDIUM
0.50 – < 0.70	HIGH
≥ 0.70	CRITICAL

For example:

Fraud Probability: 95.51%
Risk Level: CRITICAL

The ML prediction threshold and the risk-level boundaries serve different purposes:

Prediction threshold: determines the binary fraud prediction.
Risk level: communicates the probability as a business-friendly category.
⚡ Real-Time Streaming

The real-time component uses:

Apache Kafka
PySpark Structured Streaming
Random Forest
MySQL
Streamlit
Step 1 – Transaction Producer

A new transaction is generated by the Kafka producer.

kafka/producer.py

The transaction is published to:

bank_transactions

Kafka topic.

Step 2 – Kafka

Kafka acts as the transaction event ingestion layer.

It allows transaction events to be published and consumed independently.

Producer
   ↓
Kafka Topic
   ↓
Consumer / Streaming Application
Step 3 – PySpark Streaming

PySpark Structured Streaming continuously consumes events from Kafka.

The streaming application:

Reads the Kafka event
Parses the transaction data
Performs feature engineering
Loads the trained ML model
Generates fraud probability
Determines the risk level
Stores the prediction in MySQL
Step 4 – Machine Learning Inference

The trained Random Forest model is used to predict the incoming transaction.

For example:

Transaction
   ↓
Feature Engineering
   ↓
Random Forest
   ↓
Fraud Probability = 95.51%
   ↓
Risk Level = CRITICAL

The model performs inference, not training, for each incoming transaction.

Step 5 – MySQL

The prediction is stored in MySQL along with information such as:

fraud_probability
risk_level
is_fraud
prediction_source

Streaming predictions are identified using:

prediction_source = KAFKA_PYSPARK
Step 6 – Live Monitoring

The Streamlit dashboard reads the processed predictions from MySQL.

The Live Fraud Monitoring page displays transactions processed through the streaming pipeline.

Therefore, the complete live flow is:

New Transaction
      ↓
Kafka
      ↓
PySpark
      ↓
Random Forest
      ↓
MySQL
      ↓
Streamlit
      ↓
Live Fraud Monitoring
🖥️ Streamlit Dashboard

The application provides several sections:

Home

Provides an overview of the SecureBank system.

Check a Payment

Allows a user to enter transaction details and receive:

Fraud probability
Fraud prediction
Risk level
Payment information
Transactions

Provides transaction-level information and analytics.

Security

Provides fraud-related insights and security information.

Live Fraud Monitoring

Displays predictions generated through the Kafka + PySpark streaming pipeline.

🗄️ SQL Analytics

MySQL is used not only for storage but also for transaction analytics.

Example analysis:

SELECT
    city,
    COUNT(*) AS transactions,
    SUM(is_fraud) AS fraud_cases
FROM transactions
GROUP BY city
ORDER BY fraud_cases DESC;

This allows the system to analyze transaction volumes and fraud cases across different cities.

🛠️ Technology Stack
Category	Technologies
Programming	Python, SQL
Data Processing	Pandas, NumPy
Machine Learning	Scikit-learn, Random Forest
Streaming	Apache Kafka, PySpark Structured Streaming
Database	MySQL
Frontend / Dashboard	Streamlit
Model Persistence	Joblib
Configuration	python-dotenv
Development Tools	Git, GitHub, VS Code
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
⚙️ Installation & Setup
1. Clone the Repository
git clone https://github.com/karthik2004-tester/SecureBank.git
cd SecureBank
2. Install Python Dependencies
pip install -r requirements.txt
3. Configure MySQL

Create the database:

CREATE DATABASE banking_analytics;

Create the required transactions table using the SQL schema included in the project.

4. Configure Environment Variables

Create a .env file in the project root:

MYSQL_PASSWORD=your_mysql_password

The .env file should not be committed to GitHub.

▶️ Running the Project
Step 1 – Load the Dataset

Run the ETL pipeline:

python etl.py

This cleans the transaction dataset and loads it into MySQL.

Step 2 – Train the Model
python train_model.py

The trained model and configuration files are saved inside:

model/
Step 3 – Start Kafka

On Windows:

cd "C:\kafka\kafka_2.13-4.3.0"

.\bin\windows\kafka-server-start.bat .\config\server.properties
Step 4 – Start PySpark Streaming

From the project directory:

python streaming.py

The application starts listening for transactions from Kafka.

Step 5 – Start Streamlit
python -m streamlit run app.py

The SecureBank dashboard will start.

Step 6 – Send a Test Transaction

Open another terminal:

cd kafka
python producer.py

The transaction is then processed through:

Kafka
  ↓
PySpark
  ↓
Random Forest
  ↓
MySQL
  ↓
Streamlit
🔐 Security & Configuration

Sensitive database credentials are loaded using environment variables through python-dotenv.

The .env file is excluded from version control using .gitignore.

No database password should be stored directly in the source code or committed to GitHub.

🔮 Future Enhancements

Possible future improvements include:

Automated periodic model retraining
Model drift monitoring
Advanced fraud detection algorithms
Automated fraud alerts and notifications
Kafka partitioning for higher throughput
Distributed Spark deployment
Cloud deployment
Role-based dashboard access
Production-grade monitoring and logging
Integration with real historical banking fraud data
⚠️ Project Scope

SecureBank is an academic/portfolio prototype demonstrating an end-to-end architecture for banking transaction analytics and fraud-risk detection.

The transaction dataset is synthetic. Therefore, the model metrics should not be interpreted as production banking fraud-detection performance.

A production implementation would require real historical transaction data, verified fraud labels, stronger security controls, monitoring, model governance, scalability, and appropriate compliance measures.

👨‍💻 Author

Karthikeya R Hegde

MCA – BMS College of Engineering, Bengaluru

GitHub: karthik2004-tester
