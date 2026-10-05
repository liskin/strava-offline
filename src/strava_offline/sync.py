from contextlib import contextmanager
from datetime import datetime
import logging
import sqlite3
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import Union

from . import config
from . import sqlite
from .strava import StravaAPI
from .strava import StravaWeb

# A metadata source: the OAuth API client or the website scraper. Both expose
# get_bikes() and get_activities().
StravaSource = Union[StravaAPI, StravaWeb]


def _has_location_data(activity: Mapping[str, Any]) -> bool:
    # The Strava API exposes start_latlng (a [lat, lng] list) but no explicit
    # boolean; the website scraper provides has_location_data directly.
    if 'has_location_data' in activity:
        return bool(activity['has_location_data'])
    start_latlng = activity.get('start_latlng')
    return isinstance(start_latlng, list) and len(start_latlng) >= 2


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
        'sport_type': "TEXT",
        'commute': "BOOLEAN",
        'trainer': "BOOLEAN",
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
        'sport_type': activity.get('sport_type'),
        'commute': activity['commute'],
        'trainer': activity['trainer'],
        'has_location_data': _has_location_data(activity),
    },
)

schema = sqlite.Schema(
    # Version of database schema. Bump this whenever the schema changes,
    # tables will be recreated using the stored json data and the new schema.
    version=4,

    tables=[
        table_bike,
        table_activity,
    ],
)


@contextmanager
def database(config: config.DatabaseConfig) -> Iterator[sqlite3.Connection]:
    with sqlite.database(config.strava_sqlite_database, schema) as db:
        yield db


def sync_bikes(strava: StravaSource, db: sqlite3.Connection) -> None:
    # Bikes referenced by already-synced activities. The API source returns its
    # full roster regardless; the web source resolves names for exactly these
    # ids (it has no roster endpoint).
    bike_ids = [row['gear_id'] for row in db.execute(
        "SELECT DISTINCT gear_id FROM activity WHERE gear_id LIKE 'b%'")]
    bikes = list(strava.get_bikes(bike_ids))
    if bikes:
        table_bike.upsert(db, bikes)
    else:
        # Don't run a (destructive) full upsert with no data: that would delete
        # bikes synced earlier.
        logging.info("no bikes to sync; bike table left unchanged")


def sync_activities(
    strava: StravaSource,
    db: sqlite3.Connection,
    before: Optional[datetime] = None,
    incremental: bool = False,
) -> None:
    table_activity.upsert(db, strava.get_activities(before=before), incremental=incremental)


def sync(config: config.SyncConfig, strava: StravaSource):
    with database(config) as db:
        # Activities first: the web bike sync derives its id list from them.
        sync_activities(strava, db, incremental=(not config.full))
        sync_bikes(strava, db)
