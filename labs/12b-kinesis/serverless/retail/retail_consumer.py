"""Lambda function that writes each order line of a Kinesis stream to DynamoDB.

The Kinesis Agent turns each log line into JSON with the names of the fields and
every value as text. The table has the customer as its partition key and the
invoice and the product as its sort key, so a line that arrives twice replaces
the item it had already written.
"""
import base64
import json
import os
from decimal import Decimal

import boto3


def get_table():
    return boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])


def to_item(record):
    """Return the DynamoDB item of a Kinesis record of the Lambda event."""
    line = json.loads(base64.b64decode(record['kinesis']['data']))
    return {
        'customer_id': int(line['CustomerID']),
        'line_id': f"{line['InvoiceNo']}-{line['StockCode']}",
        'invoice_no': line['InvoiceNo'],
        'stock_code': line['StockCode'],
        'description': line['Description'],
        'quantity': int(line['Quantity']),
        'unit_price': Decimal(line['UnitPrice']),
        'invoice_date': line['InvoiceDate'],
        'country': line['Country'],
    }


def handler(event, context):
    del context
    table = get_table()
    for record in event['Records']:
        table.put_item(Item=to_item(record))
    result = {
        'written': len(event['Records'])
    }
    print(json.dumps(result))
    return result
