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
        'hasPrint': True,
        'hasToCString': True,
        'hasToStdString': True
    }
    component_template = environment.get_template("Component.h")
    txt = component_template.render(
        Component_globals=Component_globals
    )
    print(txt)
    print("==========================")

    specComponent_template = environment.get_template("SpecificComponent.h")
    for component in parsedcomponents:
        txt = specComponent_template.render(
            component=component,
            Component_globals=Component_globals
        )
        print(txt)
        print("========================================")
