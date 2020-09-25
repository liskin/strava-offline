import stravalib  # type: ignore

from . import sync
from . import strava


stravaapi = strava.StravaAPI(
    scope=["read", "profile:read_all", "activity:read_all"],
)


def main():
    stravaapi.get_athlete()  # dummy request to trigger refresh if necessary
    strava = stravalib.Client(access_token=stravaapi.access_token)
    sync.sync(strava)
