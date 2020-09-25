from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode
import requests


@dataclass
class StravaAPI:
    client_id: str
    client_secret: str
    access_token: Optional[str] = None

    def authorization_url(self, redirect_uri, scope):
        params = {
            'client_id': self.client_id,
            'response_type': "code",
            'redirect_uri': redirect_uri,
            'scope': ','.join(scope),
        }
        return "https://www.strava.com/oauth/authorize?" + urlencode(params)

    def exchange_code_for_token(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': "authorization_code",
            'code': code,
        }
        r = requests.post("https://www.strava.com/oauth/token", params)
        r.raise_for_status()
        return r.json()

    def refresh_access_token(self, refresh_token):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': "refresh_token",
            'refresh_token': refresh_token,
        }
        r = requests.post("https://www.strava.com/oauth/token", params)
        r.raise_for_status()
        return r.json()
