import gzip
from unittest.mock import Mock

import pytest
from requests import Response

from strava_offline import config
from strava_offline import gpx
from strava_offline.strava import NotGpx
from strava_offline.strava import StravaWeb
from strava_offline import sync


def database():
    return sync.database(config.DatabaseConfig(strava_sqlite_database=":memory:"))


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


@pytest.mark.vcr
def test_download_gpx(tmp_path):
    cfg = config.StravaWebConfig(strava_cookie_strava4_session="TEST")
    strava = StravaWeb(config=cfg)
    gpx.download_gpx(strava=strava, activity_id=123, path=tmp_path)

    assert (tmp_path / "123.gpx.gz").exists()


@pytest.fixture
def strava_web(monkeypatch):
    cfg = config.StravaWebConfig(strava_cookie_strava4_session="TEST")
    strava = StravaWeb(config=cfg)
    get = Mock()
    monkeypatch.setattr(strava._session, "get", get)
    return strava, get


def attachment(content_disposition, body=b"<gpx/>"):
    response = Response()
    response.status_code = 200
    response.headers["Content-Type"] = "application/octet-stream"
    response.headers["Content-Disposition"] = content_disposition
    response._content = body
    return response


@pytest.mark.parametrize("content_disposition", [
    'attachment; filename="Morning.gpx"',
    'attachment; filename="Morning; Ride.gpx"',
    'attachment; filename="Morning; Ride.gpx"; filename*=UTF-8\'\'Morning%3B%20Ride.gpx',
    'attachment; filename*=UTF-8\'\'Morning%3B%20Ride.gpx',
    'ATTACHMENT; FILENAME="Morning.gpx"',
])
def test_download_gpx_attachment_filename(tmp_path, strava_web, content_disposition):
    strava, get = strava_web
    get.return_value = attachment(content_disposition)

    gpx.download_gpx(strava=strava, activity_id=123, path=tmp_path)

    assert gzip.decompress((tmp_path / "123.gpx.gz").read_bytes()) == b"<gpx/>"
    get.assert_called_once_with("https://www.strava.com/activities/123/export_original")


@pytest.mark.parametrize("content_disposition", [
    'attachment',
    'attachment; filename',
    'attachment; filename="Morning.fit"',
])
def test_download_gpx_falls_back_without_gpx_filename(tmp_path, strava_web, content_disposition):
    strava, get = strava_web
    get.side_effect = [
        attachment(content_disposition, b"original"),
        attachment('attachment; filename="Morning.gpx"', b"<gpx/>")]

    gpx.download_gpx(strava=strava, activity_id=123, path=tmp_path)

    assert gzip.decompress((tmp_path / "123.gpx.gz").read_bytes()) == b"<gpx/>"
    assert get.call_count == 2
    get.assert_called_with("https://www.strava.com/activities/123/export_gpx")


def test_download_gpx_rejects_attachments_without_filename(tmp_path, strava_web):
    strava, get = strava_web
    get.return_value = attachment('attachment')

    with pytest.raises(NotGpx):
        gpx.download_gpx(strava=strava, activity_id=123, path=tmp_path)

    assert get.call_count == 2
    assert not list(tmp_path.iterdir())
