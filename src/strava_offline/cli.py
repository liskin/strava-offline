import argparse

from .config import Config
from .strava import StravaAPI
from .sync import sync


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Local Strava mirror for archival/processing",
    )

    parser_config = argparse.ArgumentParser(add_help=False)
    group_config = parser_config.add_argument_group('config')
    group_config.add_argument(
        '--client-id', metavar="XXX", dest='strava_client_id',
        help="strava oauth2 client id (default: genenv('STRAVA_CLIENT_ID'))",
    )
    group_config.add_argument(
        '--client-secret', metavar="XXX", dest='strava_client_secret',
        help="strava oauth2 client secret (default: genenv('STRAVA_CLIENT_SECRET'))",
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

    subparsers = parser.add_subparsers(metavar="<command>", required=True)

    parser_sqlite = subparsers.add_parser(
        'sqlite', parents=[parser_config],
        help="sync bikes/activities to sqlite",
        description="""
        Synchronize bikes and activities metadata to local sqlite3 database.
        Unless --full is given, the sync is incremental, i.e. only new activities
        are synchronized and deletions aren't detected.
        """,
    )
    parser_sqlite.set_defaults(func=command_sqlite)
    parser_sqlite.add_argument(
        '--full', action='store_true',
        help="perform full sync instead of incremental",
    )

    return parser.parse_args()


def command_sqlite(config: Config, args: argparse.Namespace):
    strava = StravaAPI(
        config=config,
        scope=["read", "profile:read_all", "activity:read_all"],
    )
    sync(config=config, strava=strava, full=args.full)


def main():
    args = parse_args()
    config = Config.from_args(args)
    args.func(config, args)
