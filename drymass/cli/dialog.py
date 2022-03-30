import argparse
import functools
import pathlib

import qpformat

from .._version import version

from . import definitions
from . import config
from .profile import get_profile_path

#: DryMass analysis output suffix (appended to data path)
OUTPUT_SUFFIX = "_dm"

META_MAPPER = {"medium index": ("medium index", 1),
               "pixel size um": ("pixel size", 1e6),
               "wavelength nm": ("wavelength", 1e9),
               }


@functools.lru_cache(maxsize=32)
def input_setting(path, section, key, value=None):
    """Ask the user for a configuration key"""
    cfg = config.ConfigFile(path)
    sec = cfg[section]
    description = definitions.config[section][key][2]
    val_cfg = sec.get(key, None)
    if val_cfg is not None:
        # values from configuration have higher priority
        value = val_cfg
    else:
        if value is None:
            default = ""
        else:
            default = f" [{value}]"
        resp = input(f"Please enter '{description}'{default}: ")
        # If the user presses return, then `resp` is empty.
        value = resp.strip() or value
    cfg.set_value("meta", key, value)


def main(path=None, req_meta=None, description="DryMass analysis.",
         profile=None, recursive=False):
    """Main user dialog with optional "meta" kwargs required

    Parameters
    ----------
    path: str, pathlib.Path, or None
        Path to the measurement data. If set to `None`, the
        command-line will be parsed.
    req_meta: list of str
        Keyword arguments of the [meta] section in drymass.cfg that
        are required by the current task.
    description: str
        Description of the current task. The description is
        displayed when the user executes a console_script
        entry-point with the `--help` argument.
    profile: str, pathlib.Path, or None
        A path to a 'drymass.cfg' file or a name of a profile in
        the local library (see :mod:`drymass.cli.profile`). If set
        to `None`, the default profile is used and the user is asked
        for missing values.
    recursive: bool
        Perform recursive search in `path`. If `path` is None, then
        `recursive` must be False. Instead, the `recursive` argument
        should be set via the command line.

    Returns
    -------
    path_in: pathlib.Path or list of pathlib.Path
        The measurement path. If a recursive search is performed
        (see `recursive` parameter above), then a list of the
        measurement paths is returned.
    path_out: pathlib.Path or None
        The output path, i.e. the path with `_dm` appended. If a
        recursive search is performed, `path_out` is set to None.
    """
    # get directories
    if req_meta is None:
        req_meta = []
    if path is None:
        if recursive:
            msg = "'recursive' must not be set when 'path' is 'None'!"
            raise ValueError(msg)
        path_in, profile, recursive = parse(description)
    else:
        path_in = pathlib.Path(path).resolve()
    if recursive:
        # perform recursive analysis
        # path_in is now a list
        print("Recursing into directory tree... ", end="", flush=True)
        path_list = recursive_search(path=path_in)
        if not path_list:
            msg = "Recursive search did not find any series data in " \
                  + "'{}'!".format(path_in)
            raise IOError(msg)
        print("Done.")
        # path_out is set to None when recursive search is used
        path_out = None
        for ii, pi in enumerate(path_list):
            # request necessary metadata for each measurement
            # before the actual analysis is done.
            print("Input {}/{}: {}".format(ii+1, len(path_list), pi))
            main(path=pi, profile=profile, req_meta=req_meta)
        path_in = path_list
    else:
        # verify data set
        try:
            ds = qpformat.load_data(path_in)
        except qpformat.BadFileFormatError as e:
            msg = "For a recursive search, please pass the " \
                  + "command line parameter '-r'."
            e.args = ("; ".join(list(e.args) + [msg]),)
            raise
        else:
            # perform regular analysis
            path_out = path_in.with_name(path_in.name + OUTPUT_SUFFIX)
            path_out.mkdir(exist_ok=True)
            if path is None:
                # print directories only if taken from command line
                print("Input:  {}".format(path_in))
                print("Output: {}".format(path_out))
            if profile:
                # use a user-specified profile
                ppath = get_profile_path(profile)
                cfg_profile = config.ConfigFile(ppath)
                cfg_out = config.ConfigFile(path_out)
                cfg_out.update(cfg_profile)
            # get known meta data kwargs from dataset
            transfer_meta_data(path_in, path_out)
            # user input missing meta data keyword values
            meta = ds.get_metadata(0)
            for mm in sorted(req_meta):
                key, mult = META_MAPPER[mm]
                if key in meta:
                    value = meta[key] * mult
                else:
                    value = None
                input_setting(path=path_out,
                              section="meta",
                              key=mm,
                              value=value)
    return path_in, path_out


@functools.lru_cache(maxsize=32)  # cached to avoid multiple prints
def parse(description="DryMass analysis."):
    """Obtain the input data set path by parsing the command line"""
    print("DryMass version {}".format(version))
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('path', metavar='path', nargs='+', type=str,
                        help='Data path')
    parser.add_argument("-p", "--profile",
                        help="Use an existing profile for data analysis. "
                             + "The profile can be either a path to a "
                             + "'drymass.cfg' file or profile in the "
                             + "local library (see `dm_profile` command).",
                        default=None,
                        type=str)
    parser.add_argument("-r", "--recursive",
                        help="Recursively search for measurement data "
                             + "and run DryMass separately for each folder.",
                        default=False,
                        action='store_true')
    args = parser.parse_args()
    # Workaround: We use nargs='+' and join the input to support white
    # spaces in path names.
    jpath = " ".join(args.path)
    path_in = pathlib.Path(jpath).resolve()
    if args.recursive and not path_in.is_dir():
        msg = "Given path must be directory in recursive mode; " \
              + "got '{}'!".format(path_in)
        raise ValueError(msg)
    return path_in, args.profile, args.recursive


def recursive_search(path):
    """Perform recursive search for supported measurements"""
    path = pathlib.Path(path).resolve()
    paths_datasets = []
    # Get all candidates
    paths_with_dm = sorted(list(path.rglob("*")) + [path])
    # Exclude all files/directories that are in a results directory
    cands_noresults = []
    for c1 in paths_with_dm:
        tocheck = list(c1.parents)
        if c1.is_dir():
            tocheck.append(c1)
        for pp in tocheck:
            if pp.name and pp.name.endswith("_dm"):
                break
        else:
            cands_noresults.append(c1)
    # Try to open all series files with qpformat
    ignore_folders = []
    for c2 in cands_noresults:
        if c2.is_file():
            try:
                ds = qpformat.load_data(path=c2)
            except qpformat.file_formats.UnknownFileFormatError:
                pass
            else:
                if ds.is_series:
                    # The same thing that applies to SeriesFolder also
                    # applies to SeriesData in general.
                    paths_datasets.append(c2)
                    # Note that we completely ignore all SingleData
                    # file formats here.
                    ignore_folders.append(c2.parent)
    # Determine all directory-based measurements (SeriesFolder format)
    for c2 in cands_noresults:
        if c2.is_dir() and c2 not in ignore_folders:
            try:
                ds = qpformat.load_data(path=c2, fmt="SeriesFolder")
            except (NotImplementedError, qpformat.BadFileFormatError):
                pass
            else:
                if len(ds) > 1:
                    paths_datasets.append(c2)
    return sorted(paths_datasets)


def transfer_meta_data(path_in, path_out):
    """Read input metadata and write it to the configuration file"""
    ds = qpformat.load_data(path=path_in)
    cfg = config.ConfigFile(path_out)
    sec = cfg["meta"]
    for key in sorted(META_MAPPER):
        dskey, mult = META_MAPPER[key]
        if (key not in sec or sec[key] is None) and dskey in ds.meta_data:
            cfg.set_value("meta", key, ds.meta_data[dskey] * mult)
