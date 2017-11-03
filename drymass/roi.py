import warnings


class ROIManager(object):
    def __init__(self, qps):
        self.qps = qps
        self.rois = []

    def add(self, roislice, image_index, roi_index, identifier):
        # verify identifier
        if self.qps.identifier and self.qps.identifier not in identifier:
            msg = "`identifier` does not match dataset: {}".format(identifier)
            warnings.warn(msg, ROIManagerWarnging)
        self.rois.append((roislice, image_index, roi_index, identifier))


class ROIManagerWarnging(Warning):
    pass
