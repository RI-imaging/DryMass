import io
from os import fspath
import sys

import matplotlib.image as mpimg
import qpimage
from skimage.external import tifffile

from ..extractroi import extract_roi

from . import config
from .converting import cli_convert
from . import dialog
from . import plot
from .task_watcher import TaskWatcher


#: Matplotlib images of sensor data with labeled ROI (TIFF)
FILE_SENSOR_WITH_ROI_IMAGE = "sensor_roi_images.tif"


def cli_extract_roi(path=None, ret_data=False, profile=None):
    """Extract regions of interest"""
    description = "Extract reqions of interest in quantitative phase" \
                  + "microscopy data for further analysis in DryMass."
    path_in, path_out = dialog.main(path=path,
                                    description=description,
                                    profile=profile)
    if isinstance(path_in, list):
        # recursive analysis
        for ii, pi in enumerate(path_in):
            print("Analyzing dataset {}/{}.".format(ii+1, len(path_in)))
            cli_extract_roi(path=pi)
        # nothing else to do
        return
    # cli_convert will ask for the required meta data
    h5series = cli_convert(path=path_in, ret_data=True)
    # get the configuration after cli_convert was run
    cfg = config.ConfigFile(path_out)
    # background correction
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
        # Only get the Canny edge detection parameters if needed
        if not (cfg["bg"]["phase mask sphere"] is None
                and cfg["bg"]["amplitude mask sphere"] is None):
            dialog.main(path=path, req_meta=["medium index"])
            # This will generate the [sphere] section in drymass.cfg
            edge_kw = {
                "clip_rmin": cfg["sphere"]["edge clip radius min"],
                "clip_rmax": cfg["sphere"]["edge clip radius max"],
                "mult_coarse": cfg["sphere"]["edge coarse"],
                "mult_fine": cfg["sphere"]["edge fine"],
                "maxiter": cfg["sphere"]["edge iter"],
            }
        else:
            edge_kw = {}
    else:
        bg_amp_kw = None
        bg_pha_kw = None
        edge_kw = {}

    with TaskWatcher("Extracting ROIs... ") as tw:
        h5roi, rmgr, changed = extract_roi(
            h5series=h5series,
            dir_out=path_out,
            size_m=cfg["specimen"]["size um"] * 1e-6,
            size_var=cfg["roi"]["size variation"],
            max_ecc=cfg["roi"]["eccentricity max"],
            dist_border=cfg["roi"]["dist border px"],
            pad_border=cfg["roi"]["pad border px"],
            exclude_overlap=cfg["roi"]["exclude overlap px"],
            threshold=cfg["roi"]["threshold"],
            ignore_data=cfg["roi"]["ignore data"],
            force_roi=cfg["roi"]["force"],
            bg_amp_kw=bg_amp_kw,
            bg_amp_bin=cfg["bg"]["amplitude binary threshold"],
            bg_amp_mask_radial_clearance=cfg["bg"]["amplitude mask sphere"],
            bg_pha_kw=bg_pha_kw,
            bg_pha_bin=cfg["bg"]["phase binary threshold"],
            bg_pha_mask_radial_clearance=cfg["bg"]["phase mask sphere"],
            bg_sphere_edge_kw=edge_kw,
            search_enabled=cfg["roi"]["enabled"],
            ret_roimgr=True,
            ret_changed=True,
            count=tw.count,
            max_count=tw.max_count,
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
                # new indexing convention in drymass 0.6.0
                image_index = ii + 1
                rois = rmgr.get_from_image_index(image_index)
                imio = io.BytesIO()
                plot.plot_qpi_phase(qps[ii],
                                    rois=rois,
                                    path=imio,
                                    labels_excluded=cfg["roi"]["ignore data"])
                imio.seek(0)
                imdat = (mpimg.imread(imio) * 255).astype("uint8")
                tf.save(imdat, compress=9)
        print("Done")

    if ret_data:
        return h5roi


def strpar(cfg, section, key):
    """String representation of a section/key combination"""
    return "[{}] {} = {}".format(section, key, cfg[section][key])
