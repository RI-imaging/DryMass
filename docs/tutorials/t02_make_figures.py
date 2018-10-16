from drymass import cli
import imageio
import matplotlib.pylab as plt
import numpy as np

from t02_method_comparison import dot_boxplot

path = "DHM_HL60_cells.zip"

# setup output directory
path_in, path_out = cli.dialog.main(path)

# set metadata
cfg = cli.config.ConfigFile(path_out)
cfg.set_value("meta", "medium index", 1.335)
cfg.set_value("meta", "pixel size um", 0.107)
cfg.set_value("meta", "wavelength nm", 633)

# extract ROIs
cli.cli_extract_roi(path=path_in)

# get image 27
# Note: Remove the DHM_HL60_cells.zip_dm folder to reproduce the figure
senpath = path_out / cli.FILE_SENSOR_WITH_ROI_IMAGE
sentif = imageio.mimread(senpath)[26]
imageio.imsave("_t02_roi_search1.jpg", sentif[..., :3])

# rerun with updated configuration
cfg.set_value("specimen", "size um", 13)
cfg.set_value("roi", "pad border px", 80)
cfg.set_value("roi", "size variation", .2)
cfg.set_value("roi", "exclude overlap px", 100)
cli.cli_extract_roi(path=path_in)

# remove ROI slices
cfg.set_value("roi", "ignore data", ["8.4", "15.2", "18.2", "18.3", "35.2"])

# bg correction
cfg.set_value("bg", "phase border px", 30)
cfg.set_value("bg", "phase profile", "poly2o")

# edge projection
cfg.set_value("sphere", "method", "edge")
cfg.set_value("sphere", "model", "projection")
cli.cli_analyze_sphere(path=path_in)

senpath = path_out / cli.FILE_SPHERE_ANALYSIS_IMAGE.format("edge",
                                                           "projection")
sentif = imageio.mimread(senpath)[52]
imageio.imsave("_t02_edge_projection.jpg", sentif[..., :3])

# image projection
cfg.set_value("sphere", "method", "image")
cfg.set_value("sphere", "model", "projection")
cli.cli_analyze_sphere(path=path_in)

# image rytov
cfg.set_value("sphere", "method", "image")
cfg.set_value("sphere", "model", "rytov")
cli.cli_analyze_sphere(path=path_in)

# image rytov-sc
cfg.set_value("sphere", "method", "image")
cfg.set_value("sphere", "model", "rytov-sc")
cli.cli_analyze_sphere(path=path_in)

senpath = path_out / cli.FILE_SPHERE_ANALYSIS_IMAGE.format("image",
                                                           "rytov-sc")
sentif = imageio.mimread(senpath)[52]
imageio.imsave("_t02_image_rytov-sc.jpg", sentif[..., :3])

# comparison plot
ri_data = [
    np.loadtxt(path_out / "sphere_image_rytov-sc_statistics.txt",
               usecols=(1,)),
    np.loadtxt(path_out / "sphere_image_rytov_statistics.txt",
               usecols=(1,)),
    np.loadtxt(path_out / "sphere_image_projection_statistics.txt",
               usecols=(1,)),
    np.loadtxt(path_out / "sphere_edge_projection_statistics.txt",
               usecols=(1,)),
    ]
colors = ["#E48620", "#DE2400", "#6e559d", "#048E00"]
labels = ["image rytov-sc", "image rytov",
          "image projection", "edge projection"]

plt.figure(figsize=(8, 5))
ax = plt.subplot(111, title="HL60 (DHM)")
ax.set_ylabel("refractive index")
dot_boxplot(ax=ax, data=ri_data, colors=colors, labels=labels)
plt.tight_layout()
plt.savefig("_t02_reproduced_5d.jpg")
plt.close()
