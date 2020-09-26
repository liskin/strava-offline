from dataclasses import dataclass
from typing import Optional
import argparse

from . import config
from . import sqlite
from .strava import StravaAPI, StravaWeb


class BaseCommand:
    name: str
    help: Optional[str] = None
    description: Optional[str] = None

    Config = config.BaseConfig

    @classmethod
    def add_subparser(cls, subparsers) -> None:
        subparser = subparsers.add_parser(
            cls.name, parents=[cls.Config.to_arg_parser()],
            help=cls.help, description=cls.description,
        )
        subparser.set_defaults(command=cls)


class SqliteCommand(BaseCommand):
    name = 'sqlite'
    help = "sync bikes/activities to sqlite"
    description = """
    Synchronize bikes and activities metadata to local sqlite3 database.
    Unless --full is given, the sync is incremental, i.e. only new activities
    are synchronized and deletions aren't detected.
    """

    @dataclass
    class Config(config.StravaApiConfig, config.DatabaseConfig):
        full: bool = False

        @classmethod
        def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
            parser.add_argument(
                '--full', action='store_true',
                help="perform full sync instead of incremental",
            )

            super().add_arguments(parser)

    @staticmethod
    def run(config: Config) -> None:
        strava = StravaAPI(
            config=config,
            scope=["read", "profile:read_all", "activity:read_all"],
        )
        sqlite.sync(config=config, strava=strava, full=config.full)


commands = [
    SqliteCommand,
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Local Strava mirror for archival/processing",
    )

    subparsers = parser.add_subparsers(metavar="<command>", required=True)
    for command in commands:
        command.add_subparser(subparsers)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = args.command.Config.from_args(args)
    args.command.run(config)
