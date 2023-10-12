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

specheader_template = environment.get_template("SpecificHeader.h")
specheaders = [
    {
        'name': 'HeaderA',
        'usesExtraBits': True,
        'numBytes': 1,
        'numExtraBits': 2,
        'fields': [
            {
                'name': 'fieldA',
                'type': 'uint8_t',
            },
            {
                'name': 'fieldB',
                'type': 'uint16_t'
            }
        ]
    },
    {
        'name': 'HeaderB',
        'usesExtraBits': False,
        'numBytes': 1,
        'numExtraBits': 0,
        'fields': [
            {
                'name': 'fieldA',
                'type': 'float',
            },
            {
                'name': 'fieldB',
                'type': 'int32_t'
            }
        ]
    }
]

for header in specheaders:
    txt = specheader_template.render(header=header)
    print(txt)
    print("========================================")

