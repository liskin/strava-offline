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

    @staticmethod
    def to_arg_parser(parser: argparse.ArgumentParser) -> None:
        group_config = parser.add_argument_group('config')
        group_config.add_argument(
            '--client-id', metavar="XXX", dest='strava_client_id',
            help="strava oauth2 client id (default: genenv('STRAVA_CLIENT_ID'))",
        )
        group_config.add_argument(
            '--client-secret', metavar="XXX", dest='strava_client_secret',
            help="strava oauth2 client secret (default: genenv('STRAVA_CLIENT_SECRET'))",
        )
        group_config.add_argument(
            '--strava4-session', metavar="XX", dest='strava_cookie_strava4_session:',
            help="'_strava4_session' cookie value (default: genenv('STRAVA_COOKIE_STRAVA4_SESSION'))",
        )
        group_config.add_argument(
            '--token-file', metavar="FILE", dest='strava_token_filename',
            help=f"strava oauth2 token store (default: {Config.strava_token_filename})",
        )
        group_config.add_argument(
            '--database', metavar="FILE", dest='strava_sqlite_database',
            help=f"sqlite database file (default: {Config.strava_sqlite_database})",
        )
        group_config.add_argument(
            '--http-host', metavar="HOST", dest='http_host',
            help=f"oauth2 http server host (default: {Config.http_host})",
        )
        group_config.add_argument(
            '--http-port', metavar="PORT", dest='http_port', type=int,
            help=f"oauth2 http server port (default: {Config.http_port})",
        )
