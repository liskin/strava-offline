import argparse

from .sync import sync
from .strava import StravaAPI


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Local Strava mirror for archival/processing",
    )

    subparsers = parser.add_subparsers(metavar="<command>", required=True)

    parser_sqlite = subparsers.add_parser(
        'sqlite', help="sync bikes/activities to sqlite",
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
    parser_sqlite.add_argument(
        '--output', metavar="FILE", default="strava.sqlite",
        help="sqlite database file (default: strava.sqlite)",
    )
    parser_sqlite.add_argument(
        '--token-file', metavar="FILE", default="token.json",
        help="strava oauth2 token store (default: token.json)"
    )

    return parser.parse_args()


def command_sqlite(args: argparse.Namespace):
    strava = StravaAPI(
        scope=["read", "profile:read_all", "activity:read_all"],
        token_filename=args.token_file,
    )
    sync(strava=strava, full=args.full, filename=args.output)


def main():
    args = parse_args()
    args.func(args)
