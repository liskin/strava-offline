from datetime import datetime
from datetime import timezone
import json
import logging
import re
from typing import Any
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional

from requests import Session
from requests_oauthlib import OAuth2Session

from . import config
from . import redirect_server


class StravaAPI:
    def __init__(
        self,
        config: config.StravaApiConfig,
        scope: List[str] = ["read", "profile:read_all", "activity:read_all"],
    ):
        self._config = config

        token = self._load_token()

        self._session = OAuth2Session(
            client_id=config.strava_client_id,
            redirect_uri=redirect_server.redirect_uri(config),
            scope=scope,
            token=token,
            auto_refresh_url="https://www.strava.com/oauth/token",
            auto_refresh_kwargs={
                'client_id': config.strava_client_id,
                'client_secret': config.strava_client_secret,
            },
            token_updater=self._save_token,
        )

        if not token:
            self._authorize()

    def _load_token(self):
        try:
            with self._config.strava_token_filename.open("r") as f:
                return json.load(f)
        except Exception:
            return None

    def _save_token(self, token) -> None:
        self._config.strava_token_filename.parent.mkdir(parents=True, exist_ok=True)
        with self._config.strava_token_filename.open("w") as f:
            json.dump(token, f)

    def _authorize(self) -> None:
        authorization_url, _ = self._session.authorization_url("https://www.strava.com/oauth/authorize")
        code = redirect_server.get_code(config=self._config, authorization_url=authorization_url)
        token = self._session.fetch_token(
            "https://www.strava.com/oauth/token",
            code=code,
            client_secret=self._config.strava_client_secret,
            include_client_id=True,
        )
        self._save_token(token)

    def get_athlete(self) -> Mapping[str, Any]:
        r = self._session.get("https://www.strava.com/api/v3/athlete")
        r.raise_for_status()
        return r.json()

    def get_bikes(self, bike_ids: Optional[Iterable[str]] = None) -> Iterable[Mapping[str, Any]]:
        # bike_ids is accepted for interface parity with StravaWeb but unused:
        # the API returns the athlete's full bike roster.
        return self.get_athlete()['bikes']

    def get_activities(self, before: Optional[datetime] = None) -> Iterable[Mapping[str, Any]]:
        if not before:
            before = datetime.now(timezone.utc)
        params = {'before': int(before.timestamp()), 'per_page': 200, 'page': 0}
        while True:
            params['page'] += 1
            r = self._session.get("https://www.strava.com/api/v3/athlete/activities", params=params)
            r.raise_for_status()
            activities = r.json()
            if activities:
                yield from activities
            else:
                break


class NotGpx(Exception):
    pass


def _normalize_start_date(start_time: Optional[str]) -> Optional[str]:
    # Strava's website returns e.g. "2026-06-08T14:38:34+0000"; the API uses the
    # "...Z" form. Normalize so both sources store the same shape.
    if not start_time:
        return None
    return start_time.replace("+0000", "Z")


def _web_gear_id(model: Mapping[str, Any]) -> Optional[str]:
    # training_activities exposes a numeric bike_id / athlete_gear_id; the API
    # (and strava-offline's bike table) uses the "b"/"g"-prefixed string form.
    bike_id = model.get('bike_id')
    if bike_id:
        return f"b{bike_id}"
    gear_id = model.get('athlete_gear_id')
    if gear_id:
        return f"g{gear_id}"
    return None


def _parse_bike_name(html: str) -> Optional[str]:
    # The bike detail page title is "Strava | <athlete> | <bike name>"; fall
    # back to the page's <h1> if the title format ever changes.
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    if m:
        parts = [p.strip() for p in m.group(1).split("|")]
        if len(parts) >= 3 and parts[-1]:
            return parts[-1]
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip() or None
    return None


def _training_activity_to_summary(model: Mapping[str, Any]) -> Mapping[str, Any]:
    # Map a /athlete/training_activities row to the shape table_activity expects
    # from the API's SummaryActivity. upload_id has no website equivalent.
    return {
        'id': model['id'],
        'upload_id': None,
        'name': model.get('name'),
        'start_date': _normalize_start_date(model.get('start_time')),
        'moving_time': model.get('moving_time_raw'),
        'elapsed_time': model.get('elapsed_time_raw'),
        'distance': model.get('distance_raw'),
        'total_elevation_gain': model.get('elevation_gain_raw'),
        'gear_id': _web_gear_id(model),
        # activity_type_display_name is the coarse category ("Ride") matching the
        # API's `type`; sport_type is the fine enum ("MountainBikeRide"). Avoid
        # display_type, which is the human label ("Mountain Bike Ride").
        'type': model.get('activity_type_display_name') or model.get('sport_type'),
        'sport_type': model.get('sport_type') or model.get('activity_type_display_name'),
        'commute': bool(model.get('commute')),
        'trainer': bool(model.get('trainer')),
        'has_location_data': bool(model.get('has_latlng')),
    }


class StravaWeb:
    def __init__(self, config: config.StravaWebConfig):
        self._config = config
        self._session = Session()
        self._session.cookies.set(
            '_strava4_session', config.strava_cookie_strava4_session,
            domain="www.strava.com", secure=True,
        )

    def get_bikes(self, bike_ids: Optional[Iterable[str]] = None) -> Iterable[Mapping[str, Any]]:
        # The website has no bike-roster endpoint, so resolve names one detail
        # page at a time for the bikes referenced by synced activities. gear_id
        # is "b<id>"; the page lives at /bikes/<id>. Deleted bikes 404 and are
        # skipped, which naturally yields the athlete's current roster.
        for gear_id in (bike_ids or []):
            r = self._session.get(f"https://www.strava.com/bikes/{gear_id[1:]}")
            if r.status_code == 404:
                logging.debug("bike %s not found (deleted?), skipping", gear_id)
                continue
            r.raise_for_status()
            name = _parse_bike_name(r.text)
            if name:
                yield {'id': gear_id, 'name': name}
            else:
                logging.warning("could not parse name for bike %s", gear_id)

    def get_activities(self, before: Optional[datetime] = None) -> Iterable[Mapping[str, Any]]:
        # Page through the website's training-log JSON endpoint (same cookie as
        # gpx export). `before` is unused: the log is newest-first and the
        # incremental cutoff is handled by the sqlite upsert.
        headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
        page = 0
        while True:
            page += 1
            r = self._session.get(
                "https://www.strava.com/athlete/training_activities",
                params={'per_page': '20', 'page': str(page), 'new_activity_only': 'false'},
                headers=headers)
            r.raise_for_status()
            models = r.json().get('models') or []
            if not models:
                break
            for model in models:
                yield _training_activity_to_summary(model)

    def _get_gpx(self, what: str, activity_id: int) -> bytes:
        r = self._session.get(f"https://www.strava.com/activities/{activity_id}/export_{what}")
        r.raise_for_status()

        content_type_ok = r.headers.get('Content-Type') == "application/octet-stream"

        content_disposition, content_disposition_params = _parse_content_disposition_header(
            r.headers.get('Content-Disposition', ""))
        content_disposition_ok = (
            content_disposition == "attachment"
            and content_disposition_params['filename'].endswith(".gpx"))

        if content_type_ok and content_disposition_ok:
            return r.content
        else:
            raise NotGpx(f"expected gpx attachment, got:\n{r.headers}")

    def get_gpx(self, activity_id: int) -> bytes:
        try:
            # Try to obtain the original gpx as the export_gpx endpoint always returns a processed
            # and stripped gpx. The original gpx may contain a longer track than shown on Strava as
            # it's not filtered and cropped.
            return self._get_gpx("original", activity_id)
        except NotGpx:
            return self._get_gpx("gpx", activity_id)


def _parse_content_disposition_header(header):
    tokens = header.split(';')
    content_disposition, params = tokens[0].strip(), tokens[1:]
    params_dict = {}
    items_to_strip = "\"' "

    for param in params:
        param = param.strip()
        if param:
            key, value = param, True
            index_of_equals = param.find("=")
            if index_of_equals != -1:
                key = param[:index_of_equals].strip(items_to_strip)
                value = param[index_of_equals + 1:].strip(items_to_strip)
            params_dict[key.lower()] = value
    return content_disposition, params_dict
