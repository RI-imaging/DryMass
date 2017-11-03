import argparse
import os
import pathlib

import numpy as np

from . import config_file
from . import convert
from . import definitions


OUTPUT_SUFFIX = "_dm"


def cli_convert():
    parser = argparse.ArgumentParser(
        description='DryMass raw data conversion.')
    parser.add_argument('path', metavar='path', type=str,
                        help='Data path')
    args = parser.parse_args()

    path_out = setup_dirout(args.path)
    cfg = user_complete_config_meta(path_out)
    convert.convert(path_in=args.path,
                    path_out=path_out,
                    meta_data=cfg["meta"])


def setup_dirout(path_in):
    path_in = pathlib.Path(path_in).resolve()
    if not path_in.exists():
        raise ValueError("Path '{}' does not exist!".format(path_in))
    path_out = pathlib.Path(str(path_in) + OUTPUT_SUFFIX)
    if not path_out.exists():
        os.mkdir(str(path_out))
    return path_out


def user_complete_config_meta(path):
    cfg = config_file.ConfigFile(path)
    meta = cfg["meta"]
    for key in definitions.config["meta"]:
        description = definitions.config["meta"][key][2]
        if key not in meta or np.isnan(meta[key]):
            val = input("Please enter '{}' ({}):".format(key, description))
            cfg.set_value("meta", key, val)
    return cfg
