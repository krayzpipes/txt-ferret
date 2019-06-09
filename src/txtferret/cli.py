from datetime import datetime
import multiprocessing as mp
import pathlib
import sys

import click
from loguru import logger

from ._config import load_config, save_config
from .core import TxtFerret


def set_logger(**cli_kwargs):
    """Configured logger.

    Sets up handlers for stdout and for output file if the user
    passed an output file name.

    Sets up message format and level.

    :param cli_kwargs: The key/value pairs depicting the CLI arguments
        given by the user.
    """
    # Setup basic log config including a sink for stdout.
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

    # If output file is defined, create a sink for it and add it to
    # the logger.
    if output_file is not None:
        output_sink = {
            "sink": output_file,
            "serialize": False,
            "format": "{time:YYYY:MM:DD-HH:mm:ss:ZZ} {message}",
            "level": cli_kwargs["log_level"],
        }
        log_config["handlers"].append(output_sink)

    logger.configure(**log_config)


def prep_config(**cli_kwargs):
    file_name = cli_kwargs["config_file"]
    override = cli_kwargs["config_override"]
    config = load_config(yaml_file=file_name, default_override=override)
    config["cli_kwargs"] = {**cli_kwargs}
    return config


def bootstrap(config):
    ferret = TxtFerret(config)
    ferret.scan_file()
    return ferret.summary()


def get_files_from_dir(directory=None):
    path = pathlib.Path(directory)
    file_names = [item.name for item in path.iterdir() if item.is_file()]
    return file_names


def get_totals(results=None):
    _total_failures = 0
    _total_passes = 0

    for result in results:
        _total_failures += result.get("failures")
        _total_passes += result.get("passed")

    return _total_failures, _total_passes


def log_summary(result=None, file_count=None):
    failures = result.get("failures")
    passed = result.get("passed")
    logger.info("SUMMARY:")
    logger.info(f"  - Scanned {file_count} file(s).")
    logger.info(f"  - Matched regex, failed sanity: {failures}")
    logger.info(f"  - Matched regex, passed sanity: {passed}")

    seconds = result.get("time")
    minutes = seconds // 60

    logger.info(f"Finished in {seconds} seconds (~{minutes} minutes).")


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--no-tokenize",
    "-nt",
    is_flag=True,
    help="When set, the output from the scan will not be tokenized.",
)
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    help="Log level (cautious of file size for debug): INFO, WARNING, ERROR, DEBUG",
)
@click.option("--summarize", "-s", is_flag=True, help="Summarize output")
@click.option(
    "--output-file",
    "-o",
    default=None,
    help="Write output to file specified by this switch.",
)
@click.option(
    "--config-file", "-c", default=None, help="Load user-defined config file."
)
@click.option(
    "--config-override",
    "-co",
    is_flag=True,
    help="Delete default filters and only use user-defined filters from config file.",
)
@click.option(
    "--delimiter",
    "-d",
    default="",
    help="Delimiter to use for field parsing instead of line parsing.",
)
@click.option(
    "--bulk",
    "-b",
    is_flag=True,
    help="Scan multiple files in a directory.",
)
@click.argument("file_name")
def scan(**cli_kwargs):
    """Kicks off scanning of user-defined file(s)."""

    config = prep_config(**cli_kwargs)

    set_logger(**cli_kwargs)

    if not cli_kwargs["bulk"]:

        result = bootstrap(config)

        log_summary(result=result, file_count=1)

    else:

        start = datetime.now()

        file_names = get_files_from_dir(directory=cli_kwargs["file_name"])
        configs = []

        # Generate a config for each file name which can be passed to
        # multiprocessing...
        for file_ in file_names:
            temp_config = {**config}
            temp_config["cli_kwargs"]["file_name"] = file_
            configs.append(temp_config)

        # Devy out the work to available CPUs
        cpus = mp.cpu_count()
        with mp.Pool(cpus) as p:
            results = p.map(bootstrap, configs)

        end = datetime.now()

        total_failures, total_passes = get_totals(results)

        total_scanned = len(results)

        delta = start - end

        final_result = {
            "failures": total_failures,
            "passes": total_passes,
            "time": delta.seconds,
        }

        log_summary(result=final_result, file_count=total_scanned)


@click.command()
@click.argument("file_name")
def dump_config(file_name):
    """Writes default config to user-specified file location."""
    config = load_config()
    save_config(config, file_name)


cli.add_command(scan)
cli.add_command(dump_config)
