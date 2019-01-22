import pathlib

from . import definitions
from . import parse_funcs
from .._version import version

#: DryMass configuration file name
FILE_CONFIG = "drymass.cfg"


class ConfigFile(object):
    def __init__(self, path):
        """DryMass configuration file management

        Manage configuration file of an experimental data set
        with restrictions imposed by
        :data:`drymass.cli.definitions.config`.

        Parameters
        ----------
        path: str
            path to the configuration file or a folder containing the
            configuration file :data:`FILE_CONFIG`.
        """
        path = pathlib.Path(path).resolve()
        if path.is_dir():
            path = path / FILE_CONFIG
        path.touch()
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
        # For versions > 0.8.1, unknown configuration keys are `None`.
        # Prior versions also used `np.nan`. Keep "nan" in the list
        # below for backwards compatibility.
        if value in [None, "nan", "none", "None", "()", "[]"]:
            if definitions.config[section][key][0] is not None:
                msg = "Unset value '{}' not allowed for [{}]: {}!".format(
                      value, section, key)
                raise ValueError(msg)
            ret_value = None
        else:
            type_func = definitions.config[section][key][1]
            try:
                type_func(value)
            except BaseException as e:
                msg = "Failed to parse: '[{}]: {}={}'".format(section, key,
                                                              value)
                e.args = ("{}; {}".format(msg, ", ".join(e.args)),)
                raise
            ret_value = type_func(value)
        return ret_value

    def _parse_compat(self, section, key, value):
        if section == "bg":
            # drymass < 0.1.3: API changed in qpimage 0.1.6
            if (key in ["amplitude profile", "phase profile"]
                    and value == "ramp"):
                value = "tilt"
        elif section == "roi":
            # drymass <= 0.1.5: keys were renamed to reflect pixel units
            if key in ["dist border", "exclude overlap", "pad border"]:
                key += " px"
        return key, value

    def _parse(self, autocomplete=True):
        """Return configuration dictionary

        Parameters
        ----------
        autocomplete: bool
            whether to fill in default configuration values when
            the corresponding keys are missing in a given section.
            Note that missing sections are not added. If missing
            keys are found, the original configuration file is
            overridden with the new data. Disabling autocompletion
            also prevents writing to the configuration file.

        Returns
        -------
        datadict: dict of dicts
            configuration dictionary

        Notes
        -----
        This function is private, because the autocomplete feature is
        actually a desired behavior to keep the configuration file
        human-readable. Normal users should not be able to use it,
        because the concept could be considered confusing.
        """
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
                # backwards compatibility:
                key, val = self._parse_compat(sec, key, val)
                val = self._check_value(sec, key, val)
                outdict[sec][key] = val
        if autocomplete:
            # Insert default variables where missing
            must_write = False
            for sec in outdict:
                for key in definitions.config[sec]:
                    if key not in outdict[sec]:
                        outdict[sec][key] = definitions.config[sec][key][0]
                        must_write = True
            if must_write:
                # Update the configuration file
                self._write(outdict)
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
                if value is not None:
                    value = typefunc(value)
                    if typefunc is parse_funcs.strlist:
                        # cosmetics for e.g. '[roi]: ignore data'
                        value = ", ".join(value)
                lines.append("{} = {}".format(sk, value))
        for ii in range(len(lines)):
            lines[ii] += "\n"
        with self.path.open("w") as fd:
            fd.writelines(lines)

    def remove_section(self, section):
        """Remove a section from the configuration file"""
        datadict = self._parse(autocomplete=False)
        datadict.pop(section)
        self._write(datadict)

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

    def update(self, other):
        """Update the current configuration with data from another

        Parameters
        ----------
        other: ConfigFile
            the configuration file from which data is imported into
            the current configuration

        Notes
        -----
        None-valued keys are ignored.
        """
        other_dict = other._parse(autocomplete=False)
        for sec in other_dict:
            for key in other_dict[sec]:
                value = other_dict[sec][key]
                if value is not None:
                    self.set_value(section=sec,
                                   key=key,
                                   value=value)
