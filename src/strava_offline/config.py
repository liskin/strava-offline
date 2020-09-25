import os


strava_client_id = os.getenv('STRAVA_CLIENT_ID')
strava_client_secret = os.getenv('STRAVA_CLIENT_SECRET')

if not strava_client_id or not strava_client_secret:
    raise RuntimeError("STRAVA_CLIENT_ID or STRAVA_CLIENT_SECRET not found in env")

http_host = '127.0.0.1'
http_port = 12345
