import pathlib
import warnings


class ROIManagerWarnging(Warning):
    pass


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

    def load(self, path):
        path = pathlib.Path(path)
        with path.open(mode="r") as fd:
            lines = fd.readlines()
        # remove empty lines
        lines = [ll for ll in lines if ll.strip()]
        for ll in lines:
            ll = ll.strip().split("\t")
            sldata = "".join([c for c in ll[3] if c in ",0123456789"])
            sldata = sldata.replace(",,", ",").split(",")
            sldata = [int(s) for s in sldata if s]
            slice1 = slice(min(sldata[0], sldata[1]),
                           max(sldata[0], sldata[1]))
            slice2 = slice(min(sldata[2], sldata[3]),
                           max(sldata[2], sldata[3]))
            self.add(identifier=ll[0],
                     image_index=int(ll[1]),
                     roi_index=int(ll[2]),
                     roislice=(slice1, slice2)
                     )

    def save(self, path):
        path = pathlib.Path(path)
        with path.open(mode="w") as fd:
            for roi in self.rois:
                roi = [str(r) for r in roi]
                fd.write("\t".join(roi) + "\r\n")
