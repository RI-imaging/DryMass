import argparse
import functools
import pathlib

import numpy as np

from .._version import version

from . import definitions
from . import config


OUTPUT_SUFFIX = "_dm"


@functools.lru_cache(maxsize=32)
def input_setting(path, section, key):
    cfg = config.ConfigFile(path)
    sec = cfg[section]
    description = definitions.config[section][key][2]
    if key not in sec or np.isnan(sec[key]):
        val = input("Please enter '{}' ({}): ".format(key, description))
        cfg.set_value("meta", key, val)


def main(path=None, req_meta=[]):
    # get directories
    if path is None:
        path_in = parse().resolve()
    else:
        path_in = pathlib.Path(path).resolve()
    path_out = path_in.with_name(path_in.name + OUTPUT_SUFFIX)
    path_out.mkdir(exist_ok=True)
    # print directories (wrapped with functools so only executed once)
    print_info(path_in, path_out)
    # user input meta data keyword values
    for mm in sorted(req_meta):
        input_setting(path=path_out,
                      section="meta",
                      key=mm)
    return path_in, path_out


@functools.lru_cache(maxsize=32)
def parse():
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


@functools.lru_cache(maxsize=32)
def print_info(path_in, path_out):
    print("Input:  {}".format(path_in))
    print("Output: {}".format(path_out))
