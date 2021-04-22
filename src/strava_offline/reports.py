import sqlite3

from tabulate import tabulate


def tabulate_execute(db: sqlite3.Connection, sql: str, *params) -> str:
    table = (dict(row) for row in db.execute(sql, params))
    return tabulate(table, headers='keys')


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
