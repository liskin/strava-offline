from dataclasses import dataclass, field, fields
from functools import partial
import argparse
import os


def _getenv(var: str) -> str:
    val = os.getenv(var)
    if val is None:
        raise RuntimeError(var + " not specified")
    return val


@dataclass
class Config:
    strava_client_id: str = field(default_factory=partial(_getenv, 'STRAVA_CLIENT_ID'))
    strava_client_secret: str = field(default_factory=partial(_getenv, 'STRAVA_CLIENT_SECRET'))
    strava_cookie_strava4_session: str = field(default_factory=partial(_getenv, 'STRAVA_COOKIE_STRAVA4_SESSION'))
    strava_token_filename: str = "token.json"
    strava_sqlite_database: str = "strava.sqlite"

    http_host: str = '127.0.0.1'
    http_port: int = 12345

    @staticmethod
    def from_args(args: argparse.Namespace) -> 'Config':
        field_set = set(f.name for f in fields(Config))
        kwargs = {k: v for k, v in vars(args).items() if k in field_set and v is not None}
        return Config(**kwargs)
