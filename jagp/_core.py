import jinja2
import os
from _parser import parse, parse_component
import argparse
from yaml import load, dump, Loader


templates_path = os.path.join(os.path.dirname(__file__), "..", "templates", "include")
environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(templates_path),
    trim_blocks=True,
    lstrip_blocks=True
)

#%% Simple test of a parser
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    args = parser.parse_args()

    with open(args.input_file, "r") as fid:
        desc = load(fid, Loader=Loader)

    parsedcomponents, parsedpackets = parse(desc, args.verbose)

    # Generate templates
    Component_globals = {
        'use_get_prefix': False,
        'hasToCString': True,
        'hasToStdString': True,
        'enclose_components_in_namespace': True
    }
    # component_template = environment.get_template("Component.h.jinja2")
    # txt = component_template.render(
    #     Component_globals=Component_globals
    # )
    # with open(os.path.join(
    #     os.path.dirname(__file__), "..",
    #     "build", "Component.h"), "w"
    # ) as fid:
    #     fid.write(txt)
    
    specComponent_template = environment.get_template("SpecificComponent.h.jinja2")
    for component in parsedcomponents:
        txt = specComponent_template.render(
            component=component,
            Component_globals=Component_globals
        )
        filepath = os.path.join(
            os.path.dirname(__file__), "..",
            "build", "%s.h" % (component['name'])) 
        with open(filepath, "w") as fid:
            print("Writing to %s" % (filepath))
            fid.write(txt)
