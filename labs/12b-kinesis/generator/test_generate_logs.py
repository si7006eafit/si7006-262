import csv
import gzip
import io

import generate_logs

ROWS = [
    [
        '554065', '22755', 'SMALL PURPLE BABUSHKA NOTEBOOK ', '12',
        '5/22/2011 10:39', '0.85', '18287', 'United Kingdom'
    ],
    [
        '574890', '22041', 'RECORD FRAME 7" SINGLE SIZE ', '48',
        '11/07/11 14:23', '2.1', '18229', 'United Kingdom'
    ],
    [
        'C541433', '23166', 'MEDIUM CERAMIC TOP STORAGE JAR', '-74215',
        '1/18/2011 10:17', '1.04', '12346', 'United Kingdom'
    ],
]


def write_data(path):
    text = io.StringIO()
    writer = csv.writer(text)
    writer.writerow(generate_logs.FIELDS)
    writer.writerows(ROWS)
    with gzip.open(path, 'wt', encoding='utf-8', newline='') as target:
        target.write(text.getvalue())


def test_the_rows_skip_the_header_and_keep_the_quotes(tmp_path):
    data = tmp_path / 'data.csv.gz'
    write_data(data)
    rows = generate_logs.read_rows(data)
    assert len(rows) == 3
    assert rows[1][2] == 'RECORD FRAME 7" SINGLE SIZE '


def test_a_log_line_has_eight_trimmed_fields_separated_by_tabs():
    line = generate_logs.to_log_line(ROWS[0])
    assert line.endswith('\n')
    fields = line.rstrip('\n').split('\t')
    assert len(fields) == 8
    assert fields[2] == 'SMALL PURPLE BABUSHKA NOTEBOOK'


def test_the_lines_go_back_to_the_first_at_the_end():
    lines, position = generate_logs.next_lines(ROWS, 2, 3)
    assert [line.split('\t')[0]
            for line in lines] == ['C541433', '554065', '574890']
    assert position == 2


def test_a_missing_state_starts_at_the_first_line(tmp_path):
    assert generate_logs.read_position(tmp_path / 'missing.txt') == 0
