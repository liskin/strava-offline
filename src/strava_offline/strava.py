from urllib.parse import urlencode
import requests


def authorization_url(client_id, redirect_uri, scope):
    params = {
        'client_id': client_id,
        'response_type': "code",
        'redirect_uri': redirect_uri,
        'scope': ','.join(scope),
    }
    return "https://www.strava.com/oauth/authorize?" + urlencode(params)


def exchange_code_for_token(client_id, client_secret, code):
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': "authorization_code",
        'code': code,
    }
    r = requests.post("https://www.strava.com/oauth/token", params)
    r.raise_for_status()
    return r.json()


def refresh_access_token(client_id, client_secret, refresh_token):
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': "refresh_token",
        'refresh_token': refresh_token,
    }
    r = requests.post("https://www.strava.com/oauth/token", params)
    r.raise_for_status()
    return r.json()
