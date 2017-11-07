import copy

import matplotlib as mpl
import matplotlib.pylab as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np


CM_PHASE = "viridis"
CM_PHASE_ERROR = copy.copy(plt.get_cmap("seismic"))
CM_PHASE_ERROR.set_over("g", 1)
CM_PHASE_ERROR.set_under("g", 1)
CM_INTENSITY = "gray"
CM_REFRACTIVE_INDEX = "gnuplot2"


mpl.rcParams['font.family'] = "sans-serif"
mpl.rcParams["text.usetex"] = False


def add_cbar(ax, mapper, cbformat="%.2f", label="",
             loc="right", size="5%", labelloc=None):
    if labelloc is None:
        labelloc = loc
    divider = make_axes_locatable(ax)
    cax = divider.append_axes(loc, size=size, pad=0.05)
    acbar = plt.colorbar(mapper, cax=cax, format=cbformat, label=label)
    acbar.ax.yaxis.set_ticks_position(labelloc)
    acbar.ax.yaxis.set_label_position(labelloc)
    return acbar


def plot_image(data, ax=None, imtype="phase", cbar=True, px_um=None,
               ret_cbar=False, **kwargs):
    """
    type can be "phase", "intensity", "fluorescence"

    """
    if ax is None:
        ax = plt.subplot(111)

    if imtype == "phase":
        cmap = CM_PHASE
        gridcolor = "w"
        cbformat = "%.1f"
        cblabel = "[rad]"
    elif imtype == "intensity":
        cmap = CM_INTENSITY
        gridcolor = "k"
        cbformat = "%.3f"
        cblabel = "[a.u.]"
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
        cbformat = "%.3f"
        cblabel = ""
    elif imtype == "phase error":
        cmap = CM_PHASE_ERROR
        gridcolor = "k"
        if "vmin" not in kwargs and "vmax" not in kwargs:
            vmax = np.max(np.abs(data))
            kwargs["vmax"] = vmax
            kwargs["vmin"] = -vmax
        cbformat = "%.3f"
        cblabel = "[rad]"
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
                         cbformat=cbformat,
                         label=cblabel)

        if ret_cbar:
            retval.append(acbar)

    if len(retval) == 1:
        return retval[0]
    else:
        return retval


def plot_qpi_phase(qpi, rois=None, path=None):
    fig = plt.figure(figsize=(6, 4))
    ax1 = plt.subplot(111, title="sensor phase image")
    px_um = qpi["pixel size"] * 1e6
    plot_image(data=qpi.pha,
               ax=ax1,
               imtype="phase",
               cbar=True,
               px_um=px_um)
    if rois:
        for roi in rois:
            slx, sly = roi[1]
            x0 = slx.start * px_um
            x1 = slx.stop * px_um
            y0 = sly.start * px_um
            y1 = sly.stop * px_um
            box = mpl.patches.Rectangle(xy=(y0, x0),
                                        width=y1 - y0,
                                        height=x1 - x0,
                                        facecolor="none",
                                        edgecolor="w",
                                        )
            ax1.add_patch(box)
            ax1.text(y0, x0, roi[0],
                     horizontalalignment="left",
                     verticalalignment="bottom",
                     color="w")
    plt.tight_layout()
    if path:
        fig.savefig(path)
        plt.close()
    else:
        return fig


def plot_qpi_sphere(qpi_real, qpi_sim, path=None, simtype="simulation"):
    fig = plt.figure(figsize=(9, 4.5))
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
    ax1 = plt.subplot(
        231, title="phase data {}".format(qpi_real["identifier"]))
    plot_image(data=real_phase, ax=ax1, **kw_phase)

    # simulated phase
    ax2 = plt.subplot(232, title=simtype)
    plot_image(data=qpi_sim.pha, ax=ax2, **kw_phase)
    ax2.text(0.01, .99,
             "index: {:.5f}\n".format(index)
             + "radius: {:.3f}µm".format(radius_um),
             horizontalalignment="left",
             verticalalignment="top",
             color="w",
             transform=ax2.transAxes,
             )

    # phase difference
    ax3 = plt.subplot(233, title="phase difference")
    errmax = qpi_sim.pha.max() * .2
    plot_image(data=qpi_sim.pha - real_phase, ax=ax3,
               imtype="phase error", vmax=errmax, vmin=-errmax,
               px_um=px_um)

    # real intensity
    ax4 = plt.subplot(234, title="intensity {}".format(qpi_real["identifier"]))
    plot_image(data=real_inten, ax=ax4, **kw_inten)

    # computed intensity
    ax5 = plt.subplot(235, title=simtype)
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

    plt.tight_layout()
    if path:
        fig.savefig(path)
        plt.close()
    else:
        return fig
