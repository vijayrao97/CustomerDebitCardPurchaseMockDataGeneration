import csv
import boto3
import random
import os
from datetime import datetime
from faker import Faker

fake = Faker()

# CONFIGURATION
BUCKET_NAME = 'your AWS bucketname'
S3_PREFIX = 'transactions'  # Base prefix
AWS_REGION = 'ap-south-1'

# Initialize S3 client
s3 = boto3.client('s3', region_name=AWS_REGION)

def generate_transaction_data(date_str, num_records=100):
    data = []
    for _ in range(num_records):
        data.append([
            fake.uuid4(),
            fake.name(),
            fake.credit_card_number(card_type=None),
            random.choice(['Visa', 'MasterCard', 'RuPay']),
            random.choice(['HDFC Bank', 'ICICI Bank', 'SBI', 'Axis Bank']),
            date_str,
            round(random.uniform(100, 10000), 2)
        ])
    return data

def write_csv(data, local_file_path):
    with open(local_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'customer_id', 'name', 'debit_card_number',
            'debit_card_type', 'bank_name', 'transaction_date', 'amount_spend'
        ])
        writer.writerows(data)

def upload_to_s3(local_file_path, s3_key):
    s3.upload_file(local_file_path, BUCKET_NAME, s3_key)
    print(f"Uploaded to s3://{BUCKET_NAME}/{s3_key}")

def lambda_handler(event, context):

    sqs_client = boto3.client('sqs')
    QUEUE_URL = 'AWS link'

    # TODO implement
    # today = datetime.today().strftime('%Y-%m-%d')
    today = datetime(2025, 6, 27).strftime('%Y-%m-%d')
    local_dir = '/tmp/daily_transactions'
    os.makedirs(local_dir, exist_ok=True)

    filename = 'transactions.csv'
    local_file_path = os.path.join(local_dir, filename)
    partition_path = f"date={today}/{filename}"
    s3_key = f"{S3_PREFIX}/{partition_path}"

    data = generate_transaction_data(today, num_records=10)
    write_csv(data, local_file_path)
    upload_to_s3(local_file_path, s3_key)