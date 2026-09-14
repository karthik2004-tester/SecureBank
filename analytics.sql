SELECT COUNT(*) AS total_transactions FROM transactions;
SELECT SUM(amount) AS total_amount FROM transactions;
SELECT AVG(amount) AS average_amount FROM transactions;

SELECT
    is_fraud,
    COUNT(*) AS total
FROM transactions
GROUP BY is_fraud;

SELECT
    ROUND(
        SUM(is_fraud) * 100.0 / COUNT(*),
        2
    ) AS fraud_percentage
FROM transactions;

SELECT
    transaction_type,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_amount
FROM transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;

SELECT
    location,
    COUNT(*) AS fraud_transactions
FROM transactions
WHERE is_fraud = 1
GROUP BY location
ORDER BY fraud_transactions DESC;

SELECT
    customer_id,
    SUM(amount) AS total_amount
FROM transactions
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 10;

SELECT *
FROM transactions
WHERE amount > 75000
ORDER BY amount DESC;

SELECT *
FROM transactions
WHERE is_fraud = 1
AND hour BETWEEN 0 AND 5
ORDER BY amount DESC;

