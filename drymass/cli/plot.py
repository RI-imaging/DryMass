import copy

import matplotlib as mpl
import matplotlib.pylab as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from ..import extractroi


CM_PHASE = "viridis"
CM_PHASE_ERROR = copy.copy(plt.get_cmap("seismic"))
CM_PHASE_ERROR.set_over("#37FF32")
CM_PHASE_ERROR.set_under("#05C500")
CM_INTENSITY = "gray"
CM_REFRACTIVE_INDEX = "gnuplot2"


try:
    mpl.rcParams['font.family'] = "sans-serif"
    mpl.rcParams["text.usetex"] = False
except TypeError:  # building the docs
    pass


def add_cbar(ax, mapper, fmt="%.2f", units="",
             loc="right", size="5%", labelloc=None,
             extend="neither"):
    """Add a colorbar to a plot"""
    if labelloc is None:
        labelloc = loc
    divider = make_axes_locatable(ax)
    cax = divider.append_axes(loc, size=size, pad=0.05)
    if units:
        cax.text(1.2, 1.05, units, ha="left", va="bottom")
    acbar = plt.colorbar(mapper, cax=cax, format=fmt, extend=extend)
    acbar.ax.yaxis.set_ticks_position(labelloc)
    acbar.ax.yaxis.set_label_position(labelloc)
    return acbar


def plot_image(data, ax=None, imtype="phase", cbar=True, px_um=None,
               ret_cbar=False, cbformat=None, **kwargs):
    """Plot an image

    Parameters
    ----------
    data: 2d np.ndarray
        Input image
    ax: matplotlib.Axes
        Axis to plot to
    imtype: str
        One of ["intensity", "phase", "phase error",
        "refractive index"].
    cbar: bool
        Whether to add a colorbar.
    px_um: float
        Pixel size [µm]
    ret_cbar: bool
        Whether to return the colorbar.
    kwargs: dict
        Keyword arguments to `plt.imshow`.

    Returns
    -------
    ax [, cbar]:
        Axis and colorbar.
    """
    if ax is None:
        ax = plt.subplot(111)

    cbkw = {}
    if cbformat is None:
        cbkw["fmt"] = "%.3f"
    else:
        cbkw["fmt"] = cbformat

    if imtype == "phase":
        cmap = CM_PHASE
        gridcolor = "w"
        if cbformat is None:
            cbkw["fmt"] = "%.1f"
        cbkw["units"] = "[rad]"
    elif imtype == "intensity":
        cmap = CM_INTENSITY
        gridcolor = "k"
        cbkw["units"] = "[a.u.]"
        # Make sure gray is at 1 in the colormap
        if "vmin" in kwargs and "vmax" in kwargs:
            vmin = kwargs["vmin"]
            vmax = kwargs["vmax"]
            if vmin < 1 and vmax > 1:
                diff = max(1 - vmin, vmax - 1)
                kwargs["vmin"] = 1 - diff
                kwargs["vmax"] = 1 + diff
    elif imtype == "refractive index":
        cmap = CM_REFRACTIVE_INDEX
        gridcolor = "w"
        cbkw["units"] = ""
    elif imtype == "phase error":
        cmap = CM_PHASE_ERROR
        gridcolor = "k"
        if "vmin" not in kwargs and "vmax" not in kwargs:
            vmax = np.max(np.abs(data))
            kwargs["vmax"] = vmax
            kwargs["vmin"] = -vmax
        cbkw["units"] = "[rad]"
        cbkw["extend"] = "both"
    else:
        raise ValueError("Unknown image type: {}".format(imtype))

    if px_um is None:
        shx, shy = np.array(data.shape)
        unit = "px"
    else:
        shx, shy = np.array(data.shape) * px_um
        unit = "µm"

    mapper = ax.imshow(data,
                       cmap=cmap,
                       extent=(0, shy, 0, shx),
                       interpolation="bilinear",
                       origin="lower",
                       **kwargs)

    ax.set_xlabel("x [{}]".format(unit))
    ax.set_ylabel("y [{}]".format(unit))
    ax.grid(color=gridcolor, lw="1", alpha=.1)

    retval = [ax]

    if cbar:
        acbar = add_cbar(ax=ax,
                         mapper=mapper,
                         **cbkw)

        if ret_cbar:
            retval.append(acbar)

    if len(retval) == 1:
        return retval[0]
    else:
        return retval


def plot_qpi_phase(qpi, rois=None, path=None, labels_excluded=[]):
    """Plot phase data"""
    fig = plt.figure(figsize=(6, 4))
    ax1 = plt.subplot(111)
    px_um = qpi["pixel size"] * 1e6
    plot_image(data=qpi.pha,
               ax=ax1,
               imtype="phase",
               cbar=True,
               px_um=px_um)
    if rois:
        for roi in rois:
            slx, sly = roi.roi_slice
            x0 = slx.start * px_um
            x1 = slx.stop * px_um
            y0 = sly.start * px_um
            y1 = sly.stop * px_um

            if extractroi.is_ignored_roi(roi=roi, ignore_data=labels_excluded):
                color = "r"
                ax1.text(y1, x1, "excluded",
                         horizontalalignment="right",
                         verticalalignment="top",
                         color=color)
            else:
                color = "w"
            box = mpl.patches.Rectangle(xy=(y0, x0),
                                        width=y1 - y0,
                                        height=x1 - x0,
                                        facecolor="none",
                                        edgecolor=color,
                                        )
            ax1.add_patch(box)
            ax1.text(y0, x0, roi.identifier,
                     horizontalalignment="left",
                     verticalalignment="bottom",
                     color=color)
    plt.tight_layout(rect=(0, 0, 1, .93), pad=.1)

    fig.text(x=.5, y=.99, s="sensor phase image",
             verticalalignment="top",
             horizontalalignment="center",
             fontsize=14)

    if path:
        fig.savefig(path)
        plt.close()
    else:
        return fig


def plot_qpi_sphere(qpi_real, qpi_sim, path=None, simtype="simulation"):
    """Plot QPI sphere analysis data"""
    fig = plt.figure(figsize=(9, 5))
    px_um = qpi_real["pixel size"] * 1e6
    radius_um = qpi_sim["sim radius"] * 1e6
    center = qpi_sim["sim center"]
    index = qpi_sim["sim index"]

    real_phase = qpi_real.pha
    kw_phase = {"px_um": px_um,
                "cbar": True,
                "imtype": "phase",
                "vmin": real_phase.min(),
                "vmax": real_phase.max(),
                }

    real_inten = qpi_real.amp**2
    kw_inten = {"px_um": px_um,
                "cbar": True,
                "imtype": "intensity",
                "vmin": real_inten.min(),
                "vmax": real_inten.max(),
                }
    # real phase
    ax1 = plt.subplot(231, title="data (phase)")
    plot_image(data=real_phase, ax=ax1, **kw_phase)

    # simulated phase
    ax2 = plt.subplot(232, title=simtype + " (phase)")
    plot_image(data=qpi_sim.pha, ax=ax2, **kw_phase)
    ax2.text(0.01, .99,
             "index: {:.5f}\n".format(index)
             + "radius: {:.3f}µm".format(radius_um),
             horizontalalignment="left",
             verticalalignment="top",
             color="w",
             transform=ax2.transAxes,
             )

    # phase residuals
    ax3 = plt.subplot(233, title="phase residuals")
    errmax = qpi_sim.pha.max() * .2
    plot_image(data=qpi_sim.pha - real_phase, ax=ax3,
               imtype="phase error", vmax=errmax, vmin=-errmax,
               px_um=px_um)

    # real intensity
    ax4 = plt.subplot(234, title="data (intensity)")
    plot_image(data=real_inten, ax=ax4, **kw_inten)

    # computed intensity
    ax5 = plt.subplot(235)
    if len(simtype) > 9:
        # sometimes the title is too long and is printed on top of the units
        kw5 = {"loc": "right",
               "ha": "right"}
    else:
        kw5 = {}
    ax5.set_title(simtype + " (intensity)", **kw5)

    plot_image(data=qpi_sim.amp**2, ax=ax5, **kw_inten)

    # plot detected radius
    for ax in [ax1, ax2, ax4, ax5]:
        circ = mpl.patches.Circle(xy=((center[1] + .5) * px_um,
                                      (center[0] + .5) * px_um),
                                  radius=radius_um,
                                  facecolor="none",
                                  edgecolor="w",
                                  ls=(0, (3, 8)),
                                  lw=.5,
                                  )
        ax.add_patch(circ)

    # line plot through center
    ax6 = plt.subplot(236, title="phase line plot")
    x = np.arange(qpi_real.shape[1]) * px_um
    ax6.plot(x, qpi_sim.pha[int(center[0])], label=simtype)
    ax6.plot(x, qpi_real.pha[int(center[0])], label="data")
    ax6.set_xlabel("[µm]")
    ax6.legend(loc="center right")

    # remove unused labels
    for ax in [ax1, ax2, ax3]:
        ax.set_xlabel("")
    for ax in [ax2, ax3, ax5]:
        ax.set_ylabel("")

    plt.tight_layout(rect=(0, 0, 1, .93), pad=.1, h_pad=.6)

    # add identifier
    fig.text(x=.5, y=.99, s=qpi_sim["identifier"],
             verticalalignment="top",
             horizontalalignment="center",
             fontsize=14)

    if path:
        fig.savefig(path)
        plt.close()
    else:
        return fig
