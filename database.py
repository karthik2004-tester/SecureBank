import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="banking_analytics"
    )
    return connection