"""Write the order lines of an online store as log files, the way an application server would.

Each run writes one file, named after the time of the run, in --output (/var/log/retail by
default), with the next --lines lines of the data set, one order line per log line, its
fields separated by tabs and without a header. The position of the last line written is kept
in --state, so the next run continues where this one stopped, and starts again from the
first line at the end of the data set.

    sudo python3 generate_logs.py --lines 1000
"""
import argparse
import csv
import gzip
import time
from pathlib import Path

HERE = Path(__file__).parent
FIELDS = [
    'InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate',
    'UnitPrice', 'CustomerID', 'Country'
]


def read_rows(data):
    """Return the order lines of the data set, without its header."""
    with gzip.open(data, 'rt', encoding='utf-8', newline='') as source:
        reader = csv.reader(source)
        header = next(reader)
        if header != FIELDS:
            raise ValueError(f'unexpected columns: {header}')
        return list(reader)


def to_log_line(row):
    """One order line as a log line: the fields, trimmed, separated by tabs."""
    return '\t'.join(field.strip() for field in row) + '\n'


def next_lines(rows, start, count):
    """Return count lines from position start, going back to the first line at the end,
    and the position where the next run starts."""
    lines = []
    position = start % len(rows)
    for _ in range(count):
        lines.append(to_log_line(rows[position]))
        position = (position + 1) % len(rows)
    return lines, position


def read_position(state):
    try:
        return int(state.read_text(encoding='utf-8').strip())
    except (FileNotFoundError, ValueError):
        return 0


def main():
    parser = argparse.ArgumentParser(
        description='Write order lines as log files.')
    parser.add_argument('--lines',
                        type=int,
                        default=100,
                        help='lines to write (default: %(default)s)')
    parser.add_argument('--data',
                        type=Path,
                        default=HERE / 'online-retail.csv.gz',
                        help='the data set (default: %(default)s)')
    parser.add_argument('--output',
                        type=Path,
                        default=Path('/var/log/retail'),
                        help='folder of the log files (default: %(default)s)')
    parser.add_argument(
        '--state',
        type=Path,
        default=HERE / 'last_line.txt',
        help='file with the position of the next line (default: %(default)s)')
    args = parser.parse_args()

    rows = read_rows(args.data)
    start = read_position(args.state)
    lines, position = next_lines(rows, start, args.lines)
    log_file = args.output / time.strftime('%Y%m%d-%H%M%S.log')
    with open(log_file, 'w', encoding='utf-8', newline='') as target:
        target.writelines(lines)
    args.state.write_text(f'{position}\n', encoding='utf-8')
    print(f'Wrote {len(lines)} lines, from line {start + 1} of {len(rows)}, '
          f'to {log_file}')


if __name__ == '__main__':
    main()
