import argparse
import functools
import pathlib
import shutil

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
def input_setting(path, section, key):
    """Ask the user for a configuration key"""
    cfg = config.ConfigFile(path)
    sec = cfg[section]
    description = definitions.config[section][key][2]
    if key not in sec or sec[key] is None:
        val = input("Please enter '{}' ({}): ".format(key, description))
        cfg.set_value("meta", key, val)


def main(path=None, req_meta=[], description="DryMass analysis.",
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
            qpformat.load_data(path_in)
        except qpformat.BadFileFormatError as e:
            msg = "For a recursive search, please pass the " \
                  + "command line parameter '-r'."
            e.args = ("; ".join(list(e.args) + [msg]),)
            raise
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
            shutil.copy(ppath, path_out / config.FILE_CONFIG)
        # get known meta data kwargs from dataset
        transfer_meta_data(path_in, path_out)
        # user input missing meta data keyword values
        for mm in sorted(req_meta):
            input_setting(path=path_out,
                          section="meta",
                          key=mm)
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
    path_in = []
    # Get all candidates
    cands1 = list(path.rglob("*")) + [path]
    # Exclude all directories with the suffix _dm that contain drymass.cfg
    cands2 = []
    for c1 in cands1:
        tocheck = list(c1.parents)
        if c1.is_dir():
            tocheck.append(c1)
        for pp in tocheck:
            if pp.name.endswith("_dm") and (pp / "drymass.cfg").exists():
                break
        else:
            cands2.append(c1)
    # Determine all directory-based measurements (SeriesFolder format)
    for c2 in cands2:
        if c2.is_dir():
            try:
                ds = qpformat.load_data(path=c2, fmt="SeriesFolder")
            except (NotImplementedError, qpformat.BadFileFormatError):
                pass
            else:
                if len(ds) > 1:
                    path_in.append(c2)
    if not path_in:
        # If we have found SeriesFolder measurements, then we probably do not
        # want to analyze any other files lying around, especially
        # because they could be related to background correction.
        # Try to open all the other files with qpformat
        for c2 in cands2:
            if c2.is_file():
                try:
                    ds = qpformat.load_data(path=c2)
                except qpformat.file_formats.UnknownFileFormatError:
                    pass
                else:
                    if ds.is_series:
                        # The same thing that applies to SeriesFolder also
                        # applies to SeriesData in general.
                        path_in.append(c2)
                        # Note that we completely ignore all SingleData
                        # file formats here.
    return sorted(path_in)


def transfer_meta_data(path_in, path_out):
    """Read input meta data and write it to the configuration file"""
    ds = qpformat.load_data(path=path_in)
    cfg = config.ConfigFile(path_out)
    sec = cfg["meta"]
    for key in sorted(META_MAPPER):
        dskey, mult = META_MAPPER[key]
        if (key not in sec or sec[key] is None) and dskey in ds.meta_data:
            cfg.set_value("meta", key, ds.meta_data[dskey] * mult)
