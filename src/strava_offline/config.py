import argparse
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from functools import partial
import os
from typing import Optional
from typing import Type
from typing import TypeVar

import appdirs  # type: ignore [import]


def _getenv(var: str, default: Optional[str] = None) -> str:
    val = os.getenv(var)
    if val:
        return val
    elif default:
        return default
    else:
        raise RuntimeError(var + " not specified")


T = TypeVar('T', bound='BaseConfig')


@dataclass
class BaseConfig:
    # @final, python 3.7 compat
    @classmethod
    def from_args(cls: Type[T], args: argparse.Namespace) -> T:
        field_set = set(f.name for f in fields(cls))
        kwargs = {k: v for k, v in vars(args).items() if k in field_set and v is not None}
        return cls(**kwargs)  # type: ignore[call-arg]

    # @final, python 3.7 compat
    @classmethod
    def to_arg_parser(cls: Type[T]) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        cls.add_arguments(parser)
        return parser

    @classmethod
    def add_arguments(cls: Type[T], parser: argparse.ArgumentParser) -> None:
        assert not hasattr(super(), 'add_arguments')


@dataclass
class StravaApiConfig(BaseConfig):
    strava_client_id: str = field(
        default_factory=partial(_getenv, 'STRAVA_CLIENT_ID', default='54316'))
    strava_client_secret: str = field(
        default_factory=partial(_getenv, 'STRAVA_CLIENT_SECRET', default='3cfc2260d03472baca90d49fc4bc1d9714711771'))
    strava_token_filename: str = os.path.join(appdirs.user_config_dir(appname=__package__), 'token.json')
    http_host: str = '127.0.0.1'
    http_port: int = 12345

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        group = parser.add_argument_group('Strava API')
        group.add_argument(
            '--client-id', metavar="XXX", dest='strava_client_id',
            help="strava oauth2 client id (default: getenv('STRAVA_CLIENT_ID') or a built-in default)",
        )
        group.add_argument(
            '--client-secret', metavar="XXX", dest='strava_client_secret',
            help="strava oauth2 client secret (default: getenv('STRAVA_CLIENT_SECRET') or a built-in default)",
        )
        group.add_argument(
            '--token-file', metavar="FILE", dest='strava_token_filename',
            help=f"strava oauth2 token store (default: {cls.strava_token_filename})",
        )
        group.add_argument(
            '--http-host', metavar="HOST", dest='http_host',
            help=f"oauth2 http server host (default: {cls.http_host})",
        )
        group.add_argument(
            '--http-port', metavar="PORT", dest='http_port', type=int,
            help=f"oauth2 http server port (default: {cls.http_port})",
        )

        super().add_arguments(parser)


@dataclass
class StravaWebConfig(BaseConfig):
    strava_cookie_strava4_session: str = field(default_factory=partial(_getenv, 'STRAVA_COOKIE_STRAVA4_SESSION'))

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        group = parser.add_argument_group('Strava web')
        group.add_argument(
            '--strava4-session', metavar="XX", dest='strava_cookie_strava4_session',
            help="'_strava4_session' cookie value (default: getenv('STRAVA_COOKIE_STRAVA4_SESSION'))",
        )

        super().add_arguments(parser)


@dataclass
class DatabaseConfig(BaseConfig):
    strava_sqlite_database: str = os.path.join(appdirs.user_data_dir(appname=__package__), "strava.sqlite")

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        group = parser.add_argument_group('strava-offline database')
        group.add_argument(
            '--database', metavar="FILE", dest='strava_sqlite_database',
            help=f"sqlite database file (default: {cls.strava_sqlite_database})",
        )

        super().add_arguments(parser)


@dataclass
class SyncConfig(DatabaseConfig):
    full: bool = False

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--full', action='store_true',
            help="perform full sync instead of incremental",
        )

        super().add_arguments(parser)


@dataclass
class GpxConfig(DatabaseConfig):
    dir_activities: str = os.path.join("strava_data", "activities")
    dir_activities_backup: Optional[str] = None

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        group = parser.add_argument_group('strava-offline gpx storage')
        group.add_argument(
            '--dir-activities', metavar="DIR", dest='dir_activities',
            help=f"directory to store gpx files indexed by activity id (default: {cls.dir_activities})",
        )
        group.add_argument(
            '--dir-activities-backup', metavar="DIR", dest='dir_activities_backup',
            help="optional path to activities in Strava backup (no need to redownload these)",
        )

        super().add_arguments(parser)
