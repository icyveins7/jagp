from yaml import load, dump
from yaml import Loader, Dumper
import argparse

stdintDict = {
    "u8": "uint8_t",
    "u16": "uint16_t",
    "u32": "uint32_t",
    "u64": "uint64_t",
    "s8": "int8_t",
    "s16": "int16_t",
    "s32": "int32_t",
    "s64": "int64_t",
    "f32": "float",
    "f64": "double",
    "b1": "uint8_t", # For bit-sized fields
    "b2": "uint8_t",
    "b3": "uint8_t",
    "b4": "uint8_t",
    "b5": "uint8_t",
    "b6": "uint8_t",
    "b7": "uint8_t"
}

sizeInference = {
    "uint8_t": 8,
    "uint16_t": 16,
    "uint32_t": 32,
    "uint64_t": 64,
    "int8_t": 8,
    "int16_t": 16,
    "int32_t": 32,
    "int64_t": 64,
    "float": 32,
    "double": 64
}

def parse(desc: dict, verbose: bool=True) -> dict:
    parsed = desc
    for header in parsed['headers']:
        parsedheader, offset = parse_header(header, verbose)
        print(parsedheader)


def parse_header(header: dict, verbose: bool=True) -> dict:
    parsed = header
    # Iterate over the fields
    offset = 0 # Accumulated offset in bits
    for i, field in enumerate(parsed['fields']):
        # Check if it's the shortcut string
        if isinstance(field, str):
            # Split into the name and the type
            name, typekey = field.split(" ")
            size = int(typekey[1:])
            if verbose:
                print("Shortcut split: %s %s, size %d" % (
                    name, stdintDict[typekey], size
                ))

            # Infer offsets
            byte_offset = offset // 8
            bit_offset = offset % 8

            # Change the field in-place
            parsed['fields'][i] = {
                'name': name,
                'type': stdintDict[typekey],
                'size': size,
                'byte_offset': byte_offset,
                'bit_offset': bit_offset
            }

            # Increment offset counter
            offset += size
            
        # Otherwise if it's already a dict
        elif isinstance(field, dict):
            # Expect to see the name and the type at minimum
            if field.get('name') is None:
                raise ValueError("No name specified for field")
            if field.get('type') is None:
                raise ValueError("No type specified for field")

            # Check if size was specified, otherwise infer it
            if field.get('size') is None:
                parsed['fields'][i]['size'] = sizeInference[field['type']] # Change in place
                if verbose:
                    print("Field '%s' size inferred to be %d bits" % (field['name'], parsed['fields'][i]['size']))

            # Check if offsets were specified, infer them if they aren't
            if field.get('byte_offset') is None:
                byte_offset = offset // 8
                if verbose:
                    print("Field '%s' byte offset inferred to be %d" % (field['name'], byte_offset))
            else:
                byte_offset = field.get('byte_offset')

            if field.get('bit_offset') is None:
                bit_offset = offset % 8
                if verbose:
                    print("Field '%s' bit offset inferred to be %d" % (field['name'], bit_offset))
            else:
                bit_offset = field.get('bit_offset')

            # Verify that the final offset values are valid
            if byte_offset*8 + bit_offset < offset:
                raise ValueError(
                    "Field '%s' byte offset (%d) + bit offset (%d) is greater than the current offset (%d)" % (
                    field['name'], byte_offset, bit_offset, offset)
                )
            elif byte_offset*8 + bit_offset != offset:
                if verbose:
                    print(
                        "Padding detected before field '%s': byte offset (%d) + bit offset (%d) is greater than expected" % (
                        field['name'], byte_offset, byte_offset)
                    )
                # Move our internal offset to the specified value
                offset = byte_offset*8 + bit_offset
            else:
                # Otherwise increment the offset
                offset += parsed['fields'][i]['size']
            
            # Write the offset values
            parsed['fields'][i]['byte_offset'] = byte_offset
            parsed['fields'][i]['bit_offset'] = bit_offset
                
        else: 
            raise TypeError("Field must be just a string or a dict")
        
    # TODO: check if offset and optionally specified numBytes are valid

    return parsed, offset
            

#%% Simple test of a parser
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    args = parser.parse_args()

    with open(args.input_file, "r") as fid:
        desc = load(fid, Loader=Loader)

    print(parse(desc, args.verbose))

