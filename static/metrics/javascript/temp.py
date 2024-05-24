import pymysql
import random
from datetime import datetime, timedelta

# Connect to the SQLite database
conn  = pymysql.connect(host="database-1.chu04k6u0syf.us-east-1.rds.amazonaws.com", user='admin', password='admin1234', database='exercises')
cursor = conn.cursor()

# Insert random data into the table
for _ in range(10):  # Inserting 10 rows for demonstration
    timestamp = (datetime.now() - timedelta(days=random.randint(1, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    user_id = "7"
    age = random.randint(18, 80)
    gender = random.randint(0, 1)  # Assuming 0 for male, 1 for female
    height = random.randint(150, 200)  # Height in cm
    weight = random.randint(50, 100)  # Weight in kg
    heartrate = random.uniform(60, 200)  # Random heartrate between 60 and 200
    steps = random.randint(1000, 20000)  # Random steps count
    exercise_id = random.randint(50, 900)  # Random exercise_id

    cursor.execute(f'''INSERT INTO fitness_data (timestamp, user_id, Age, gender, height, weight, heartrate, steps, exercise_id)
                      VALUES ("{timestamp}", {user_id}, {age}, {gender}, {height}, {weight}, {heartrate}, {steps}, {exercise_id})''')

# Commit changes and close connection
conn.commit()
conn.close()