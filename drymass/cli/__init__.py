import argparse
import functools
import io
import os
import pathlib
import sys

import numpy as np
from PIL import Image
import qpimage
from skimage.external import tifffile

from ..anasphere import analyze_sphere
from ..converter import convert
from ..extractroi import extract_roi
from .. import config_file
from .. import definitions
from .. import plot
from .._version import version


OUTPUT_SUFFIX = "_dm"
FILE_SENSOR_WITH_ROI_IMAGE = "sensor_roi_images.tif"
FILE_SPHERE_ANALYSIS_IMAGE = "sphere_{}_{}_images.tif"


def cli_analyze_sphere(ret_data=False):
    path_out = setup_analysis()[1]
    cfg = user_complete_config_meta(path_out,
                                    meta_keys=["medium index",
                                               "pixel size um",
                                               "wavelength nm"])
    h5roi = cli_extract_roi(ret_data=True)
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
    h5sim = analyze_sphere(h5roiseries=h5roi,
                           dir_out=path_out,
                           r0=cfg["specimen"]["size um"] / 2 * 1e-6,
                           method=cfg["sphere"]["method"],
                           model=cfg["sphere"]["model"],
                           alpha=cfg["sphere"]["refraction increment"],
                           rad_fact=cfg["sphere"]["radial inclusion factor"],
                           edgekw=edgekw,
                           imagekw=imagekw,
                           )
    print("Done.")

    if cfg["output"]["sphere images"]:
        print("Plotting sphere images... ", end="", flush=True)
        tifout = path_out / FILE_SPHERE_ANALYSIS_IMAGE.format(
            cfg["sphere"]["method"],
            cfg["sphere"]["model"]
        )
        # plot h5series and rmgr with matplotlib
        with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qps_roi, \
                qpimage.QPSeries(h5file=h5sim, h5mode="r") as qps_sim, \
                tifffile.TiffWriter(str(tifout), imagej=True) as tf:
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


def cli_convert(ret_data=False):
    path_in, path_out = setup_analysis()
    cfg = user_complete_config_meta(path_out,
                                    meta_keys=["pixel size um",
                                               "wavelength nm"])
    print("Converting input data... ", end="", flush=True)
    meta_data = {"pixel size": cfg["meta"]["pixel size um"] * 1e-6,
                 "wavelength": cfg["meta"]["wavelength nm"] * 1e-9,
                 "medium index": cfg["meta"]["medium index"],
                 }

    holo_kw = {"filter_name": cfg["holo"]["filter name"],
               "filter_size": cfg["holo"]["filter size"],
               "sideband": cfg["holo"]["sideband"],
               }

    bg_data_amp = cfg["bg"]["amplitude data"]
    bg_data_pha = cfg["bg"]["phase data"]

    if bg_data_amp == "none":
        bg_data_amp = None

    if bg_data_pha == "none":
        bg_data_pha = None

    h5series, ds = convert(path_in=path_in,
                           dir_out=path_out,
                           meta_data=meta_data,
                           holo_kw=holo_kw,
                           bg_data_amp=bg_data_amp,
                           bg_data_pha=bg_data_pha,
                           write_tif=cfg["output"]["sensor tif data"],
                           ret_dataset=True,
                           )
    if "hologram" not in ds.storage_type:
        # remove "holo" section from configuration
        cfg.remove_section("holo")
    print("Done.")
    if ret_data:
        return h5series


def cli_extract_roi(ret_data=False):
    path_out = setup_analysis()[1]
    # cli_convert will ask for the required meta data
    h5series = cli_convert(ret_data=True)
    # get the configuration after cli_convert was run
    cfg = config_file.ConfigFile(path_out)
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
    print("Done.")
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
                tifffile.TiffWriter(str(tifout), imagej=True) as tf:
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


@functools.lru_cache(maxsize=4)
def setup_analysis():
    print("DryMass version {}".format(version))
    parser = argparse.ArgumentParser(description='DryMass QPI analysis.')
    parser.add_argument('path', metavar='path', type=str,
                        help='Data path')
    args = parser.parse_args()
    path_in = pathlib.Path(args.path).resolve()
    if not path_in.exists():
        raise ValueError("Path '{}' does not exist!".format(path_in))
    path_out = pathlib.Path(str(path_in) + OUTPUT_SUFFIX)
    if not path_out.exists():
        os.mkdir(str(path_out))
    print("Input:  {}".format(path_in))
    print("Output: {}".format(path_out))
    return path_in, path_out


def strpar(cfg, section, key):
    return "[{}] {} = {}".format(section, key, cfg[section][key])


def user_complete_config_meta(path, meta_keys):
    cfg = config_file.ConfigFile(path)
    meta = cfg["meta"]
    for key in sorted(meta_keys):
        description = definitions.config["meta"][key][2]
        if key not in meta or np.isnan(meta[key]):
            val = input("Please enter '{}' ({}): ".format(key, description))
            cfg.set_value("meta", key, val)
    return cfg
