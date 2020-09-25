from . import auth
from . import sync


def main():
    strava = auth.get_client()
    sync.sync(strava)
