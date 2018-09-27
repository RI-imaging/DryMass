import argparse
import functools
import pathlib

import numpy as np
import qpformat

from .._version import version

from . import definitions
from . import config

#: DryMass analysis output suffix (appended to data path)
OUTPUT_SUFFIX = "_dm"

META_MAPPER = {"medium index": ("medium index", 1),
               "pixel size um": ("pixel size", 1e6),
               "wavelength nm": ("wavelength", 1e9),
               }


@functools.lru_cache(maxsize=32)
def input_setting(path, section, key):
    """Ask the user for a configuration key"""
    cfg = config.ConfigFile(path)
    sec = cfg[section]
    description = definitions.config[section][key][2]
    if key not in sec or np.isnan(sec[key]):
        val = input("Please enter '{}' ({}): ".format(key, description))
        cfg.set_value("meta", key, val)


def main(path=None, req_meta=[]):
    """Main user dialog with optional "meta" kwargs required"""
    # get directories
    if path is None:
        path_in = parse().resolve()
    else:
        path_in = pathlib.Path(path).resolve()
    path_out = path_in.with_name(path_in.name + OUTPUT_SUFFIX)
    path_out.mkdir(exist_ok=True)
    # print directories (wrapped with functools so only executed once)
    print_info(path_in, path_out)
    # get known meta data kwargs from dataset
    transfer_meta_data(path_in, path_out)
    # user input missing meta data keyword values
    for mm in sorted(req_meta):
        input_setting(path=path_out,
                      section="meta",
                      key=mm)
    return path_in, path_out


@functools.lru_cache(maxsize=32)  # cached to avoid multiple prints
def parse():
    """Obtain the input data set path by parsing the command line"""
    print("DryMass version {}".format(version))
    parser = argparse.ArgumentParser(description='DryMass QPI analysis.')
    parser.add_argument('path', metavar='path', nargs='+', type=str,
                        help='Data path')
    args = parser.parse_args()
    # Workaround: We use nargs='+' and join the input to support white
    # spaces in path names.
    jpath = " ".join(args.path)
    path_in = pathlib.Path(jpath).resolve()
    return path_in


def transfer_meta_data(path_in, path_out):
    """Read input meta data and write it to the configuration file"""
    ds = qpformat.load_data(path=path_in)
    cfg = config.ConfigFile(path_out)
    sec = cfg["meta"]
    for key in sorted(META_MAPPER):
        dskey, mult = META_MAPPER[key]
        if (key not in sec or np.isnan(sec[key])) and dskey in ds.meta_data:
            cfg.set_value("meta", key, ds.meta_data[dskey] * mult)


@functools.lru_cache(maxsize=32)  # cached to avoid multiple prints
def print_info(path_in, path_out):
    """Print input and output paths"""
    print("Input:  {}".format(path_in))
    print("Output: {}".format(path_out))
