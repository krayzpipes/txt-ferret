import click

from ._config import load_config, save_config
from .core import TxtFerret

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
    "--output", "-o",
    help="Write output to file specified by this switch.",
)
@click.argument("file_name")
def scan(file_name, no_tokenize, log_level, summarize):
    # Code to run scan
    ferret = TxtFerret(file_name)

@click.command()
@click.argument("file_name")
def dump_config(file_name):
    # Dump config code
    config = load_config()
    save_config(config, file_name)

cli.add_command(scan)
cli.add_command(dump_config)
