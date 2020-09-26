from abc import ABC, abstractmethod
from dataclasses import dataclass
import argparse

from . import config
from .strava import StravaAPI, StravaWeb
from .sync import sync


class BaseCommand(ABC):
    @classmethod
    @abstractmethod
    def add_subparser(cls, subparsers) -> argparse.ArgumentParser:
        pass


class SqliteCommand(BaseCommand):
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

    @classmethod
    def add_subparser(cls, subparsers) -> argparse.ArgumentParser:
        return subparsers.add_parser(
            'sqlite', parents=[cls.Config.to_arg_parser()],
            help="sync bikes/activities to sqlite",
            description="""
            Synchronize bikes and activities metadata to local sqlite3 database.
            Unless --full is given, the sync is incremental, i.e. only new activities
            are synchronized and deletions aren't detected.
            """,
        )

    @staticmethod
    def run(config: Config) -> None:
        strava = StravaAPI(
            config=config,
            scope=["read", "profile:read_all", "activity:read_all"],
        )
        sync(config=config, strava=strava, full=config.full)


commands = [
    SqliteCommand,
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Local Strava mirror for archival/processing",
    )

    subparsers = parser.add_subparsers(metavar="<command>", required=True)
    for command in commands:
        subparser = command.add_subparser(subparsers)
        subparser.set_defaults(command=command)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = args.command.Config.from_args(args)
    args.command.run(config)
