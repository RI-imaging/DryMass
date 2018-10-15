import pathlib
import warnings


class ROIManagerWarning(UserWarning):
    """Used for unexpected keyword arguments."""
    pass


class ROI(object):
    def __init__(self, identifier, image_index, roi_index, roi_slice):
        """Handle one region of interest (ROI)"""
        if not isinstance(identifier, str):
            raise ValueError("`identifier` must be a string!")
        # verify roi_slice
        if not (isinstance(roi_slice, (tuple, list))
                and len(roi_slice) == 2
                and isinstance(roi_slice[0], slice)
                and isinstance(roi_slice[1], slice)):
            raise ValueError("`roi_slice` must be a tuple of two slices!")

        self.identifier = identifier
        self.image_index = image_index
        self.roi_index = roi_index
        self.roi_slice = roi_slice

    def __eq__(self, other):
        return self.to_str() == other.to_str()

    def __lt__(self, other):
        # used for sorting
        if self.image_index == other.image_index:
            return self.roi_index < other.roi_index
        else:
            return self.image_index < other.image_index

    def __repr__(self):
        return self.to_str()

    @staticmethod
    def from_str(strin):
        """Load ROI from a string"""
        ll = strin.strip().split("\t")
        # extract slice data
        sldata = "".join([c for c in ll[3] if c in ",0123456789"])
        sldata = sldata.replace(",,", ",").split(",")
        sldata = [int(s) for s in sldata if s]
        slice1 = slice(min(sldata[0], sldata[1]),
                       max(sldata[0], sldata[1]))
        slice2 = slice(min(sldata[2], sldata[3]),
                       max(sldata[2], sldata[3]))
        roi = ROI(identifier=ll[0],
                  image_index=int(ll[1]),
                  roi_index=int(ll[2]),
                  roi_slice=(slice1, slice2)
                  )
        return roi

    def to_str(self):
        """Export ROI to a string"""
        strout = "\t".join([self.identifier,
                            str(self.image_index),
                            str(self.roi_index),
                            str(self.roi_slice)
                            ])
        return strout


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
        return len(self.rois)

    def add(self, roi_slice, image_index, roi_index, identifier):
        """Add a ROI to ROIManager

        Parameters
        ----------
        roi_slice: (slice, slice)
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
        self.rois.append(ROI(identifier=identifier,
                             image_index=image_index,
                             roi_index=roi_index,
                             roi_slice=roi_slice))

    def get_from_image_index(self, image_index):
        rois = [r for r in self.rois if r.image_index == image_index]
        return sorted(rois)

    def load(self, path):
        """Load ROIs from a text file"""
        path = pathlib.Path(path)
        with path.open(mode="r") as fd:
            lines = fd.readlines()
        for ll in lines:
            # ignore empty lines
            if ll.strip():
                self.rois.append(ROI.from_str(ll))

    def save(self, path):
        """Save ROIs to a text file (`path` will be overridden)"""
        path = pathlib.Path(path)
        with path.open(mode="w") as fd:
            for roi in self.rois:
                fd.write(roi.to_str() + "\r\n")
