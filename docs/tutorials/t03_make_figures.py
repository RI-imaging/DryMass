import shutil

from drymass import cli
import matplotlib.pylab as plt
import qpimage


path = "QLSR_PAA_beads_modified.h5"

# setup output directory
path_in, path_out = cli.dialog.main(path)
shutil.rmtree(path_out)


# Select 2nd order polynomial background correction
# -------------------------------------------------

# initial run with standard parameters
h5roi = cli.cli_extract_roi(path=path_in, ret_data=True)
h5sim = cli.cli_analyze_sphere(path=path_in, ret_data=True)

# get qpimage data of phase images with quadratic background
with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qproi, \
        qpimage.QPSeries(h5file=h5sim, h5mode="r") as qpsim:
    qe1 = [qproi[3].pha - qpsim[3].pha,
           qproi[4].pha - qpsim[4].pha]

# get configuration handle
cfg = cli.config.ConfigFile(path_out)

kwerr = {"px_um": cfg["meta"]["pixel size um"],
         "imtype": "phase error",
         "vmin": -0.5,
         "vmax": +0.5,
         "cbformat": "%.1f",
         }

kwplt = {"px_um": cfg["meta"]["pixel size um"]}

# repeat with poly2o correction
cfg.set_value("bg", "phase profile", "poly2o")
cli.cli_analyze_sphere(path=path_in, ret_data=True)
with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qproi, \
        qpimage.QPSeries(h5file=h5sim, h5mode="r") as qpsim:
    qe2 = [qproi[3].pha - qpsim[3].pha,
           qproi[4].pha - qpsim[4].pha]

# repeat with no correction
cfg.set_value("bg", "enabled", False)
cli.cli_extract_roi(path=path_in)
cfg.set_value("bg", "enabled", True)
with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qproi:
    qd = [qproi[3].pha, qproi[4].pha]

# plot differences
fig, axes = plt.subplots(2, 3, figsize=(8, 4.4))
cli.plot.plot_image(qd[0], ax=axes[0, 0], **kwplt)
cli.plot.plot_image(qe1[0], ax=axes[0, 1], **kwerr)
cli.plot.plot_image(qe2[0], ax=axes[0, 2], **kwerr)

cli.plot.plot_image(qd[1], ax=axes[1, 0], **kwplt)
cli.plot.plot_image(qe1[1], ax=axes[1, 1], **kwerr)
cli.plot.plot_image(qe2[1], ax=axes[1, 2], **kwerr)

for ii in range(axes.shape[0]):
    axes[ii, 0].set_title("input phase")
    axes[ii, 1].set_title("tilt residuals")
    axes[ii, 2].set_title("poly2o residuals")

    axes[ii, 1].set_ylabel("")
    axes[ii, 2].set_ylabel("")

axes[0, 0].set_xlabel("")
axes[0, 1].set_xlabel("")
axes[0, 2].set_xlabel("")

plt.tight_layout(pad=0, h_pad=.6)
plt.savefig("_t03_quadratic_correction.jpg")
plt.close()

# Include beads that are close to each other
# ------------------------------------------
cfg.set_value("roi", "exclude overlap px", 0)
cfg.set_value("bg", "enabled", False)
cli.cli_extract_roi(path=path_in)
cfg.set_value("bg", "enabled", True)
with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qproi:
    td = [qproi[5].pha, qproi[7].pha]

cli.cli_analyze_sphere(path=path_in)
with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qproi, \
        qpimage.QPSeries(h5file=h5sim, h5mode="r") as qpsim:
    te1 = [qproi[5].pha - qpsim[5].pha,
           qproi[7].pha - qpsim[7].pha]

cfg.set_value("bg", "phase binary threshold", "threshold_triangle")
cli.cli_analyze_sphere(path=path_in)
with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qproi, \
        qpimage.QPSeries(h5file=h5sim, h5mode="r") as qpsim:
    te2 = [qproi[5].pha - qpsim[5].pha,
           qproi[7].pha - qpsim[7].pha]

# plot differences
fig, axes = plt.subplots(2, 3, figsize=(8, 4.4))
cli.plot.plot_image(td[0], ax=axes[0, 0], **kwplt)
cli.plot.plot_image(te1[0], ax=axes[0, 1], **kwerr)
cli.plot.plot_image(te2[0], ax=axes[0, 2], **kwerr)

cli.plot.plot_image(td[1], ax=axes[1, 0], **kwplt)
cli.plot.plot_image(te1[1], ax=axes[1, 1], **kwerr)
cli.plot.plot_image(te2[1], ax=axes[1, 2], **kwerr)

for ii in range(axes.shape[0]):
    axes[ii, 0].set_title("input phase")
    axes[ii, 1].set_title("residuals, no mask")
    axes[ii, 2].set_title("residuals, with mask")
    axes[ii, 1].set_ylabel("")
    axes[ii, 2].set_ylabel("")

axes[0, 0].set_xlabel("")
axes[0, 1].set_xlabel("")
axes[0, 2].set_xlabel("")

plt.tight_layout(pad=0, h_pad=.6)
plt.savefig("_t03_bead_overlap.jpg")
plt.close()


# Include beads at the border of the sensor image
# -----------------------------------------------
cfg.set_value("roi", "dist border px", 0)
cfg.set_value("bg", "enabled", False)
cli.cli_extract_roi(path=path_in)
cfg.set_value("bg", "enabled", True)
with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qproi:
    bd = qproi[9].pha

cli.cli_analyze_sphere(path=path_in)
with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qproi, \
        qpimage.QPSeries(h5file=h5sim, h5mode="r") as qpsim:
    be = qproi[9].pha - qpsim[9].pha


# plot differences
fig, axes = plt.subplots(1, 2, figsize=(5, 2.4))
cli.plot.plot_image(bd, ax=axes[0], **kwplt)
cli.plot.plot_image(be, ax=axes[1], **kwerr)

axes[0].set_title("input phase")
axes[1].set_title("phase residuals")
axes[1].set_ylabel("")

plt.tight_layout(pad=0)
plt.savefig("_t03_bead_border.jpg")
plt.close()

# Exact determination of radius and refractive index
# --------------------------------------------------
cfg.set_value("sphere", "method", "image")
cfg.set_value("sphere", "model", "rytov-sc")
h5ryt = cli.cli_analyze_sphere(path=path_in, ret_data=True)

errs = []
with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qproi, \
        qpimage.QPSeries(h5file=h5ryt, h5mode="r") as qpsim:
    for ii in range(len(qproi)):
        errs.append(qproi[ii].pha - qpsim[ii].pha)

errs.pop(8)

# plot differences
fig, axes = plt.subplots(3, 3, figsize=(8, 8))
axes = axes.flatten()
titles = ["1. offset",
          "2. linear tilt",
          "3. linear tilt",
          "4. quadratic distortion",
          "5. quadratic distortion",
          "6.1 two beads",
          "6.2 two beads",
          "7. all of the above",
          "8. bead at border",
          ]

for ii in range(9):
    cli.plot.plot_image(errs[ii], ax=axes[ii], **kwerr)
    axes[ii].set_title(titles[ii])

for ii in range(6):
    axes[ii].set_xlabel("")

for ii in [1, 2, 4, 5, 7, 8]:
    axes[ii].set_ylabel("")

plt.tight_layout(pad=0, h_pad=.6, w_pad=.6)
plt.savefig("_t03_summary_rytov-sc.jpg")
plt.close()
