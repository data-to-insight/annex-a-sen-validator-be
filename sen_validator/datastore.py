import logging
import os
from copy import copy
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from pandas import DataFrame

# logger = logging.getLogger(__name__)

# def create_datastore(data: Dict[str, Any], metadata: Dict[str, Any]):
#     """
#     Returns a dictionary with keys for
#     - Every table name in config.py
#     - Every table name again, with the suffix '_last', if last years data was uploaded.
#     - A 'metadata' key, which links to a nested dictionary with
#       - 'postcodes' - a postcodes csv, with columns "laua" (LA code), "oseast1m", "osnrth1m" (coordinates) and "pcd" (the postcode)
#       - 'localAuthority' - the code of the local authority (long form)
#       - 'collectionYear' - the collection year string (e.g. '2019/20)

#     :param data: Dict of raw DataFrames by name (from config.py) together with the '_last' data.
#     :param metadata:
#     """

#     logger.info(", ".join(data.keys()))
#     data = copy(data)