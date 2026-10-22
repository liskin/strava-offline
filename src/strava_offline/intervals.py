from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Iterable
from typing import Mapping
from typing import Optional

from requests import Session

from . import config

INTERVALS_BASE = "https://intervals.icu/api/v1"


def _activity_to_summary(activity: Mapping[str, Any]) -> Mapping[str, Any]:
    # Map an intervals.icu Activity to the shape table_activity expects from the
    # Strava API's SummaryActivity. Every non-Strava-sourced activity carries a
    # strava_id, so we key on it to keep integer ids stable across sources (a db
    # previously synced from Strava keeps the same activity ids).
    gear = activity.get('gear') or {}
    activity_type = activity.get('type')
    trainer = bool(activity.get('trainer'))
    # intervals.icu exposes no lat/lng field; approximate has_location_data:
    # indoor/virtual rides and trainer sessions have no GPS track.
    outdoor = not trainer and not (activity_type or "").startswith("Virtual")
    return {
        'id': int(activity['strava_id']),
        'upload_id': None,  # not exposed by intervals.icu
        'name': activity.get('name'),
        'start_date': activity.get('start_date'),  # already UTC ISO-8601 with 'Z'
        'moving_time': activity.get('moving_time'),
        'elapsed_time': activity.get('elapsed_time'),
        'distance': activity.get('distance'),
        'total_elevation_gain': activity.get('total_elevation_gain'),
        'gear_id': gear.get('id'),  # already in strava-offline's "b<id>" form
        # intervals' `type` is Strava's coarse enum ("Ride"/"VirtualRide"); it
        # has no separate sport_type and sub_type is usually null.
        'type': activity_type,
        'sport_type': activity.get('sub_type') or activity_type,
        'commute': bool(activity.get('commute')),
        'trainer': trainer,
        'has_location_data': outdoor,
    }


class IntervalsAPI:
    def __init__(self, config: config.IntervalsConfig):
        self._config = config
        self._session = Session()
        # HTTP Basic auth: username is the literal "API_KEY", password is the key.
        self._session.auth = ('API_KEY', config.intervals_api_key)
        # intervals.icu returns 403 for requests without a User-Agent.
        self._session.headers['User-Agent'] = \
            "strava-offline (https://github.com/liskin/strava-offline)"

    def _get_athlete(self) -> Mapping[str, Any]:
        r = self._session.get(f"{INTERVALS_BASE}/athlete/0")
        r.raise_for_status()
        return r.json()

    def get_bikes(self, bike_ids: Optional[Iterable[str]] = None) -> Iterable[Mapping[str, Any]]:
        # bike_ids is accepted for interface parity with other sources but unused:
        # intervals returns the athlete's full bike roster (with names).
        for bike in self._get_athlete().get('bikes', []):
            yield {'id': bike['id'], 'name': bike['name']}

    def get_activities(self, before: Optional[datetime] = None) -> Iterable[Mapping[str, Any]]:
        params = {'oldest': '1970-01-01'}
        if before:
            # intervals wants a naive local ISO datetime; UTC is close enough as
            # this only trims the newest edge (incremental dedup does the rest).
            params['newest'] = before.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

        r = self._session.get(f"{INTERVALS_BASE}/athlete/0/activities", params=params)
        r.raise_for_status()

        for activity in r.json():
            # Strava's API terms forbid intervals from re-exposing Strava-sourced
            # activities: they come back as empty stubs (source=="STRAVA", all
            # fields null). Skip anything without a strava_id to link on.
            if activity.get('source') == 'STRAVA' or not activity.get('strava_id'):
                continue
            yield _activity_to_summary(activity)
