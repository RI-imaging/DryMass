import numpy as np


def fbool(value):
    """boolean"""
    if isinstance(value, str):
        value = value.lower()
        if value == "false":
            value = False
        elif value == "true":
            value = True
        elif value:
            value = bool(float(value))
        else:
            raise ValueError("empty string")
    else:
        value = bool(float(value))
    return value


def fintlist(alist):
    """A list of integers"""
    outlist = []
    if isinstance(alist, str):
        # we have a string (comma-separated integers)
        alist = alist.strip().strip("[] ").split(",")
    for it in alist:
        if it:
            outlist.append(int(float(it)))
    return outlist


def float_or_str(flt_or_str):
    """Either a float or an alphanumeric string"""
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


def int_or_str(it_or_str):
    """Either an int or an alphanumeric string"""
    if isinstance(it_or_str, str):
        it_or_str = it_or_str.strip()
        if it_or_str.replace(".", "").isdigit():
            value = int(float(it_or_str))
        else:
            value = it_or_str
    else:
        value = int(float(it_or_str))
    return value


def lcstr(astr):
    """lower-case string"""
    return astr.lower()


def tupletupleint(items):
    """A tuple containing x- and y- slice tuples"""
    if isinstance(items, str):
        for s in " ()[]":
            items = items.replace(s, "")
        if items.strip():
            # we have a string representation of the slices
            x1, x2, y1, y2 = items.split(",")
            out = ((int(float(x1)), int(float(x2))),
                   (int(float(y1)), int(float(y2))))
        else:
            out = ()
    else:
        if items:
            (x1, x2), (y1, y2) = items
            out = ((int(float(x1)), int(float(x2))),
                   (int(float(y1)), int(float(y2))))
        else:
            out = ()
    return out


func_types = {fbool: bool,
              fintlist: list,
              lcstr: str,
              tupletupleint: tuple,
              }
