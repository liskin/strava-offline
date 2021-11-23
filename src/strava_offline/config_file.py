import os
import pathlib
from sys import stdout
from typing import Callable
from typing import Iterator
from typing import Optional
from typing import Set

import click
import click_config_file  # type: ignore [import]
import platformdirs
import yaml


def yaml_config_option():
    path = os.path.join(platformdirs.user_config_dir(appname=__package__), 'config.yaml')

    def provider(file_path, _cmd_name):
        if os.path.isfile(file_path):
            with open(file_path) as f:
                return yaml.safe_load(f)
        else:
            return {}

    return click_config_file.configuration_option(
        implicit=False, default=path, show_default=True, provider=provider)


def yaml_config_sample_option(**kwargs):
    def callback(ctx, _param, value) -> None:
        if not value or ctx.resilient_parsing:
            return

        stdout.write(yaml_config_sample(ctx.command, **kwargs))
        ctx.exit()

    return click.option(
        '--config-sample', is_flag=True, is_eager=True, expose_value=False,
        help="Show sample configuration file",
        callback=callback)


def yaml_config_sample(
    command: click.Command,
    sample_get_value: Optional[Callable[[click.Option], Optional[str]]] = None,
    sample_hidden: Set[str] = set()
) -> str:
    sample_hidden = sample_hidden | {'config', 'config_sample'}

    def collect_options(cmd: click.Command, seen: Set[str] = set()) -> Iterator[click.Option]:
        for p in cmd.params:
            if not isinstance(p, click.Option):
                continue
            if p.hidden or p.name in sample_hidden or p.name in seen:
                continue
            seen.add(p.name)
            yield p

        if isinstance(cmd, click.Group):
            for c in cmd.commands.values():
                yield from collect_options(c, seen=seen)

    def sample_value(opt: click.Option):
        if sample_get_value:
            value = sample_get_value(opt)
            if value is not None:
                return value

        if isinstance(opt.default, (int, str)):
            return opt.default
        elif isinstance(opt.default, pathlib.Path):
            return str(opt.default)
        else:
            return opt.make_metavar()

    def sample_yaml(opt: click.Option):
        sample = ""

        if opt.help:
            sample += "\n".join(f"# {line}" for line in opt.help.splitlines()) + "\n"

        sample += yaml.safe_dump({opt.name: sample_value(opt)}, default_flow_style=False)
        return sample

    return "\n".join(sample_yaml(opt) for opt in collect_options(command))
