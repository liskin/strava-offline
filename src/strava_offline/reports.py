from io import StringIO
import sqlite3
import csv
from typing import Optional

from tabulate import tabulate


def tabulate_execute(db: sqlite3.Connection, sql: str, *params, format='plain') -> str:
    # db.set_trace_callback(print)
    # sqlite3.enable_callback_tracebacks(True)
    table = (dict(row) for row in db.execute(sql, params))
    if format == 'csv':
        table = list(table)
        if len(table) == 0:
            return ""

        keys = list(table[0].keys())
        stream = StringIO()
        writer = csv.DictWriter(stream, keys)
        writer.writeheader()
        for row in table:
            writer.writerow(row)

        return stream.getvalue()

    else:
        return tabulate(table, headers='keys', tablefmt=format)


def yearly(db: sqlite3.Connection, year: int) -> str:
    return tabulate_execute(db, """
        SELECT
            a.type AS "Activity type",
            CAST(SUM(a.distance) / 1000 AS INT) AS "Distance (km)",
            CAST(SUM(a.moving_time) / 3600 AS INT) AS "Moving time (hour)"
        FROM activity a
        WHERE start_date LIKE ?
        GROUP BY 1
        ORDER BY 2 DESC
    """, f"{year}-%")


def yearly_bikes(db: sqlite3.Connection, year: int) -> str:
    return tabulate_execute(db, """
        SELECT
            b.name AS "Bike",
            CAST(SUM(a.distance) / 1000 AS INT) AS "Distance (km)",
            CAST(SUM(a.moving_time) / 3600 AS INT) AS "Moving time (hour)"
        FROM activity a INNER JOIN bike b ON a.gear_id = b.id
        WHERE start_date LIKE ?
        GROUP BY 1
        ORDER BY 2 DESC
    """, f"{year}-%")


def bikes_cummulative_distance(db: sqlite3.Connection, resolution: str, output_format: str, bike: Optional[str], start_year: int, end_year) -> str:
    sql_template = """
        WITH
        daily AS (
            SELECT
                b.name AS "Bike"
                ,CASE
                    WHEN ? == "day" THEN strftime("%Y-%m-%d", a.start_date)
                    WHEN ? == "month" THEN strftime("%Y-%m-01", a.start_date)
                    WHEN ? == "year" THEN strftime("%Y-01-01", a.start_date)
                END AS "Date"
                ,CAST(SUM(a.distance) / 1000.0 AS DOUBLE) AS "Distance (km)"
                ,CAST(SUM(a.moving_time) / 3600.0 AS DOUBLE) AS "Moving time (hour)"
                ,CAST(SUM(a.total_elevation_gain) AS DOUBLE) AS "Total Elevation (m)"
            FROM activity a INNER JOIN bike b ON a.gear_id = b.id
            GROUP BY 1, 2
        )

        ,daily_with_cumsum AS (
            SELECT
                *
                ,SUM(`Distance (km)`) OVER (PARTITION BY Bike ORDER BY Date ASC) AS "Cummulative (km)"
                ,SUM(`Moving time (hour)`) OVER (PARTITION BY Bike ORDER BY Date ASC) AS "Cummulative (hour)"
                ,SUM(`Total Elevation (m)`) OVER (PARTITION BY Bike ORDER BY Date ASC) AS "Cummulative (elevation)"
            FROM daily
        )

        SELECT
            Bike
            ,Date
            ,printf("%.02f", `Distance (km)`) AS `Distance (km)`
            ,printf("%.02f", `Cummulative (km)`) AS `Cummulative (km)`
            ,printf("%.02f", `Total Elevation (m)`) AS `Total Elevation (m)`
            ,printf("%.02f", `Cummulative (elevation)`) AS `Cummulative (elevation)`
            ,printf("%.02f", `Moving Time (hour)`) AS `Moving Time (hour)`
            ,printf("%.02f", `Cummulative (hour)`) AS `Cummulative (hour)`
        FROM daily_with_cumsum
        WHERE
            CAST(strftime("%Y", Date) AS INT) BETWEEN  ? AND  ?
            AND
            Bike LIKE ?
        ORDER BY Bike ASC, Date ASC
    """

    bike = bike or ""
    return tabulate_execute(db, sql_template , resolution, resolution, resolution, start_year, end_year, f'{bike}%', format=output_format)


def bikes(db: sqlite3.Connection) -> str:
    return tabulate_execute(db, """
        SELECT
            b.name AS "Bike",
            CAST(SUM(a.distance) / 1000 AS INT) AS "Distance (km)",
            CAST(SUM(a.moving_time) / 3600 AS INT) AS "Moving time (hour)"
        FROM activity a INNER JOIN bike b ON a.gear_id = b.id
        GROUP BY 1
        ORDER BY 2 DESC
    """)
