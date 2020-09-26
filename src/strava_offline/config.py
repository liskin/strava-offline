from dataclasses import dataclass, field, fields
from functools import partial
from typing import Type, TypeVar, final
import argparse
import os


def _getenv(var: str) -> str:
    val = os.getenv(var)
    if val is None:
        raise RuntimeError(var + " not specified")
    return val


T = TypeVar('T', bound='BaseConfig')


@dataclass
class BaseConfig:
    @final
    @classmethod
    def from_args(cls: Type[T], args: argparse.Namespace) -> T:
        field_set = set(f.name for f in fields(cls))
        kwargs = {k: v for k, v in vars(args).items() if k in field_set and v is not None}
        return cls(**kwargs)  # type: ignore[call-arg]

    @final
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
    strava_client_id: str = field(default_factory=partial(_getenv, 'STRAVA_CLIENT_ID'))
    strava_client_secret: str = field(default_factory=partial(_getenv, 'STRAVA_CLIENT_SECRET'))
    strava_token_filename: str = "token.json"
    http_host: str = '127.0.0.1'
    http_port: int = 12345

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        group = parser.add_argument_group('Strava API')
        group.add_argument(
            '--client-id', metavar="XXX", dest='strava_client_id',
            help="strava oauth2 client id (default: genenv('STRAVA_CLIENT_ID'))",
        )
        group.add_argument(
            '--client-secret', metavar="XXX", dest='strava_client_secret',
            help="strava oauth2 client secret (default: genenv('STRAVA_CLIENT_SECRET'))",
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
            '--strava4-session', metavar="XX", dest='strava_cookie_strava4_session:',
            help="'_strava4_session' cookie value (default: genenv('STRAVA_COOKIE_STRAVA4_SESSION'))",
        )

        super().add_arguments(parser)


@dataclass
class DatabaseConfig(BaseConfig):
    strava_sqlite_database: str = "strava.sqlite"

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        group = parser.add_argument_group('strava-offline database')
        group.add_argument(
            '--database', metavar="FILE", dest='strava_sqlite_database',
            help=f"sqlite database file (default: {cls.strava_sqlite_database})",
        )

        super().add_arguments(parser)
