from contextlib import contextmanager
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import Callable
from typing import Iterator
from typing import List
from typing import Optional

from . import config
from .strava import StravaAPI


@contextmanager
def database(config: config.DatabaseConfig) -> Iterator[sqlite3.Connection]:
    Path(config.strava_sqlite_database).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(config.strava_sqlite_database, isolation_level=None)
    db.row_factory = sqlite3.Row
    try:
        with db:  # transaction
            db.execute("BEGIN")
            migrations = schema_prepare_migrations(db)
            schema_init(db)
            schema_do_migrations(db, migrations)
        yield db
    finally:
        db.close()


# Version of database schema. Bump this whenever one of the following is changed:
#
#  * schema_init
#  * sync_bike
#  * sync_activity
#
# The tables will be recreated using the stored json data and the new schema.
SCHEMA_VERSION = 1


def schema_init(db: sqlite3.Connection) -> None:
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


def schema_prepare_migrations(db: sqlite3.Connection) -> List[Callable]:
    migrations: List[Callable] = []

    db_version = db.execute("PRAGMA user_version").fetchone()[0]
    if db_version >= SCHEMA_VERSION:
        return migrations

    # migrate table "bike" by re-syncing entries from stored raw json replies
    try:
        db.execute("DROP TABLE IF EXISTS bike_old")
        db.execute("ALTER TABLE bike RENAME TO bike_old")

        def migrate_bike(db: sqlite3.Connection):
            for row in db.execute("SELECT json FROM bike_old"):
                sync_bike(json.loads(row['json']), db)
            db.execute("DROP TABLE bike_old")

        migrations.append(migrate_bike)
    except sqlite3.DatabaseError:
        pass

    # migrate table "activity" by re-syncing entries from stored raw json replies
    try:
        db.execute("DROP TABLE IF EXISTS activity_old")
        db.execute("ALTER TABLE activity RENAME TO activity_old")

        def migrate_activity(db: sqlite3.Connection):
            for row in db.execute("SELECT json FROM activity_old"):
                sync_activity(json.loads(row['json']), db)
            db.execute("DROP TABLE activity_old")

        migrations.append(migrate_activity)
    except sqlite3.DatabaseError:
        pass

    # update schema version
    def migrate_version(db: sqlite3.Connection):
        db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    migrations.append(migrate_version)

    return migrations


def schema_do_migrations(db: sqlite3.Connection, migrations: List[Callable]) -> None:
    for migration in migrations:
        migration(db)


def sync_bike(bike, db: sqlite3.Connection):
    db.execute(
        "INSERT OR REPLACE INTO bike(id, json, name) VALUES (?, ?, ?)",
        (bike['id'], json.dumps(bike), bike['name'])
    )


def sync_bikes(strava, db: sqlite3.Connection):
    with db:  # transaction
        db.execute("BEGIN")

        old_bikes = set(b['id'] for b in db.execute("SELECT id FROM bike"))

        for bike in strava.get_bikes():
            old_bikes.discard(bike['id'])
            sync_bike(bike, db)

        delete = ((bike,) for bike in old_bikes)
        db.executemany("DELETE FROM bike WHERE id = ?", delete)


def sync_activity(activity, db: sqlite3.Connection):
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


def sync_activities(
    strava: StravaAPI, db: sqlite3.Connection, before: Optional[datetime] = None
):
    with db:  # transaction
        db.execute("BEGIN")

        old_activities = set(a['id'] for a in db.execute("SELECT id FROM activity"))

        for activity in strava.get_activities(before=before):
            status = "seen: " if activity['id'] in old_activities else "new:  "
            print(status + str(activity['id']) + " - " + activity['start_date'])

            old_activities.discard(activity['id'])
            sync_activity(activity, db)

        delete = ((activity,) for activity in old_activities)
        db.executemany("DELETE FROM activity WHERE id = ?", delete)


def sync_activities_incremental(
    strava: StravaAPI, db: sqlite3.Connection, before: Optional[datetime] = None
):
    with db:  # transaction
        db.execute("BEGIN")

        old_activities = set(a['id'] for a in db.execute("SELECT id FROM activity"))

        seen = 0
        for activity in strava.get_activities(before=before):
            status = "seen: " if activity['id'] in old_activities else "new:  "
            print(status + str(activity['id']) + " - " + activity['start_date'])

            if activity['id'] in old_activities:
                seen += 1
            if seen > 10:
                break

            sync_activity(activity, db)


def sync(config: config.SyncConfig, strava: StravaAPI):
    with database(config) as db:
        sync_bikes(strava, db)
        if config.full:
            sync_activities(strava, db)
        else:
            sync_activities_incremental(strava, db)
