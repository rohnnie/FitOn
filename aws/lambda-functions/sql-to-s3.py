import pymysql
import boto3
import csv
import os
from time import gmtime, strftime
from datetime import datetime, timedelta

# RDS MySQL database configuration
rds_host = "database-1.chu04k6u0syf.us-east-1.rds.amazonaws.com"
db_user = "admin"
db_password = "admin1234"
db_name = "exercises"

# S3 bucket configuration
s3_bucket = "exercises-dataset"
s3_client = boto3.client('s3')
s3_key_meta = 'last_modified.txt'

conn = pymysql.connect(host=rds_host, user=db_user, password=db_password, database=db_name, connect_timeout=60)



def lambda_handler(event, context):
        
    
    # Get last timestamp when data was dumped to S3
    print("GETTING LAST TIMESTAMP ... ")
    last_dump_timestamp = get_last_dump_timestamp(s3_bucket, s3_key_meta)
    # last_dump_timestamp = '2024-05-11 21:32:00'
    
    # # Connect to RDS MySQL database
    print("CONNECTING TO DB ..... ")
    cursor = conn.cursor()
    print("CONNECTED TO DB")
    # # Execute SELECT query to fetch updated or inserted data since last timestamp
    print("LAST MODIFIED TIME .....")
    print(last_dump_timestamp)
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    thirty_days_ago_str = thirty_days_ago.strftime('%Y-%m-%d')
    
    query = f"SELECT * FROM fitness_data WHERE timestamp >= '{thirty_days_ago_str}';"
    cursor.execute(query)
    data = cursor.fetchall()
    
    print(data)
    
    # # Write data to a CSV file
    csv_file_path = f"/tmp/exercise_data.csv"  # Lambda's /tmp directory
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([i[0] for i in cursor.description])  # Write column headers
        csv_writer.writerows(data)
    
    # # Upload CSV file to S3
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    s3_key = f"exercise_data.csv"
    s3_client.upload_file(csv_file_path, s3_bucket, s3_key)
    s3_client.put_object(Bucket = s3_bucket, Key = s3_key_meta, Body = current_time.encode())
    
    # # Clean up temporary file
    os.remove(csv_file_path)
    
    return {
        'statusCode': 200,
        'body': 'Data dumped to S3 successfully!'
    }

def get_last_dump_timestamp(s3_bucket, s3_key):
    try:
        print("GETTING RESPONSE FROM S3 ... ")
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key_meta)
        last_modified = response['Body'].read()
        print("LAST MODIFIED ... ")
        return BytesIO(last_modified)
    except Exception as e:
        print(f"Error retrieving last dump timestamp: {e}")
        return '2024-05-11 21:32:00'  # Default timestamp if not found

