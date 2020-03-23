import io
from os import fspath

import matplotlib.image as mpimg
import qpimage
from skimage.external import tifffile

from ..anasphere import analyze_sphere

from . import config
from . import dialog
from .extracting import cli_extract_roi
from . import plot
from .task_watcher import TaskWatcher


#: Matplotlib images of sphere analysis (TIFF)
FILE_SPHERE_ANALYSIS_IMAGE = "sphere_{}_{}_images.tif"


def cli_analyze_sphere(path=None, ret_data=False, profile=None):
    """Perform sphere analysis"""
    description = "Determine integral refractive index, radius, and " \
                  + "related parameters by inferring spherical symmetry " \
                  + "for each phase object found."
    path_in, path_out = dialog.main(path=path,
                                    req_meta=["medium index",
                                              "pixel size um",
                                              "wavelength nm"],
                                    description=description,
                                    profile=profile)
    if isinstance(path_in, list):
        # recursive analysis
        for ii, pi in enumerate(path_in):
            print("Analyzing dataset {}/{}.".format(ii+1, len(path_in)))
            cli_analyze_sphere(path=pi)
        # nothing else to do
        return
    cfg = config.ConfigFile(path_out)
    h5roi = cli_extract_roi(path=path_in, ret_data=True)

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

    with TaskWatcher("Performing sphere analysis... ") as tw:
        h5sim, changed, reused = analyze_sphere(
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
            ret_reused=True,
            count=tw.count,
            max_count=tw.max_count,
        )

    if reused:
        print("Done (reused {} previous fits).".format(reused))
    else:
        print("Done.")

    tifout = path_out / FILE_SPHERE_ANALYSIS_IMAGE.format(
        cfg["sphere"]["method"],
        cfg["sphere"]["model"]
    )
    if (changed and cfg["output"]["sphere images"]) or not tifout.exists():

        with TaskWatcher("Plotting sphere images... ") as tw:
            # plot h5series and rmgr with matplotlib
            with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qps_roi, \
                    qpimage.QPSeries(h5file=h5sim, h5mode="r") as qps_sim, \
                    tifffile.TiffWriter(fspath(tifout), imagej=True) as tf:
                tw.max_count.value += len(qps_roi)
                for qpi_real in qps_roi:
                    qpi_sim = find_qpi_by_identifier(qps_sim,
                                                     qpi_real["identifier"])
                    if qpi_sim is not None:
                        assert qpi_real["identifier"] in qpi_sim["identifier"]
                        imio = io.BytesIO()
                        plot.plot_qpi_sphere(qpi_real=qpi_real,
                                             qpi_sim=qpi_sim,
                                             path=imio,
                                             simtype=cfg["sphere"]["model"])
                        imio.seek(0)
                        imdat = (mpimg.imread(imio) * 255).astype("uint8")
                        tf.save(imdat, compress=9)
                    tw.count.value += 1
        print("Done")

    if ret_data:
        return h5sim


def find_qpi_by_identifier(qps, identifier):
    """Find the QPImage that has the same initial parts as identifier

    Parameters
    ----------
    qps: qpimage.QPSereis
        Series data
    identifier: str
        A string "hash:number" that identifies a QPImage

    Returns
    -------
    qpi: qpimage.QPImage or None
        The `QPImage` in ``qps`` whose first two identifier parts match
        ``identifier`` or `None`, if no matching `QPImage` is found.
    """
    numid = identifier.count(":") + 1
    for qpi in qps:
        parts = qpi["identifier"].split(":")
        if ":".join(parts[:numid]) == identifier:
            break
    else:
        qpi = None
    return qpi
