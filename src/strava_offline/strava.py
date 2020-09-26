from datetime import datetime
from requests_oauthlib import OAuth2Session  # type: ignore
from typing import List
import json
import pytz

from . import redirect_server
from .config import Config


class StravaAPI:
    def __init__(self, config: Config, scope: List[str]):
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

    @property
    def access_token(self) -> str:
        return self._session.access_token

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
