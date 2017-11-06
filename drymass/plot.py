import matplotlib as mpl
import matplotlib.pylab as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np


CM_PHASE = "viridis"
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
                       interpolation="none",
                       origin="lower",
                       **kwargs)

    ax.set_xlabel("x [{}]".format(unit))
    ax.set_ylabel("y [{}]".format(unit))
    ax.set_title(imtype)
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
    ax1 = plt.subplot(111)
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
