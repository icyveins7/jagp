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
                'byte_offset': 0,
                'bit_offset': 0,
                'size': 2,
            },
            {
                'name': 'fieldB',
                'type': 'uint8_t',
                'byte_offset': 0,
                'bit_offset': 2,
                'size': 6
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
                'byte_offset': 0,
                'size': 32
            },
            {
                'name': 'fieldB',
                'type': 'int32_t',
                'byte_offset': 4,
                'size': 32
            },
            {
                'name': 'fieldC',
                'type': 'uint8_t',
                'byte_offset': 8,
                'bit_offset': 0,
                'size': 1
            },
            {
                'name': 'fieldD',
                'type': 'uint8_t',
                'byte_offset': 8,
                'bit_offset': 1,
                'size': 7
            }
        ]
    }
]

for header in specheaders:
    txt = specheader_template.render(header=header)
    print(txt)
    print("========================================")

