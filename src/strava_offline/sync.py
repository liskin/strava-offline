from contextlib import contextmanager
from datetime import datetime
from stravalib import unithelper as uh  # type: ignore
import pytz
import sqlite3


@contextmanager
def database():
    db = sqlite3.connect("strava.sqlite")
    db.row_factory = sqlite3.Row
    try:
        db.execute((
            "CREATE TABLE IF NOT EXISTS activity"
            "( id INTEGER PRIMARY KEY"
            ", name TEXT"
            ", start_date INTEGER"
            ", moving_time REAL"
            ", elapsed_time REAL"
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


def sync_activities(strava, db):
    now = datetime.now(pytz.utc)
    with db:  # transaction
        for activity in strava.get_activities(before=now):
            try:
                db.execute(
                    (
                        "INSERT INTO activity"
                        "( id"
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
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    ),
                    (
                        activity.id,
                        activity.name,
                        int(activity.start_date.timestamp()),
                        float(activity.moving_time.total_seconds()),
                        float(activity.elapsed_time.total_seconds()),
                        float(uh.meters(activity.distance).num),
                        float(uh.meters(activity.total_elevation_gain).num),
                        activity.gear_id,
                        activity.type,
                        activity.commute,
                    )
                )
                print(activity.start_date)
            except sqlite3.IntegrityError:
                continue


def sync(strava):
    with database() as db:
        sync_activities(strava, db)
