from .sync import sync
from .strava import StravaAPI


def main():
    strava = StravaAPI(scope=["read", "profile:read_all", "activity:read_all"])
    sync(strava)
