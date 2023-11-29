import click

from . import config_file


@click.command(context_settings={'max_content_width': 120})
@config_file.yaml_config_option()
@config_file.yaml_config_sample_option()
def cli() -> None:
    pass
