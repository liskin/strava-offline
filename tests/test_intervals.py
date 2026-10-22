from typing import Any
from typing import List
from typing import Mapping

from strava_offline import config
from strava_offline import intervals
from strava_offline.intervals import _activity_to_summary

# All data below is synthetic: made-up ids, bike ids and names, not from any
# real account. The intervals.icu Activity shape is documented at
# https://intervals.icu/api/v1/docs.


def test_map_outdoor_ride():
    a = {
        'id': "i111",
        'strava_id': "1000000001",
        'source': "OAUTH_CLIENT",
        'start_date': "2024-01-02T08:30:00Z",
        'start_date_local': "2024-01-02T09:30:00",
        'type': "Ride",
        'sub_type': None,
        'name': "Test outdoor ride",
        'distance': 12345.6,
        'moving_time': 3600,
        'elapsed_time': 4000,
        'total_elevation_gain': 150.0,
        'gear': {'id': "b100", 'name': None},
        'commute': False,
        'trainer': None,
    }
    s = _activity_to_summary(a)
    # strava_id becomes the integer primary key (stable across sources)
    assert s['id'] == 1000000001
    assert isinstance(s['id'], int)
    assert s['upload_id'] is None
    assert s['name'] == "Test outdoor ride"
    assert s['start_date'] == "2024-01-02T08:30:00Z"  # already UTC, unchanged
    assert s['moving_time'] == 3600
    assert s['elapsed_time'] == 4000
    assert s['distance'] == 12345.6
    assert s['total_elevation_gain'] == 150.0
    assert s['gear_id'] == "b100"
    assert s['type'] == "Ride"           # coarse enum, matches Strava API `type`
    assert s['sport_type'] == "Ride"     # no sub_type -> falls back to type
    assert s['commute'] is False
    assert s['trainer'] is False
    assert s['has_location_data'] is True


def test_map_virtual_ride_has_no_location():
    a = {
        'strava_id': "1000000002",
        'source': "ZWIFT",
        'start_date': "2024-02-03T18:00:00Z",
        'type': "VirtualRide",
        'sub_type': None,
        'name': "Test virtual ride",
        'distance': 17206.47,
        'moving_time': 1570,
        'elapsed_time': 1570,
        'total_elevation_gain': 100.0,
        'gear': {'id': "b200"},
        'commute': False,
        'trainer': True,
    }
    s = _activity_to_summary(a)
    assert s['type'] == "VirtualRide"
    assert s['trainer'] is True
    assert s['has_location_data'] is False


def test_map_uses_sub_type_as_sport_type():
    a = {
        'strava_id': "1000000003",
        'source': "OAUTH_CLIENT",
        'type': "Ride",
        'sub_type': "MountainBikeRide",
        'gear': None,
    }
    s = _activity_to_summary(a)
    assert s['type'] == "Ride"
    assert s['sport_type'] == "MountainBikeRide"
    assert s['gear_id'] is None  # gear may be absent


class _FakeResponse:
    def __init__(self, payload: Any):
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> Any:
        return self._payload


class _FakeSession:
    def __init__(self, payload: Any):
        self._payload = payload
        self.auth = None
        self.headers: dict = {}

    def get(self, url: str, params=None) -> _FakeResponse:
        return _FakeResponse(self._payload)


def _api_with_activities(payload: List[Mapping[str, Any]]) -> intervals.IntervalsAPI:
    api = intervals.IntervalsAPI(config=config.IntervalsConfig(intervals_api_key="k"))
    api._session = _FakeSession(payload)  # type: ignore[assignment]
    return api


def test_get_activities_skips_strava_stubs():
    payload = [
        # Strava-sourced stub: intervals can't re-expose it, all fields null.
        {'id': "2000000009", 'source': "STRAVA", 'strava_id': None, 'name': None},
        # Non-Strava activity with data.
        {'id': "i1", 'source': "OAUTH_CLIENT", 'strava_id': "1000000004",
         'type': "Ride", 'name': "Ride", 'gear': {'id': "b100"}},
        # Defensive: anything lacking a strava_id is skipped too.
        {'id': "i2", 'source': "GARMIN_CONNECT", 'strava_id': None, 'name': "x"},
    ]
    got = list(_api_with_activities(payload).get_activities())
    assert [a['id'] for a in got] == [1000000004]


def test_get_bikes_returns_roster():
    api = intervals.IntervalsAPI(config=config.IntervalsConfig(intervals_api_key="k"))
    api._session = _FakeSession({'bikes': [  # type: ignore[assignment]
        {'id': "b100", 'name': "Road", 'distance': 1.0},
        {'id': "b200", 'name': "MTB", 'distance': 2.0},
    ]})
    assert list(api.get_bikes()) == [
        {'id': "b100", 'name': "Road"},
        {'id': "b200", 'name': "MTB"},
    ]
