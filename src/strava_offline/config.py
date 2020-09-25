import os


def getenv(var: str) -> str:
    val = os.getenv(var)
    assert val is not None
    return val


strava_client_id = getenv('STRAVA_CLIENT_ID')
strava_client_secret = getenv('STRAVA_CLIENT_SECRET')

http_host = '127.0.0.1'
http_port = 12345
