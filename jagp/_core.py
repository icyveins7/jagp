import jinja2
import os


templates_path = os.path.join(os.path.dirname(__file__), "..", "templates", "include")
environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(templates_path),
    trim_blocks=True,
    lstrip_blocks=True
)


#%% Simple test of header
header_template = environment.get_template("Header.h")
txt = header_template.render(all_numBits_zero=True)
print(txt)
print("==========================")

specheader_template = environment.get_template("SpecHeader.h")
txt = specheader_template.render()
print(txt)

