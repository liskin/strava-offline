from abc import ABC
from abc import abstractmethod
import argparse
from dataclasses import dataclass
from typing import Optional
from typing import Type

from . import config
from . import gpx
from . import sqlite
from .strava import StravaAPI
from .strava import StravaWeb


class BaseCommand(ABC):
    name: str
    help: Optional[str] = None
    description: Optional[str] = None

    Config = config.BaseConfig

    # @final, python 3.7 compat
    @classmethod
    def add_subparser(cls, subparsers) -> None:
        subparser = subparsers.add_parser(
            cls.name, parents=[cls.Config.to_arg_parser()],
            help=cls.help, description=cls.description,
        )
        subparser.set_defaults(command=cls)

    @staticmethod
    @abstractmethod
    def run(config) -> None:
        pass


class SqliteCommand(BaseCommand):
    name = 'sqlite'
    help = "sync bikes/activities to sqlite"
    description = """
    Synchronize bikes and activities metadata to local sqlite3 database.
    Unless --full is given, the sync is incremental, i.e. only new activities
    are synchronized and deletions aren't detected.
    """

    @dataclass
    class Config(config.StravaApiConfig, config.SyncConfig):
        pass

    @staticmethod
    def run(config: Config) -> None:
        strava = StravaAPI(
            config=config,
            scope=["read", "profile:read_all", "activity:read_all"],
        )
        sqlite.sync(config=config, strava=strava)


class GpxCommand(BaseCommand):
    name = 'gpx'
    help = "download gpx for your activities"
    description = """
    Download known (previously synced using the "sqlite" command) activities in GPX format.
    It's recommended to only use this incrementally to download the latest activities every day
    or week, and download the bulk of your historic activities directly from Strava.
    Use --dir-activities-backup to avoid downloading activities already downloaded in the bulk.
    """

    @dataclass
    class Config(config.StravaWebConfig, config.GpxConfig):
        pass

    @staticmethod
    def run(config: Config) -> None:
        strava = StravaWeb(config=config)
        gpx.sync(config=config, strava=strava)


commands = [
    SqliteCommand,
    GpxCommand,
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
    command: Type[BaseCommand] = args.command
    config = command.Config.from_args(args)
    command.run(config)
