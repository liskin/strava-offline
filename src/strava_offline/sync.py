from contextlib import contextmanager
import json
import sqlite3


@contextmanager
def database():
    db = sqlite3.connect("strava.sqlite")
    db.row_factory = sqlite3.Row
    try:
        db.execute((
            "CREATE TABLE IF NOT EXISTS bike"
            "( id TEXT PRIMARY KEY"
            ", json TEXT"
            ", name TEXT"
            ")"
        ))
        db.execute((
            "CREATE TABLE IF NOT EXISTS activity"
            "( id INTEGER PRIMARY KEY"
            ", json TEXT"
            ", upload_id TEXT"
            ", name TEXT"
            ", start_date TEXT"
            ", moving_time INTEGER"
            ", elapsed_time INTEGER"
            ", distance REAL"
            ", total_elevation_gain REAL"
            ", gear_id TEXT"
            ", type TEXT"
            ", commute BOOLEAN"
            ")"
        ))
        yield db
    finally:
        db.close()


def sync_bikes(strava, db):
    with db:  # transaction
        for bike in strava.get_bikes():
            db.execute(
                "INSERT OR REPLACE INTO bike(id, json, name) VALUES (?, ?, ?)",
                (bike['id'], json.dumps(bike), bike['name'])
            )


def sync_activities(strava, db):
    with db:  # transaction
        for activity in strava.get_activities():
            db.execute(
                (
                    "INSERT OR REPLACE INTO activity"
                    "( id"
                    ", json"
                    ", upload_id"
                    ", name"
                    ", start_date"
                    ", moving_time"
                    ", elapsed_time"
                    ", distance"
                    ", total_elevation_gain"
                    ", gear_id"
                    ", type"
                    ", commute"
                    ")"
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                (
                    activity['id'],
                    json.dumps(activity),
                    activity['upload_id'],
                    activity['name'],
                    activity['start_date'],
                    activity['moving_time'],
                    activity['elapsed_time'],
                    activity['distance'],
                    activity['total_elevation_gain'],
                    activity['gear_id'],
                    activity['type'],
                    activity['commute'],
                )
            )
            print(activity['start_date'])


def sync(strava):
    with database() as db:
        sync_bikes(strava, db)
        sync_activities(strava, db)
