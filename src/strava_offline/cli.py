import datetime
from typing import TextIO
from typing import Union

import click

from . import config
from . import gpx
from . import reports
from . import sync
from .intervals import IntervalsAPI
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

    With --source intervals, metadata is fetched from intervals.icu using the
    --intervals-api-key instead of the (subscription-gated) Strava API. Note
    that intervals.icu can't re-expose activities it received from Strava, so
    only activities recorded elsewhere (e.g. a bike computer syncing directly to
    intervals.icu) are available; upload_id isn't provided either.
    """
    strava: Union[StravaAPI, IntervalsAPI]
    if config.source == 'intervals':
        if not config.intervals_api_key:
            raise click.UsageError(
                "--intervals-api-key (env INTERVALS_API_KEY) is required for --source intervals")
        strava = IntervalsAPI(config=config)
    else:
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
