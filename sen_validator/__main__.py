import datetime
import importlib
import json
import os
from pathlib import Path

import click
import pytest


@click.group()
def cli():
    pass


@cli.command(name="ingress")
@click.option("--filepath", "-f")
def ingress():
    pass
