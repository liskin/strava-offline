from strava_offline import config
from strava_offline import gpx
from strava_offline import sqlite


def database():
    return sqlite.database(config.DatabaseConfig(strava_sqlite_database=":memory:"))


def test_link_backup_activities(tmp_path):
    backup = tmp_path / "backup"
    backup.mkdir()

    activities = tmp_path / "activities"
    activities.mkdir()

    (backup / "1.gpx").touch()
    (backup / "4.gpx").touch()
    (backup / "6.gpx").touch()
    (activities / "5.gpx").touch()
    (backup / "7.gpx.gz").touch()

    with database() as db:
        db.executemany("INSERT INTO activity (id, upload_id) VALUES (?, ?)", [
            [1, 2],
            [3, 4],
            [5, 6],
            [7, 8],
        ])

        gpx.link_backup_activities(
            db=db, dir_activities=activities, dir_activities_backup=backup)

    assert (activities / "1.gpx").samefile(backup / "1.gpx")
    assert (activities / "3.gpx").samefile(backup / "4.gpx")
    assert not (activities / "5.gpx").samefile(backup / "6.gpx")
    assert (activities / "7.gpx.gz").samefile(backup / "7.gpx.gz")
