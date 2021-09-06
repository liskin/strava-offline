from datetime import datetime
from datetime import timezone
import json
from typing import Any
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional

from requests import Session
from requests_oauthlib import OAuth2Session  # type: ignore [import]

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
            scope=','.join(scope),
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

    def get_bikes(self) -> Iterable[Mapping[str, Any]]:
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


class StravaWeb:
    def __init__(self, config: config.StravaWebConfig):
        self._config = config
        self._session = Session()
        self._session.cookies.set(
            '_strava4_session', config.strava_cookie_strava4_session,
            domain="www.strava.com", secure=True,
        )

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
