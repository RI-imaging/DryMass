import pathlib

from . import definitions

FILE_CONFIG = "drymass.cfg"


class ConfigFile(object):
    def __init__(self, path):
        path = pathlib.Path(path).resolve()
        if path.is_dir():
            path = path / FILE_CONFIG
        self.path = path

    def __getitem__(self, section):
        datadict = self._parse()
        if section in datadict:
            return datadict[section]
        elif section in definitions.config:
            return {}
        else:
            raise ValueError("Unknown section title: {}".format(section))

    def __setitem__(self, section, sectiondict):
        datadict = self._parse()
        for key in sectiondict:
            self._check_value(section, key, sectiondict[key])
        datadict[section] = sectiondict
        self._write(datadict)

    def _check_value(self, section, key, value):
        """Check if a section/key/value pair is valid

        Raises `ValueError` if this is not the case.
        Returns `None`.
        """
        if section not in definitions.config:
            raise ValueError("Unknown section title: {}".format(section))
        if key not in definitions.config[section]:
            raise ValueError("Unknown key: {}: {}".format(section, key))
        type_func = definitions.config[section][key][1]
        try:
            type_func(value)
        except BaseException:
            raise ValueError("Wrong dtype: {}: {}={}".format(section,
                                                             key, value))

    def _parse(self):
        if not self.path.exists():
            return {}
        with self.path.open() as fd:
            data = fd.readlines()
        outdict = {}
        for line in data:
            line = line.strip()
            if (line.startswith("#") or
                    len(line) == 0):
                pass
            elif line.startswith("["):
                sec = line.strip("[]")
                outdict[sec] = {}
            else:
                key, val = line.split("=")
                key = key.strip()
                val = val.strip()
                key_func = definitions.config[sec][key][1]
                val = key_func(val)
                outdict[sec][key] = val
        return outdict

    def _write(self, datadict):
        keys = sorted(list(datadict.keys()))
        lines = []
        for kk in keys:
            lines.append("[{}]".format(kk))
            subkeys = sorted(list(datadict[kk].keys()))
            for sk in subkeys:
                lines.append("{} = {}".format(sk, datadict[kk][sk]))
        for ii in range(len(lines)):
            lines[ii] += "\r\n"
        with self.path.open("w") as fd:
            fd.writelines(lines)

    def set_value(self, section, key, value):

        sec = self[section]
        sec[key] = value
        self[section] = sec
