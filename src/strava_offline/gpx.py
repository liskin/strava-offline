import gzip
import logging
import os
from pathlib import Path
import sqlite3
from typing import Optional

from . import config
from .strava import StravaWeb
from .sync import database


def find_gpx(d: Path, i: int) -> Optional[Path]:
    for suffix in [".gpx", ".gpx.gz"]:
        p = Path(d, str(i) + suffix)
        if p.exists():
            return p

    return None


def link_backup_activities(
        db: sqlite3.Connection,
        dir_activities: Path, dir_activities_backup: Path) -> None:
    for activity in db.execute("SELECT id, upload_id FROM activity WHERE upload_id IS NOT NULL"):
        activity_id = int(activity['id'])
        upload_id = int(activity['upload_id'])

        if find_gpx(dir_activities, activity_id):
            continue

        backup = find_gpx(dir_activities_backup, activity_id) or find_gpx(dir_activities_backup, upload_id)
        if backup:
            link = Path(dir_activities, str(activity_id) + "".join(backup.suffixes))
            if hasattr(backup, 'link_to'):
                backup.link_to(link)  # type: ignore [attr-defined]
            else:
                os.link(backup, link)  # python 3.7 compat


def download_gpx(strava: StravaWeb, activity_id: int, path: Path) -> None:
    gpx = strava.get_gpx(activity_id)
    filename = Path(path, str(activity_id) + ".gpx.gz")
    tmpfilename = Path(path, str(activity_id) + ".gpx.gz.tmp")
    with gzip.open(tmpfilename, "wb") as f:
        f.write(gpx)
    tmpfilename.replace(filename)


def download_activities(db: sqlite3.Connection, strava: StravaWeb, dir_activities: Path) -> None:
    new = 0

    for activity in db.execute("SELECT id FROM activity WHERE upload_id IS NOT NULL AND has_location_data"):
        activity_id = int(activity['id'])
        if find_gpx(dir_activities, activity_id):
            continue

        logging.debug(f"downloading gpx for activity {activity_id}")
        download_gpx(strava=strava, activity_id=activity_id, path=dir_activities)
        new += 1

    logging.info(f"downloaded gpx for {new} new activities")


def sync(config: config.GpxConfig, strava: StravaWeb):
    config.dir_activities.mkdir(parents=True, exist_ok=True)

    with database(config) as db:
        if config.dir_activities_backup:
            link_backup_activities(
                db=db,
                dir_activities=config.dir_activities,
                dir_activities_backup=config.dir_activities_backup)

        download_activities(db=db, strava=strava, dir_activities=config.dir_activities)
