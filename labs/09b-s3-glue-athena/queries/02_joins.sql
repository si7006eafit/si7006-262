-- 1. Flights, cancelled flights and average departure delay of each airline
SELECT a.airline_name,
       count(*) AS flights,
       sum(CASE WHEN CAST(f.cancelled AS integer) = 1 THEN 1 ELSE 0 END) AS cancelled,
       round(avg(date_diff('minute',
                           CAST(f.scheduled_departure AS timestamp),
                           try_cast(f.actual_departure AS timestamp))), 1) AS avg_delay_min
FROM flights f
JOIN airlines a ON a.airline_code = f.airline_code
GROUP BY a.airline_name
ORDER BY flights DESC;

-- 2. The ten routes with more flights, with the cities of their airports
SELECT o.city AS origin_city,
       d.city AS destination_city,
       count(*) AS flights
FROM flights f
JOIN airports o ON o.airport_code = f.origin
JOIN airports d ON d.airport_code = f.destination
GROUP BY o.city, d.city
ORDER BY flights DESC, origin_city, destination_city
LIMIT 10;

-- 3. Flights and seats offered by aircraft model, without the cancelled flights
SELECT c.model,
       count(*) AS flights,
       sum(CAST(c.seats AS integer)) AS seats_offered
FROM flights f
JOIN aircraft c ON c.tail_number = f.tail_number
WHERE CAST(f.cancelled AS integer) = 0
GROUP BY c.model
ORDER BY flights DESC;

-- 4. Average departure delay of each airline by month: the result of the Glue job of lab 9
SELECT f.airline_code,
       substr(CAST(f.flight_date AS varchar), 1, 7) AS month,
       count(*) AS flights,
       round(avg(date_diff('minute',
                           CAST(f.scheduled_departure AS timestamp),
                           try_cast(f.actual_departure AS timestamp))), 1) AS avg_delay_min
FROM flights f
WHERE CAST(f.cancelled AS integer) = 0
GROUP BY f.airline_code, substr(CAST(f.flight_date AS varchar), 1, 7)
ORDER BY f.airline_code, month
LIMIT 12;
