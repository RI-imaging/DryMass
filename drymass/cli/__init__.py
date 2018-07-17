import io
import numbers
from os import fspath
import pathlib
import sys

import numpy as np
from PIL import Image
import qpimage
from skimage.external import tifffile

from . import config
from . import dialog
from . import plot

from ..anasphere import analyze_sphere
from ..converter import convert
from ..extractroi import extract_roi

#: Matplotlib images of sensor data with labeled ROI (TIFF)
FILE_SENSOR_WITH_ROI_IMAGE = "sensor_roi_images.tif"
#: Matplotlib images of sphere analysis (TIFF)
FILE_SPHERE_ANALYSIS_IMAGE = "sphere_{}_{}_images.tif"


def cli_analyze_sphere(path=None, ret_data=False):
    """Perform sphere analysis"""
    path_in, path_out = dialog.main(path=path,
                                    req_meta=["medium index",
                                              "pixel size um",
                                              "wavelength nm"])
    cfg = config.ConfigFile(path_out)
    h5roi = cli_extract_roi(path=path_in, ret_data=True)
    print("Performing sphere analysis... ", end="", flush=True)
    # canny edge detection parameters
    edgekw = {
        "clip_rmin": cfg["sphere"]["edge clip radius min"],
        "clip_rmax": cfg["sphere"]["edge clip radius max"],
        "mult_coarse": cfg["sphere"]["edge coarse"],
        "mult_fine": cfg["sphere"]["edge fine"],
        "maxiter": cfg["sphere"]["edge iter"],
    }
    # image fitting parameters
    imagekw = {
        "crel": cfg["sphere"]["image fit range position"],
        "rrel": cfg["sphere"]["image fit range radius"],
        "nrel": cfg["sphere"]["image fit range refractive index"],
        "fix_pha_offset": cfg["sphere"]["image fix phase offset"],
        "max_iter": cfg["sphere"]["image iter"],
        "stop_dc": cfg["sphere"]["image stop delta position"],
        "stop_dr": cfg["sphere"]["image stop delta radius"],
        "stop_dn": cfg["sphere"]["image stop delta refractive index"],
        "verbose": cfg["sphere"]["image verbosity"],
    }
    h5sim, changed = analyze_sphere(
        h5roi=h5roi,
        dir_out=path_out,
        r0=cfg["specimen"]["size um"] / 2 * 1e-6,
        method=cfg["sphere"]["method"],
        model=cfg["sphere"]["model"],
        alpha=cfg["sphere"]["refraction increment"],
        rad_fact=cfg["sphere"]["radial inclusion factor"],
        edgekw=edgekw,
        imagekw=imagekw,
        ret_changed=True,
        )

    print("Done.")

    if changed and cfg["output"]["sphere images"]:
        print("Plotting sphere images... ", end="", flush=True)
        tifout = path_out / FILE_SPHERE_ANALYSIS_IMAGE.format(
            cfg["sphere"]["method"],
            cfg["sphere"]["model"]
        )
        # plot h5series and rmgr with matplotlib
        with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qps_roi, \
                qpimage.QPSeries(h5file=h5sim, h5mode="r") as qps_sim, \
                tifffile.TiffWriter(fspath(tifout), imagej=True) as tf:
            for ii in range(len(qps_roi)):
                qpi_real = qps_roi[ii]
                qpi_sim = qps_sim[ii]
                assert qpi_real["identifier"] in qpi_sim["identifier"]
                imio = io.BytesIO()
                plot.plot_qpi_sphere(qpi_real=qpi_real,
                                     qpi_sim=qpi_sim,
                                     path=imio,
                                     simtype=cfg["sphere"]["model"])
                imio.seek(0)
                imdat = np.array(Image.open(imio))
                tf.save(imdat)
        print("Done")


def cli_convert(path=None, ret_data=False):
    """Convert input data to QPSeries data"""
    path_in, path_out = dialog.main(path=path,
                                    req_meta=["pixel size um",
                                              "wavelength nm"])
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


def cli_extract_roi(path=None, ret_data=False):
    """Extract regions of interest"""
    path_in, path_out = dialog.main(path=path)
    # cli_convert will ask for the required meta data
    h5series = cli_convert(path=path_in, ret_data=True)
    # get the configuration after cli_convert was run
    cfg = config.ConfigFile(path_out)
    print("Extracting ROIs... ", end="", flush=True)
    if cfg["bg"]["enabled"]:
        bg_amp_kw = {"fit_offset": cfg["bg"]["amplitude offset"],
                     "fit_profile": cfg["bg"]["amplitude profile"],
                     "border_perc": cfg["bg"]["amplitude border perc"],
                     "border_px": cfg["bg"]["amplitude border px"],
                     }
        bg_pha_kw = {"fit_offset": cfg["bg"]["phase offset"],
                     "fit_profile": cfg["bg"]["phase profile"],
                     "border_perc": cfg["bg"]["phase border perc"],
                     "border_px": cfg["bg"]["phase border px"],
                     }
        # compatibility for drymass.cfg files created with
        # drymass < 0.1.3 (API changed in qpimage 0.1.6).
        if bg_amp_kw["fit_profile"] == "ramp":
            bg_amp_kw["fit_profile"] = "tilt"
        if bg_pha_kw["fit_profile"] == "ramp":
            bg_pha_kw["fit_profile"] = "tilt"
    else:
        bg_amp_kw = None
        bg_pha_kw = None

    h5roi, rmgr, changed = extract_roi(
        h5series=h5series,
        dir_out=path_out,
        size_m=cfg["specimen"]["size um"] * 1e-6,
        size_var=cfg["roi"]["size variation"],
        max_ecc=cfg["roi"]["eccentricity max"],
        dist_border=cfg["roi"]["dist border px"],
        pad_border=cfg["roi"]["pad border px"],
        exclude_overlap=cfg["roi"]["exclude overlap px"],
        bg_amp_kw=bg_amp_kw,
        bg_amp_bin=cfg["bg"]["amplitude binary threshold"],
        bg_pha_kw=bg_pha_kw,
        bg_pha_bin=cfg["bg"]["phase binary threshold"],
        search_enabled=cfg["roi"]["enabled"],
        ret_roimgr=True,
        ret_changed=True,
    )
    if changed:
        print("Done.")
    else:
        print("Reusing.")
    if len(rmgr) == 0:
        print("No ROIs could be found!\n"
              + "Please try editing '{}':\n".format(cfg.path)
              + "- correct specimen size "
              + "({})\n".format(strpar(cfg, "specimen", "size um"))
              + "- increase allowed size variation "
              + "({})\n".format(strpar(cfg, "roi", "size variation"))
              + "- increase maximum allowed eccentricity "
              + "({})\n".format(strpar(cfg, "roi", "eccentricity max"))
              + "- reduce minimum distance to image border in pixels "
              + "({})\n".format(strpar(cfg, "roi", "dist border px"))
              + "- reduce minimum distance inbetween ROIs "
              + "({})".format(strpar(cfg, "roi", "exclude overlap px"))
              )
        sys.exit(1)

    if changed and cfg["output"]["roi images"]:
        print("Plotting detected ROIs... ", end="", flush=True)
        tifout = path_out / FILE_SENSOR_WITH_ROI_IMAGE
        # plot h5series and rmgr with matplotlib
        with qpimage.QPSeries(h5file=h5series, h5mode="r") as qps, \
                tifffile.TiffWriter(fspath(tifout), imagej=True) as tf:
            for ii in range(len(qps)):
                rois = rmgr.get_from_image_index(ii)
                imio = io.BytesIO()
                plot.plot_qpi_phase(qps[ii],
                                    rois=rois,
                                    path=imio)
                imio.seek(0)
                imdat = np.array(Image.open(imio))
                tf.save(imdat)
        print("Done")

    if ret_data:
        return h5roi


def parse_bg_value(bg, reldir):
    """Determine the background to use from the configuration key"""
    if bg == "none":
        bg = None
    elif isinstance(bg, numbers.Integral):
        # indexing starts at 1
        bg -= 1
    elif isinstance(bg, str):
        # can be a file name relative to the input directory
        # or an absolute path.
        reldir = pathlib.Path(reldir)
        path = reldir / bg
        if not path.exists():
            path = pathlib.Path(bg)
        bg = path
    return bg


def strpar(cfg, section, key):
    """String representation of a section/key combination"""
    return "[{}] {} = {}".format(section, key, cfg[section][key])
