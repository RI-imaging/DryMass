"""Parse DryMass definitions.py file"""
from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from sphinx.util.nodes import nested_parse_with_titles
from docutils import nodes

from drymass.cli.definitions import config


class IncludeDirective(Directive):
    required_arguments = 1
    optional_arguments = 0

    def run(self):
        sec = self.arguments[0]

        content = config[sec]

        rst = []

        for key in content:
            # get data
            if len(content[key]) == 3:
                default, func, doc = content[key]
                notes = None
            elif len(content[key]) == 4:
                default, func, doc, notes = content[key]
            # parse dtype
            dtype = func.__name__
            if dtype in ["float", "int", "str"]:
                str_dtype = ":class:`{}`".format(dtype)
            else:
                str_dtype = ":func:`{0} <drymass.cli.parse_funcs.{0}>`".format(
                            dtype)
            # add list item
            rst.append("* | **{}** = {} ({}) -- {} ".format(key, default,
                                                            str_dtype, doc))
            if notes is not None:
                # add notes
                rst.append("  | {}".format(notes.strip()))
            rst.append("")

        vl = ViewList(rst, "fakefile.rst")
        # Create a node.
        node = nodes.section()
        node.document = self.state.document
        # Parse the rst.
        nested_parse_with_titles(self.state, vl, node)
        return node.children


def setup(app):
    app.add_directive('include_definition', IncludeDirective)

    return {'version': '0.1'}   # identifies the version of our extension
