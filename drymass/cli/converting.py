import pathlib

from ..converter import convert

from . import config
from . import dialog


def cli_convert(path=None, ret_data=False, profile=None):
    """Convert input data to QPSeries data"""
    description = "Convert raw quantitative phase microscopy data to " \
                  + "the qpimage file format for further analysis in " \
                  + "DryMass."
    path_in, path_out = dialog.main(path=path,
                                    req_meta=["pixel size um",
                                              "wavelength nm"],
                                    description=description,
                                    profile=profile)
    if isinstance(path_in, list):
        # recursive analysis
        for ii, pi in enumerate(path_in):
            print("Analyzing dataset {}/{}.".format(ii+1, len(path_in)))
            cli_convert(path=pi)
        # nothing else to do
        return
    cfg = config.ConfigFile(path_out)
    print("Converting input data... ", end="", flush=True)
    meta_data = {"pixel size": cfg["meta"]["pixel size um"] * 1e-6,
                 "wavelength": cfg["meta"]["wavelength nm"] * 1e-9,
                 "medium index": cfg["meta"]["medium index"],
                 }

    holo_kw = {"filter_name": cfg["holo"]["filter name"],
               "filter_size": cfg["holo"]["filter size"],
               "sideband": cfg["holo"]["sideband"],
               }

    bg_data_amp = parse_bg_value(cfg["bg"]["amplitude data"],
                                 reldir=path_in.parent)
    bg_data_pha = parse_bg_value(cfg["bg"]["phase data"],
                                 reldir=path_in.parent)

    h5series, ds, changed = convert(path_in=path_in,
                                    dir_out=path_out,
                                    meta_data=meta_data,
                                    holo_kw=holo_kw,
                                    bg_data_amp=bg_data_amp,
                                    bg_data_pha=bg_data_pha,
                                    write_tif=cfg["output"]["sensor tif data"],
                                    ret_dataset=True,
                                    ret_changed=True,
                                    )
    if "hologram" not in ds.storage_type:
        # remove "holo" section from configuration
        cfg.remove_section("holo")
    if changed:
        print("Done.")
    else:
        print("Reusing.")
    if ret_data:
        return h5series


def parse_bg_value(bg, reldir):
    """Determine the background to use from the configuration key"""
    if isinstance(bg, str):
        # can be a file name relative to the input directory
        # or an absolute path.
        reldir = pathlib.Path(reldir)
        path = reldir / bg
        if not path.exists():
            path = pathlib.Path(bg)
        bg = path
    return bg
