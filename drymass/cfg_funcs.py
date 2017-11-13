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
            outlist.append(int(it))
    return outlist


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
            out = ((int(x1), int(x2)),
                   (int(y1), int(y2)))
        else:
            out = ()
    else:
        if items:
            (x1, x2), (y1, y2) = items
            out = ((int(x1), int(x2)),
                   (int(y1), int(y2)))
        else:
            out = ()
    return out


func_types = {fbool: bool,
              fintlist: list,
              lcstr: str,
              tupletupleint: tuple,
              }
