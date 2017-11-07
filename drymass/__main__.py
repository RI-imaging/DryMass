import argparse
import io
import os
import pathlib
from PIL import Image

import numpy as np
import qpimage
from skimage.external import tifffile

from .__init__ import analyze_sphere
from .__init__ import convert
from .__init__ import extract_roi
from . import config_file
from . import definitions
from . import plot
from ._version import version


OUTPUT_SUFFIX = "_dm"
FILE_SENSOR_WITH_ROI_IMAGE = "sensor_roi_images.tif"


def cli_analyze_sphere(ret_data=False):
    h5roi, path_out, rmgr, cfg = cli_extract_roi(ret_data=True)
    print("Sphere analysis... ", end="", flush=True)
    analyze_sphere(h5roiseries=h5roi,
                   dir_out=path_out,
                   n0=1.37,
                   r0=cfg["specimen"]["size um"] / 2 * 1e-6,
                   method=cfg["sphere"]["method"],
                   model=cfg["sphere"]["model"],
                   alpha=cfg["sphere"]["refraction increment"],
                   rad_fact=cfg["sphere"]["radial inclusion factor"],
                   )
    print("Done.")

def cli_convert(ret_data=False):
    print("DryMass version {}".format(version))
    parser = argparse.ArgumentParser(
        description='DryMass raw data conversion.')
    parser.add_argument('path', metavar='path', type=str,
                        help='Data path')
    args = parser.parse_args()
    path_in = pathlib.Path(args.path).resolve()
    print("Input:  {}".format(path_in))
    path_out = setup_dirout(path_in)
    print("Output: {}".format(path_out))
    cfg = user_complete_config_meta(path_out)
    print("Ascertain sensor data... ", end="", flush=True)
    meta_data = {"pixel size": cfg["meta"]["pixel size um"] * 1e-6,
                 "wavelength": cfg["meta"]["wavelength nm"] * 1e-9,
                 "medium index": cfg["meta"]["medium index"],
                 }
    h5series = convert(path_in=args.path,
                       dir_out=path_out,
                       meta_data=meta_data)
    print("Done.")
    if ret_data:
        return path_out, h5series, cfg


def cli_extract_roi(ret_data=False):
    path_out, h5series, cfg = cli_convert(ret_data=True)
    print("Ascertain ROI data... ", end="", flush=True)
    h5roi, rmgr = extract_roi(
        h5series=h5series,
        dir_out=path_out,
        size_m=cfg["specimen"]["size um"] * 1e-6,
        size_var=cfg["roi"]["size variation"],
        max_ecc=cfg["roi"]["eccentricity max"],
        dist_border=cfg["roi"]["dist border"],
        pad_border=cfg["roi"]["pad border"],
        exclude_overlap=cfg["roi"]["exclude overlap"],
        bg_amp_offset=cfg["bg"]["amplitude offset"],
        bg_amp_profile=cfg["bg"]["amplitude profile"],
        bg_amp_border_px=cfg["bg"]["amplitude border perc"],
        bg_amp_border_perc=cfg["bg"]["amplitude border px"],
        bg_pha_offset=cfg["bg"]["phase offset"],
        bg_pha_profile=cfg["bg"]["phase profile"],
        bg_pha_border_px=cfg["bg"]["phase border perc"],
        bg_pha_border_perc=cfg["bg"]["phase border px"],
        ret_roimgr=True,
    )
    print("Done.")
    if cfg["output"]["roi images"]:
        print("Plot detected ROIs... ", end="", flush=True)
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
        return h5roi, path_out, rmgr, cfg


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
            val = input("Please enter '{}' ({}): ".format(key, description))
            cfg.set_value("meta", key, val)
    return cfg
