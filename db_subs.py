import mysql.connector
import os
import requests
import json

DB_USER = os.environ["db_user"]
DB_PASSWORD = os.environ["db_password"]
DB_HOST = os.environ["db_host"]
DB_PORT = os.environ["db_port"]
DB_DB = os.environ["db_database"]
WEBHOOK_URL = os.environ["slack_webhook"]

db_config = {
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT,
    'database': DB_DB
}

query = (
    "SELECT Email, EmailPassword, CreateDate FROM Accounts WHERE DATE(CreateDate) = DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND `Status` IN (1,2,5,9,15,20,21)"
)

connection = None
cursor = None

print(os.environ)

try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    
    with open('D:/sub_end.txt', 'w') as file:
        for row in results:
            email, password, create_date = row
            file.write(f"{email}:{password} - {create_date}\n")
    
    with open("D:/sub_end.txt", "r") as f:
        file_contents = f.read()

    if file_contents.strip():
        message = f":police: Ending subscriptions detected! :police:\n{file_contents}"
    else:
        message = ":white_check_mark: All subscriptions is up to date! :white_check_mark:"

    headers = {"Content-type": "application/json"}
    payload = {"text": message}

    response = requests.post(f"{WEBHOOK_URL}", data=json.dumps(payload), headers=headers)

    if response.status_code != 200:
        raise ValueError(
            f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}"
        )
    else:
        print("Message sent successfully!")

except mysql.connector.Error as err:
    print("Query error:", err)

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()
