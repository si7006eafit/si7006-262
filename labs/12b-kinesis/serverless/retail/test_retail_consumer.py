import base64
import json
from decimal import Decimal
from types import SimpleNamespace

import retail_consumer as consumer

LINE = {
    'InvoiceNo': 'C541433',
    'StockCode': '23166',
    'Description': 'MEDIUM CERAMIC TOP STORAGE JAR',
    'Quantity': '-74215',
    'InvoiceDate': '1/18/2011 10:17',
    'UnitPrice': '1.04',
    'CustomerID': '12346',
    'Country': 'United Kingdom',
}


def kinesis_record(line):
    data = (json.dumps(line) + '\n').encode('utf-8')
    return {
        'kinesis': {
            'partitionKey': '123456789',
            'data': base64.b64encode(data).decode('ascii'),
        },
        'eventSource': 'aws:kinesis',
    }


def fake_table():
    items = []
    return SimpleNamespace(
        items=items, put_item=lambda **kwargs: items.append(kwargs['Item']))


def test_the_item_converts_the_text_of_the_agent_to_numbers():
    item = consumer.to_item(kinesis_record(LINE))
    assert item['customer_id'] == 12346
    assert item['line_id'] == 'C541433-23166'
    assert item['quantity'] == -74215
    assert item['unit_price'] == Decimal('1.04')
    assert item['country'] == 'United Kingdom'


def test_the_handler_writes_one_item_per_record(monkeypatch):
    table = fake_table()
    monkeypatch.setattr(consumer, 'get_table', lambda: table)
    other = {
        **LINE, 'StockCode': '22755'
    }
    result = consumer.handler(
        {
            'Records': [kinesis_record(LINE),
                        kinesis_record(other)]
        }, None)
    assert result == {
        'written': 2
    }
    assert [item['line_id']
            for item in table.items] == ['C541433-23166', 'C541433-22755']
