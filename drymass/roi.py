import pathlib
import warnings


class ROIManagerWarning(UserWarning):
    """Used for unexpected keyword arguments."""
    pass


class ROIManager(object):
    def __init__(self, identifier=None):
        """Manage regions of interest (ROI) of an image series

        Parameters
        ----------
        identifier: str or None
            The identifier of the image series.
        """
        if not (isinstance(identifier, str) or identifier is None):
            raise ValueError("`identifier` must be `None` or a string!")
        self.identifier = identifier
        self.rois = []

    def __len__(self):
        return self.rois.__len__()

    def add(self, roislice, image_index, roi_index, identifier):
        """Add a ROI to ROIManager

        Parameters
        ----------
        roislice: (slice, slice)
            Two slices indicating the x- and y-axis limits.
        image_index: int
            The image index of the image series.
        roi_index: int
            The ROI index in image `image_index`
        identifier: str
            The ROI identifier. If `self.identifier` is not contained
            within `identifier`, a `ROIManagerWarning` will be issued.
        """
        # verify identifier
        if not isinstance(identifier, str):
            raise ValueError("`identifier` must be a string!")
        if self.identifier and self.identifier not in identifier:
            msg = "Identifier of ROIManager `{}` ".format(self.identifier) \
                  + "does not match that of QPSeries `{}`.".format(identifier)
            warnings.warn(msg, ROIManagerWarning)
        # verify roislice
        if not (isinstance(roislice, (tuple, list))
                and len(roislice) == 2
                and isinstance(roislice[0], slice)
                and isinstance(roislice[1], slice)):
            raise ValueError("`roislice` must be a tuple of two slices!")
        self.rois.append((identifier, image_index, roi_index, roislice))

    def get_from_image_index(self, image_index):
        rois = [[r[0], r[3]] for r in self.rois if r[1] == image_index]
        return rois

    def load(self, path):
        """Load ROIs from a text file"""
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
        """Save ROIs to a text file (`path` will be overridden)"""
        path = pathlib.Path(path)
        with path.open(mode="w") as fd:
            for roi in self.rois:
                roi = [str(r) for r in roi]
                fd.write("\t".join(roi) + "\r\n")
