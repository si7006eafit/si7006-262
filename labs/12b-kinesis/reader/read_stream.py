"""Read the records of every shard of a Kinesis stream and print them.

It is a consumer of its own, apart from the Lambda function: it asks for an iterator
of each shard and reads with GetRecords once per second. It starts at the newest
record (LATEST), or at the oldest one that the stream keeps with --from-start
(TRIM_HORIZON). Stop it with Ctrl+C.
"""
import argparse
import json
import time

import boto3

STREAM = 'big-data-labs-retail-orders'


def shard_iterators(client, stream, iterator_type):
    shards = client.list_shards(StreamName=stream)['Shards']
    return {
        shard['ShardId']:
            client.get_shard_iterator(StreamName=stream,
                                      ShardId=shard['ShardId'],
                                      ShardIteratorType=iterator_type)
            ['ShardIterator']
        for shard in shards
    }


def describe(record):
    line = json.loads(record['Data'])
    return (
        f"{record['SequenceNumber'][-6:]}  {line['InvoiceNo']:>8}  "
        f"{line['CustomerID']:>6}  {line['Quantity']:>6} x {line['UnitPrice']:<6}  "
        f"{line['Description']}")


def main():
    parser = argparse.ArgumentParser(description='Read a Kinesis stream.')
    parser.add_argument('--stream',
                        default=STREAM,
                        help='(default: %(default)s)')
    parser.add_argument('--from-start',
                        action='store_true',
                        help='start at the oldest record that the stream keeps')
    parser.add_argument(
        '--seconds',
        type=int,
        default=0,
        help='stop after these seconds (default: run until Ctrl+C)')
    args = parser.parse_args()

    client = boto3.client('kinesis')
    iterator_type = 'TRIM_HORIZON' if args.from_start else 'LATEST'
    iterators = shard_iterators(client, args.stream, iterator_type)
    print(
        f'Reading {len(iterators)} shard(s) of {args.stream} from {iterator_type}'
    )
    total = 0
    started = time.monotonic()
    try:
        while not args.seconds or time.monotonic() - started < args.seconds:
            for shard_id, iterator in iterators.items():
                response = client.get_records(ShardIterator=iterator,
                                              Limit=1000)
                iterators[shard_id] = response['NextShardIterator']
                for record in response['Records']:
                    print(describe(record))
                total += len(response['Records'])
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    print(f'Read {total} records')


if __name__ == '__main__':
    main()
