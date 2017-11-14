import pathlib
import warnings


class ROIManager(object):
    def __init__(self, identifier=None):
        self.identifier = identifier
        self.rois = []

    def __len__(self):
        return self.rois.__len__()

    def add(self, roislice, image_index, roi_index, identifier):
        # verify identifier
        if self.identifier and self.identifier not in identifier:
            msg = "`identifier` does not match dataset: {}".format(identifier)
            warnings.warn(msg, ROIManagerWarnging)
        self.rois.append((identifier, image_index, roi_index, roislice))

    def get_from_image_index(self, image_index):
        rois = [[r[0], r[3]] for r in self.rois if r[1] == image_index]
        return rois

    def save(self, path):
        path = pathlib.Path(path)
        with path.open(mode="w") as fd:
            for roi in self.rois:
                roi = [str(r) for r in roi]
                fd.write("\t".join(roi) + "\r\n")


class ROIManagerWarnging(Warning):
    pass
