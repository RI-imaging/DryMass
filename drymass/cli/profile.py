import argparse
import pathlib
import shutil

import appdirs


APP_DIR = pathlib.Path(appdirs.user_config_dir(appname="drymass"))


def cli_profile(args=None):
    if args is None:
        parser = profile_parser()
        args = parser.parse_args()
    cmd = args.subparser_name
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if cmd in [None, "list"]:
        # default to listing all profiles
        profiles = get_profiles()
        if profiles:
            print("Available profiles:")
            for p in profiles:
                name = p.name.split("_", 1)[1][:-4]
                print(" - {}: {}".format(name, p))
        else:
            print("No profiles in local library.")
    elif cmd == "add":
        loc_path = APP_DIR / "profile_{}.cfg".format(args.name)
        if loc_path.exists():
            raise OSError("Profile '{}' already exists!".format(args.name))
        shutil.copy(args.path, loc_path)
    elif cmd == "remove":
        loc_path = APP_DIR / "profile_{}.cfg".format(args.name)
        if loc_path.exists():
            loc_path.unlink()
        else:
            raise OSError("Profile '{}' does not exist!".format(args.name))
    elif cmd == "export":
        paths = get_profiles()
        out_path = pathlib.Path(args.path)
        out_path.mkdir(parents=True, exist_ok=True)
        for p in paths:
            shutil.copy(p, out_path)
    else:
        raise ValueError("Invalid command '{}'!".format(cmd))


def get_profiles():
    """Return the paths to all profiles in the local library"""
    paths = APP_DIR.glob("profile_*")
    return sorted(paths)


def get_profile_path(name):
    """Convenience function for obtaining a profile path

    If `name` is a path to a profile file, then this path is
    returned. If `name` is a name in the local profile library,
    then the path to that profile is returned.
    """
    path = pathlib.Path(name)
    if not path.exists():
        # name from local library
        path = APP_DIR / "profile_{}.cfg".format(name)
    return path


def profile_parser():
    parser = argparse.ArgumentParser(
        description="Management of DryMass profiles. "
                    "Profiles are just drymass.cfg files that contain "
                    "user-defined default values. Profiles are stored "
                    "in a local library located in the user's configuration "
                    "directory.")
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Run `dm_profile subcommand --help` for "
        "more information.",
        dest='subparser_name')

    t_add = "adds a new profile to the local library"
    p_add = subparsers.add_parser("add", help=t_add, description=t_add)
    p_add.add_argument("name", type=str, help="profile name")
    p_add.add_argument("path", type=str, help="path to drymass.cfg")

    t_rem = "removes a profile from the local library"
    p_rem = subparsers.add_parser("remove", help=t_rem, description=t_rem)
    p_rem.add_argument("name", type=str, help="profile name")

    t_list = "list all profiles in the local library"
    subparsers.add_parser("list", help=t_list, description=t_list)

    t_exp = "export all profile in the local library"
    p_exp = subparsers.add_parser("export", help=t_exp, description=t_exp)
    p_exp.add_argument("path", type=str, help="export path")

    return parser
