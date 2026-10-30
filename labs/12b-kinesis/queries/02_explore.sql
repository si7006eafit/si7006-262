-- Lab 12b, steps 7 and 11: explore the order lines.
-- Run ONE statement at a time.

-- Statement 1: the lines that arrived, and the files and the folders where Firehose
-- wrote them.
SELECT count(*) AS order_lines,
       count(DISTINCT "$path") AS files,
       count(DISTINCT datehour) AS folders
FROM orders;

-- Statement 2: the five products with more units sold. Returns have a negative
-- quantity and are left out.
SELECT stock_code, description, sum(quantity) AS units
FROM orders
WHERE quantity > 0
GROUP BY stock_code, description
ORDER BY units DESC, stock_code
LIMIT 5;

-- Statement 3: the five customers that spent the most.
SELECT customer_id, count(DISTINCT invoice_no) AS invoices,
       round(sum(quantity * unit_price), 2) AS amount
FROM orders
WHERE quantity > 0
GROUP BY customer_id
ORDER BY amount DESC
LIMIT 5;

-- Statement 4: the returns. Their invoice starts with C and their quantity is
-- negative.
SELECT count(*) AS return_lines,
       count(DISTINCT invoice_no) AS return_invoices,
       round(sum(quantity * unit_price), 2) AS amount
FROM orders
WHERE quantity < 0;
