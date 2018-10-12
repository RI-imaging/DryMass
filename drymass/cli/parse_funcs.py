import numbers
from os import fspath
import pathlib

import numpy as np


def fbool(value):
    """Boolean value from string or number"""
    if isinstance(value, str):
        value = value.lower()
        if value == "false":
            value = False
        elif value == "true":
            value = True
        elif value:
            value = bool(float(value))
        else:
            raise ValueError("Got empty string!")
    else:
        value = bool(float(value))
    return value


def fintlist(alist):
    """List of integers from string or list of strings/integers"""
    outlist = []
    if isinstance(alist, str):
        # we have a string (comma-separated integers)
        alist = alist.strip().strip("[] ").split(",")
    for it in alist:
        if it:
            outlist.append(int(float(it)))
    return outlist


def float01(flt):
    """Float value between 0 and 1"""
    flt = float(flt)
    if flt < 0 or flt > 1:
        raise ValueError("Input must be between 0 and 1!")
    return flt


def float_or_str(flt_or_str):
    """Float value from string or number"""
    if isinstance(flt_or_str, str):
        flt_or_str = flt_or_str.strip()
        if flt_or_str == "nan":
            return np.nan
        else:
            try:
                value = float(flt_or_str)
            except ValueError:
                return flt_or_str
            else:
                return value
    else:
        return float(flt_or_str)


def floattuple_or_one(fti):
    """Tuple of two floats or ±1 from a string or a number"""
    msg = "Expected +1, -1 or (float, float), got '{}'!".format(fti)
    if isinstance(fti, (list, tuple)):
        if len(fti) != 2:
            raise ValueError(msg)
        fti = [float(fti[0]), float(fti[1])]
    elif isinstance(fti, str):
        if fti.count(","):  # tuple
            for s in " ()[]":
                fti = fti.replace(s, "")
            fti = floattuple_or_one(fti.split(","))
        else:  # one
            try:
                fti = int(float(fti))
            except ValueError:
                raise ValueError(msg)
    elif isinstance(fti, numbers.Number):
        fti = int(fti)
        if fti in [+1, -1]:
            pass
        else:
            raise ValueError(msg)
    else:
        fti = floattuple_or_one(list(fti))
    return fti


def int_or_path(intpath):
    """Integer or string from a string or a number"""
    if isinstance(intpath, str):
        intpath = intpath.strip()
        if intpath.replace(".", "").isdigit():
            value = int(float(intpath))
        else:
            value = fspath(intpath)
    elif isinstance(intpath, pathlib.Path):
        value = fspath(intpath)
    else:
        value = int(float(intpath))
    return value


def lcstr(astr):
    """Convert a string to lower-case"""
    return astr.lower()


def strlist(alist):
    """List of strings, comma- or space-separated"""
    if isinstance(alist, str):
        for s in "()[]'"+'"':
            alist = alist.replace(s, "")
        alist = alist.replace(",", " ")
        alist = alist.split(" ")
    alist = [a for a in alist if a.strip()]
    alist = sorted(alist)
    return alist


def tupletupleint(items):
    """A tuple containing x- and y- slice tuples from a string or tuple"""
    if isinstance(items, str):
        for s in " ()[]":
            items = items.replace(s, "")
        # we have a string representation of the slices
        x1, x2, y1, y2 = items.split(",")
        out = ((int(float(x1)), int(float(x2))),
               (int(float(y1)), int(float(y2))))
    else:
        (x1, x2), (y1, y2) = items
        out = ((int(float(x1)), int(float(x2))),
               (int(float(y1)), int(float(y2))))
    return out


func_types = {fbool: bool,
              fintlist: list,
              lcstr: str,
              tupletupleint: tuple,
              }
