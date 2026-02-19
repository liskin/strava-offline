import datetime
from typing import TextIO

import click

from . import config
from . import gpx
from . import reports
from . import sync
from .strava import StravaAPI
from .strava import StravaWeb


@click.group(context_settings={'max_content_width': 120})
@config.yaml_config_sample_option(sample_hidden={'output'})
def cli() -> None:
    pass


@cli.command(name='sqlite', short_help="Sync bikes/activities to sqlite")
@config.SyncConfig.options()
def cli_sqlite(config: config.SyncConfig) -> None:
    """
    Synchronize bikes and activities metadata to local sqlite3 database.
    Unless --full is given, the sync is incremental, i.e. only new activities
    are synchronized and deletions aren't detected.
    """
    strava = StravaAPI(config=config)
    sync.sync(config=config, strava=strava)


@cli.command(name='gpx', short_help="Download gpx for your activities")
@config.GpxConfig.options()
def cli_gpx(config: config.GpxConfig) -> None:
    """
    Download known (previously synced using the "sqlite" command) activities in GPX format.
    It's recommended to only use this incrementally to download the latest activities every day
    or week, and download the bulk of your historic activities directly from Strava.
    Use --dir-activities-backup to avoid downloading activities already downloaded in the bulk.
    """
    strava = StravaWeb(config=config)
    gpx.sync(config=config, strava=strava)


option_output = click.option('-o', '--output', type=click.File('w'), default='-', help="Output file")
option_year = click.argument('year', type=int, default=datetime.datetime.now().year)


@cli.command(name='report-yearly')
@config.DatabaseConfig.options()
@option_output
@option_year
def cli_report_yearly(config: config.DatabaseConfig, output: TextIO, year: int) -> None:
    "Show yearly report by activity type"
    with sync.database(config) as db:
        print(reports.yearly(db, year), file=output)


@cli.command(name='report-yearly-bikes')
@config.DatabaseConfig.options()
@option_output
@option_year
def cli_report_yearly_bikes(config: config.DatabaseConfig, output: TextIO, year: int) -> None:
    "Show yearly report by bike"
    with sync.database(config) as db:
        print(reports.yearly_bikes(db, year), file=output)


@cli.command(name='report-bikes')
@config.DatabaseConfig.options()
@option_output
def cli_report_bikes(config: config.DatabaseConfig, output: TextIO) -> None:
    "Show all-time report by bike"
    with sync.database(config) as db:
        print(reports.bikes(db), file=output)
