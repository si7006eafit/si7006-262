-- 1. The tables that the crawler created in the database airline_lake
SHOW TABLES;

-- 2. The columns of flights and the type the crawler gave each one
DESCRIBE flights;

-- 3. The columns of airlines: the names come from the header of the file
DESCRIBE airlines;

-- 4. The rows of each table
SELECT 'flights' AS table_name, count(*) AS row_count FROM flights
UNION ALL
SELECT 'airports', count(*) FROM airports
UNION ALL
SELECT 'airlines', count(*) FROM airlines
UNION ALL
SELECT 'aircraft', count(*) FROM aircraft;

-- 5. The airlines, with no header row among the data
SELECT *
FROM airlines
ORDER BY airline_code;
