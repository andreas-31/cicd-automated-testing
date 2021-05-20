#!/usr/bin/env python3
#import requests
#import hashlib
#import hmac
#import base64
import logging
#import urllib3
import json
import csv
#import datetime
from LogAnalyticsDataCollector import post_data, build_signature
from sys import exit

azure_analytics_workspace_json_file = 'azure_analytics_workspace.json'
with open(azure_analytics_workspace_json_file, "r") as jsonfile:
    data = json.load(jsonfile)
    print("Read successful")
print(data)

azure_log_customer_id = data['azure_log_customer_id']
azure_log_shared_key = data['azure_log_shared_key']

# read logs from CSV logfile and write it to Azure Monitor
# Log Analytics table.
csv_logfile = 'seleniumLogfile.csv'
table_name = 'seleniumLogsMonitor'
with open('seleniumLogfile.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        #print(row)

        data = {
            "time" : row[0],
            "category" : row[1],
            "message" : row[2]
        }
        data_json = json.dumps(data)
        print(f'data_json = {data_json}')

        try:
            post_data(azure_log_customer_id, azure_log_shared_key, data_json, table_name)
            msg = "Sent log entry successfully to Azure Monitor"
            print(msg)
            logging.info(msg)
        except Exception as error:
            logging.error("Unable to send data to Azure Log")
            logging.error(error)
