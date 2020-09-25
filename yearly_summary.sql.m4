-- vim:set ft=sql:

.headers on
.mode column
.width 20 20 20
.echo on
SELECT
	CAST(SUM(a.distance) / 1000 AS INT) || " km" AS "Total distance YEAR",
	CAST(SUM(a.moving_time) / 3600 AS INT) || "h" AS "Total moving time YEAR"
FROM activity a INNER JOIN bike b ON a.gear_id = b.id
WHERE start_date BETWEEN 'YEAR-01-01' AND 'incr(YEAR)-01-01';

SELECT
	b.name AS "Bike",
	CAST(SUM(a.distance) / 1000 AS INT) || " km" AS "Distance",
	CAST(SUM(a.moving_time) / 3600 AS INT) || " h" AS "Moving time"
FROM activity a INNER JOIN bike b ON a.gear_id = b.id
WHERE start_date BETWEEN 'YEAR-01-01' AND 'incr(YEAR)-01-01'
GROUP BY b.id ORDER BY SUM(a.distance) DESC;
