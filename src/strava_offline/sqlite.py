from contextlib import contextmanager
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional

from . import config
from .strava import StravaAPI


@contextmanager
def database(config: config.DatabaseConfig) -> Iterator[sqlite3.Connection]:
    if isinstance(config.strava_sqlite_database, Path):
        config.strava_sqlite_database.parent.mkdir(parents=True, exist_ok=True)
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
#  * bike_row
#  * activity_row
#
# The tables will be recreated using the stored json data and the new schema.
SCHEMA_VERSION = 2


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
        ", has_location_data BOOLEAN"
        ")"
    ))


def schema_table_migration(
    db: sqlite3.Connection,
    table: str,
    make_row: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> List[Callable]:
    # migrate table by re-syncing entries from stored raw json replies
    try:
        db.execute(f"DROP TABLE IF EXISTS {table}_old")
        db.execute(f"ALTER TABLE {table} RENAME TO {table}_old")

        def migrate(db: sqlite3.Connection):
            for row in db.execute(f"SELECT json FROM {table}_old"):
                upsert_row(db, table, make_row(json.loads(row['json'])))
            db.execute(f"DROP TABLE {table}_old")

        return [migrate]
    except sqlite3.DatabaseError:
        return []


def schema_prepare_migrations(db: sqlite3.Connection) -> List[Callable]:
    migrations: List[Callable] = []

    db_version = db.execute("PRAGMA user_version").fetchone()[0]
    if db_version >= SCHEMA_VERSION:
        return migrations

    def migrate_version(db: sqlite3.Connection):
        db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    migrations.extend(schema_table_migration(db, 'bike', bike_row))
    migrations.extend(schema_table_migration(db, 'activity', bike_row))
    migrations.append(migrate_version)

    return migrations


def schema_do_migrations(db: sqlite3.Connection, migrations: List[Callable]) -> None:
    for migration in migrations:
        migration(db)


def upsert_row(db: sqlite3.Connection, table: str, row: Dict[str, Any]) -> None:
    keys = ', '.join(row.keys())
    placeholders = ', '.join('?' for k in row.keys())
    db.execute(
        f"INSERT OR REPLACE INTO {table} ({keys}) VALUES ({placeholders})",
        tuple(row.values())
    )


def upsert(
    db: sqlite3.Connection,
    table: str,
    rows: Iterable[Dict[str, Any]],
    incremental: bool = False,
) -> None:
    with db:  # transaction
        db.execute("BEGIN")

        old_ids = set(r['id'] for r in db.execute(f"SELECT id FROM {table}"))
        seen = 0

        for row in rows:
            # TODO: use logging
            status = "seen: " if row['id'] in old_ids else "new:  "
            print(status + str(row['id']))

            if row['id'] in old_ids:
                old_ids.discard(row['id'])

                seen += 1
                if incremental and seen > 10:
                    break

            upsert_row(db, table, row)

        if not incremental:
            delete = ((i,) for i in old_ids)
            db.executemany(f"DELETE FROM {table} WHERE id = ?", delete)


def bike_row(bike: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'id': bike['id'],
        'json': json.dumps(bike),
        'name': bike['name'],
    }


def sync_bikes(strava: StravaAPI, db: sqlite3.Connection) -> None:
    rows = (bike_row(b) for b in strava.get_bikes())
    upsert(db, 'bike', rows)


def activity_row(activity: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'id': activity['id'],
        'json': json.dumps(activity),
        'upload_id': activity['upload_id'],
        'name': activity['name'],
        'start_date': activity['start_date'],
        'moving_time': activity['moving_time'],
        'elapsed_time': activity['elapsed_time'],
        'distance': activity['distance'],
        'total_elevation_gain': activity['total_elevation_gain'],
        'gear_id': activity['gear_id'],
        'type': activity['type'],
        'commute': activity['commute'],
        'has_location_data': activity['start_latlng'] is not None,
    }


def sync_activities(
    strava: StravaAPI,
    db: sqlite3.Connection,
    before: Optional[datetime] = None,
    incremental: bool = False,
) -> None:
    rows = (activity_row(a) for a in strava.get_activities(before=before))
    upsert(db, 'activity', rows, incremental=incremental)


def sync(config: config.SyncConfig, strava: StravaAPI):
    with database(config) as db:
        sync_bikes(strava, db)
        sync_activities(strava, db, incremental=(not config.full))
