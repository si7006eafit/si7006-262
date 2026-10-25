-- 1. The partitions of flights_by_month, one per folder month=
SHOW PARTITIONS flights_by_month;

-- 2. Flights of March by airline, from the table without partitions
SELECT airline_code,
       count(*) AS flights
FROM flights
WHERE substr(CAST(flight_date AS varchar), 1, 7) = '2026-03'
GROUP BY airline_code
ORDER BY airline_code;

-- 3. The same flights, from the partitioned table
SELECT airline_code,
       count(*) AS flights
FROM flights_by_month
WHERE month = '2026-03'
GROUP BY airline_code
ORDER BY airline_code;
