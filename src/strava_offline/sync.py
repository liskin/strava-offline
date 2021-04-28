from contextlib import contextmanager
from datetime import datetime
import sqlite3
from typing import Iterator
from typing import Optional

from . import config
from . import sqlite
from .strava import StravaAPI

table_bike = sqlite.Table(
    name='bike',
    columns={
        'id': "TEXT PRIMARY KEY",
        'name': "TEXT",
    },
    from_dict=lambda bike: {
        'id': bike['id'],
        'name': bike['name'],
    },
)

table_activity = sqlite.Table(
    name='activity',
    columns={
        'id': "INTEGER PRIMARY KEY",
        'upload_id': "TEXT",
        'name': "TEXT",
        'start_date': "TEXT",
        'moving_time': "INTEGER",
        'elapsed_time': "INTEGER",
        'distance': "REAL",
        'total_elevation_gain': "REAL",
        'gear_id': "TEXT",
        'type': "TEXT",
        'commute': "BOOLEAN",
        'has_location_data': "BOOLEAN",
    },
    from_dict=lambda activity: {
        'id': activity['id'],
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
    },
)

schema = sqlite.Schema(
    # Version of database schema. Bump this whenever the schema changes,
    # tables will be recreated using the stored json data and the new schema.
    version=2,

    tables=[
        table_bike,
        table_activity,
    ],
)


@contextmanager
def database(config: config.DatabaseConfig) -> Iterator[sqlite3.Connection]:
    with sqlite.database(config.strava_sqlite_database, schema) as db:
        yield db


def sync_bikes(strava: StravaAPI, db: sqlite3.Connection) -> None:
    table_bike.upsert(db, strava.get_bikes())


def sync_activities(
    strava: StravaAPI,
    db: sqlite3.Connection,
    before: Optional[datetime] = None,
    incremental: bool = False,
) -> None:
    table_activity.upsert(db, strava.get_activities(before=before), incremental=incremental)


def sync(config: config.SyncConfig, strava: StravaAPI):
    with database(config) as db:
        sync_bikes(strava, db)
        sync_activities(strava, db, incremental=(not config.full))
