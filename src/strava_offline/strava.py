from datetime import datetime
from requests import Session
from requests_oauthlib import OAuth2Session  # type: ignore
from typing import List
import json
import pytz

from . import redirect_server
from . import config


class StravaAPI:
    def __init__(self, config: config.StravaApiConfig, scope: List[str]):
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
            with open(self._config.strava_token_filename, "r") as f:
                return json.load(f)
        except Exception:
            return None

    def _save_token(self, token) -> None:
        with open(self._config.strava_token_filename, "w") as f:
            json.dump(token, f)

    def _authorize(self) -> None:
        authorization_url, _ = self._session.authorization_url("https://www.strava.com/oauth/authorize")
        code = redirect_server.get_code(config=self._config, authorization_url=authorization_url)
        token = self._session.fetch_token(
            "https://www.strava.com/oauth/token",
            code=code,
            client_secret=self._config.strava_client_secret,
        )
        self._save_token(token)

    def get_athlete(self):
        r = self._session.get("https://www.strava.com/api/v3/athlete")
        r.raise_for_status()
        return r.json()

    def get_bikes(self):
        return self.get_athlete()['bikes']

    def get_activities(self):
        now = int(datetime.now(pytz.utc).timestamp())
        params = {'before': now, 'per_page': 200, 'page': 0}
        while True:
            params['page'] += 1
            r = self._session.get("https://www.strava.com/api/v3/athlete/activities", params=params)
            r.raise_for_status()
            activities = r.json()
            if activities:
                yield from activities
            else:
                break


class StravaWeb:
    def __init__(self, config: config.StravaWebConfig):
        self._config = config
        self._session = Session()
        self._session.cookies.set(
            '_strava4_session', config.strava_cookie_strava4_session,
            domain="www.strava.com", secure=True,
        )

    def get_gpx(self, activity_id: int) -> bytes:
        r = self._session.get(f"https://www.strava.com/activities/{activity_id}/export_gpx")
        r.raise_for_status()

        content_type_ok = r.headers.get('Content-Type') == "application/octet-stream"
        content_disposition_ok = "attachment" in r.headers.get('Content-Disposition', "")
        if content_type_ok and content_disposition_ok:
            return r.content
        else:
            raise RuntimeError(f"expected application/octet-stream attachment, got:\n{r.headers}")

    def download_gpx(self, activity_id: int, filename: str) -> None:
        gpx = self.get_gpx(activity_id)
        with open(filename, "wb") as f:
            f.write(gpx)
