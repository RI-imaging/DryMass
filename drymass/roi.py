import warnings


class ROIManager(object):
    def __init__(self, dataset):
        self.dataset = dataset
        self.rois = []

    def add(self, roislice, image_index, roi_index, identifier):
        # verify identifier
        if self.dataset.identifier not in identifier:
            msg = "`identifier` does not match dataset: {}".format(identifier)
            warnings.warn(msg, ROIManagerWarnging)
        self.rois.append((roislice, image_index, roi_index, identifier))


class ROIManagerWarnging(Warning):
    pass
