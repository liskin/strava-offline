import pytest  # type: ignore [import]

from strava_offline import config
from strava_offline import sqlite
from strava_offline.strava import StravaAPI


def database():
    return sqlite.database(config.DatabaseConfig(strava_sqlite_database=":memory:"))


def strava(tmp_path):
    token = tmp_path / "token.json"
    token.write_text('{"access_token": "token"}')
    cfg = config.StravaApiConfig(strava_token_filename=str(token))
    return StravaAPI(config=cfg, scope=[])


@pytest.mark.vcr
def test_sync_bikes(tmp_path):
    with database() as db:
        # initial sync
        sqlite.sync_bikes(strava=strava(tmp_path), db=db)

        # check that we have all the bikes we expect
        bikes = [list(row) for row in db.execute(
            "SELECT id, name FROM bike ORDER BY id")]
        assert bikes == [
            ['b123456', 'bike1'],
            ['b234567', 'bike2'],
            ['b345678', 'bike3'],
        ]

        # delete one bike
        db.execute("DELETE FROM bike WHERE id = 'b123456'")

        # sync again
        sqlite.sync_bikes(strava=strava(tmp_path), db=db)

        # recheck that we have all the bikes we expect
        bikes = [list(row) for row in db.execute(
            "SELECT id, name FROM bike ORDER BY id")]
        assert bikes == [
            ['b123456', 'bike1'],
            ['b234567', 'bike2'],
            ['b345678', 'bike3'],
        ]
