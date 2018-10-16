from drymass import cli
import imageio
import numpy as np


path = "QLSR_PAA_beads"

# setup output directory
path_in, path_out = cli.dialog.main(path)

# set metadata
cfg = cli.config.ConfigFile(path_out)
cfg.set_value("meta", "medium index", 1.335)
cfg.set_value("meta", "pixel size um", 0.14)
cfg.set_value("meta", "wavelength nm", 647)

# perform analysis
cli.cli_analyze_sphere(path=path_in)

# get first sensor image
senpath = path_out / cli.FILE_SENSOR_WITH_ROI_IMAGE
sentif = imageio.imread(senpath)
imageio.imsave("_t01_sensor_roi_image.jpg", sentif[..., :3])

# get first sphere image
roipath = path_out / cli.FILE_SPHERE_ANALYSIS_IMAGE.format("edge",
                                                           "projection")
roitif = imageio.imread(roipath)
imageio.imsave("_t01_sphere_edge_projection_image.jpg", roitif[..., :3])


cfg.set_value("roi", "ignore data", ["4.1", "7.1", "24.1", "26.1", "27.1",
                                     "35.1", "36.1", "39.1", "40.1", "51.1",
                                     "52.1", "55.1", "58.1", "60.1", "64.1",
                                     "67.1", "71.1"])
# perform analysis again
cli.cli_analyze_sphere(path=path_in)

# extract mean and SD of RI
ri = np.loadtxt(path_out / "sphere_edge_projection_statistics.txt",
                usecols=(1,))
print("average: ", np.average(ri))
print("standard deviation: ", np.std(ri))
