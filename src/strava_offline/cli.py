from dataclasses import dataclass

import click

from . import config
from . import gpx
from . import sqlite
from .strava import StravaAPI
from .strava import StravaWeb


@click.group(context_settings={'max_content_width': 120})
@config.yaml_config_sample_option()
def cli() -> None:
    pass


@dataclass
class SqliteCommandConfig(config.StravaApiConfig, config.SyncConfig):
    pass


@cli.command(name='sqlite', short_help="Sync bikes/activities to sqlite")
@SqliteCommandConfig.options()
def cli_sqlite(config: SqliteCommandConfig) -> None:
    """
    Synchronize bikes and activities metadata to local sqlite3 database.
    Unless --full is given, the sync is incremental, i.e. only new activities
    are synchronized and deletions aren't detected.
    """
    strava = StravaAPI(
        config=config,
        scope=["read", "profile:read_all", "activity:read_all"],
    )
    sqlite.sync(config=config, strava=strava)


@dataclass
class GpxCommandConfig(config.StravaWebConfig, config.GpxConfig):
    pass


@cli.command(name='gpx', short_help="Download gpx for your activities")
@GpxCommandConfig.options()
def cli_gpx(config: GpxCommandConfig) -> None:
    """
    Download known (previously synced using the "sqlite" command) activities in GPX format.
    It's recommended to only use this incrementally to download the latest activities every day
    or week, and download the bulk of your historic activities directly from Strava.
    Use --dir-activities-backup to avoid downloading activities already downloaded in the bulk.
    """
    strava = StravaWeb(config=config)
    gpx.sync(config=config, strava=strava)
