"""Parse DryMass definitions.py file"""
import io
import pathlib

from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from sphinx.util.nodes import nested_parse_with_titles
from docutils import nodes


class IncludeDirective(Directive):
    required_arguments = 1
    optional_arguments = 0

    def run(self):
        # determine path of definitions.py
        here = pathlib.Path(__file__).parent
        dfn = str(here / ".." / ".." / "drymass" / "cli" / "definitions.py")

        with io.open(dfn, "r") as myfile:
            text = myfile.readlines()

        # extract desired section
        idstart = '    "{}": '.format(self.arguments[0])
        idend = '    },'
        sec_text = []
        in_sec = False
        for line in text:
            if line.startswith(idstart):
                in_sec = True
                continue
            if in_sec and line.startswith(idend):
                break
            if in_sec:
                sec_text.append(line.strip())

        rst = []

        # parse each line to build up docstring
        el_data = {}
        for line in sec_text:
            if line.startswith('"'):
                if el_data:
                    # append and parse
                    parse_element(rst, **el_data)
                    # reset data
                    el_data = {}
                el_data["name"] = line.split("#")[0].strip('": ')
            elif line.startswith("("):
                default, dtype, doc = line.split(", ", 2)
                el_data["default"] = default[1:].strip('"')
                el_data["dtype"] = dtype
                el_data["doc"] = doc.strip('"),')
            elif line.startswith("#"):
                if "notes" not in el_data:
                    el_data["notes"] = []
                el_data["notes"].append(line[1:])
        else:
            # parse last element
            parse_element(rst, **el_data)

        vl = ViewList(rst, "fakefile.rst")
        # Create a node.
        node = nodes.section()
        node.document = self.state.document
        # Parse the rst.
        nested_parse_with_titles(self.state, vl, node)
        return node.children


def parse_element(rst, name="", doc="", notes=[], default="", dtype=""):
    if default == "np.nan":
        default = "nan"

    if dtype in ["float", "int", "str"]:
        str_dtype = ":class:`{}`".format(dtype)
    else:
        str_dtype = ":func:`{0} <drymass.cli.parse_funcs.{0}>`".format(dtype)
    rst.append("* | **{}** = {} ({}) -- {} ".format(name, default, str_dtype, doc))
    if notes:
        rst.append("  | {}".format("".join(notes).strip()))


def setup(app):
    app.add_directive('include_definition', IncludeDirective)

    return {'version': '0.1'}   # identifies the version of our extension
