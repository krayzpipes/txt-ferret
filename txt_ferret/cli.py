import sys

import click
from loguru import logger

from ._config import load_config, save_config
from .core import TxtFerret


def _get_settings_dict(*args):
    pass

@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--no-tokenize", "-nt", is_flag=True,
    help="When set, the output from the scan will not be tokenized."
)
@click.option(
    "--log-level", "-l", default="INFO",
    help="Log level (cautious of file size for debug): INFO, WARNING, ERROR, DEBUG",
)
@click.option(
    "--summarize", "-s", is_flag=True,
    help="Summarize output",
)
@click.option(
    "--output-file", "-o", default=None,
    help="Write output to file specified by this switch.",
)
@click.option(
    "--config-file", "-c", default=None,
    help="Load user-defined config file."
)
@click.option(
    "--config-override", "-co", is_flag=True,
    help="Delete default filters and only use user-defined filters from config file.",
)
@click.option(
    "--delimiter", "-d", default="",
    help="Delimiter to use for field parsing instead of line parsing.",
)
@click.argument("file_name")
def scan(**cli_kwargs):
    # Code to run scan
    set_logger(**cli_kwargs)
    ferret = TxtFerret(**cli_kwargs)
    ferret.scan_file()


@click.command()
@click.argument("file_name")
def dump_config(file_name):
    # Dump config code
    config = load_config()
    save_config(config, file_name)

cli.add_command(scan)
cli.add_command(dump_config)


def set_logger(**cli_kwargs):
    """Customizes log output and adds output file sync if requested."""

    log_config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": "<lvl>{time:YYYY:MM:DD-HH:mm:ss:ZZ} {message}</lvl>",
                "level": cli_kwargs["log_level"],
            }
        ]
    }

    output_file = cli_kwargs["output_file"]

    if output_file is not None:
        output_sink = {
            "sink": output_file,
            "serialize": False,
            "format": "{time:YYYY:MM:DD-HH:mm:ss:ZZ} {message}",
            "level": cli_kwargs["log_level"]
        }
        log_config["handlers"].append(output_sink)

    logger.configure(**log_config)

