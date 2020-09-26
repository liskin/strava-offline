import argparse

from .config import Config
from .strava import StravaAPI, StravaWeb
from .sync import sync


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Local Strava mirror for archival/processing",
    )

    parser_config = argparse.ArgumentParser(add_help=False)
    Config.to_arg_parser(parser_config)

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
