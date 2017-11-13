import pathlib

from . import definitions
from ._version import version

FILE_CONFIG = "drymass.cfg"


class ConfigFile(object):
    def __init__(self, path):
        """DryMass configuration file management

        Manage configuration file of an experimental data set
        with restrictions imposed by `drymass.definitions.config`.

        Parameters
        ----------
        path: str
            path to the configuration file
        """
        path = pathlib.Path(path).resolve()
        if path.is_dir():
            path = path / FILE_CONFIG
        self.path = path

    def __getitem__(self, section):
        """Get a configuration section

        Parameters
        ----------
        section: str
            the configuration section

        Returns
        -------
        sectiondict: dict
            the configuration section dictionary
        """
        datadict = self._parse()
        if section in datadict:
            return datadict[section]
        elif section in definitions.config:
            # return default values
            secd = {}
            for kk in definitions.config[section]:
                secd[kk] = definitions.config[section][kk][0]
            # write result
            datadict[section] = secd
            self._write(datadict)
            return secd
        else:
            raise ValueError("Unknown section title: {}".format(section))

    def __setitem__(self, section, sectiondict):
        """Replace a section in the configuration file

        Parameters
        ----------
        section: str
            the section name
        sectiondict: dict
            the configuration dictionary

        Notes
        -----
        The previous content of the configuration section
        in the configuration file is replaced.
        """
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
        """Return full documentation

        Returns
        -------
        datadict: dict of dicts
            Full configuration
        """
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
        """Write configuration dictionary

        Parameters
        ----------
        datadict: dict of dicts
            the full configuration

        Notes
        -----
        The configuration key values are converted to the correct
        dtype before writing using the definitions given in
        definitions.py.
        """
        keys = sorted(list(datadict.keys()))
        lines = ["# DryMass version {}".format(version),
                 "# Configuration file documented at: ",
                 "# https://drymass.readthedocs.io/en/stable/configuration"
                 + "_file.html",
                 ]
        for kk in keys:
            lines.append("")
            lines.append("[{}]".format(kk))
            subkeys = sorted(list(datadict[kk].keys()))
            for sk in subkeys:
                value = datadict[kk][sk]
                typefunc = definitions.config[kk][sk][1]
                lines.append("{} = {}".format(sk, typefunc(value)))
        for ii in range(len(lines)):
            lines[ii] += "\r\n"
        with self.path.open("w") as fd:
            fd.writelines(lines)

    def set_value(self, section, key, value):
        """Set a configuration key value

        Parameters
        ----------
        section: str
            the configuration section
        key: str
            the configuration key in `section`
        value:
            the configuration key value

        Notes
        -----
        Valid section and key names are defined in definitions.py
        """
        # load, update, and save
        sec = self[section]
        sec[key] = value
        self[section] = sec
