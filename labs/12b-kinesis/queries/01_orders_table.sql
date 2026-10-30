-- Lab 12b, step 7: a table over the log lines that Firehose delivers.
-- Replace YOUR_BUCKET with the name of your bucket (run echo $BUCKET), in the
-- two places where it appears.
-- In the Athena query editor, choose the workgroup big-data-labs-retail and
-- the database big_data_labs_retail, and run ONE statement at a time.

-- Statement 1: Firehose writes the lines in folders such as orders/2026/11/06/21/,
-- with the fields separated by tabs. Partition projection makes the table find
-- the folders by itself.
CREATE EXTERNAL TABLE orders (
    invoice_no   string,
    stock_code   string,
    description  string,
    quantity     int,
    invoice_date string,
    unit_price   double,
    customer_id  bigint,
    country      string
)
PARTITIONED BY (datehour string)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
LOCATION 's3://YOUR_BUCKET/orders/'
TBLPROPERTIES (
    'projection.enabled' = 'true',
    'projection.datehour.type' = 'date',
    'projection.datehour.format' = 'yyyy/MM/dd/HH',
    'projection.datehour.range' = '2026/01/01/00,NOW',
    'projection.datehour.interval' = '1',
    'projection.datehour.interval.unit' = 'HOURS',
    'storage.location.template' = 's3://YOUR_BUCKET/orders/${datehour}/'
);
