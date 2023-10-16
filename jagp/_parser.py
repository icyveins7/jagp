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
        parsedfields = parse_header(header, verbose)


def parse_header(header: dict, verbose: bool=True) -> dict:
    parsed = header
    # Iterate over the fields
    parsedfields = list()
    for field in parsed['fields']:
        # Check if it's the shortcut string
        if isinstance(field, str):
            # Split into the name and the type
            name, typekey = field.split(" ")
            size = int(typekey[1:])
            if verbose:
                print("Shortcut split: %s %s, size %d" % (
                    name, stdintDict[typekey], size
                ))

            # Change the field in-place?


            # Push into a new list
            parsedfields.append({
                'name': name,
                'type': stdintDict[typekey],
                'size': size
            })
            
        # Otherwise if it's already a dict
        elif isinstance(field, dict):
            # Expect to see the name and the type at minimum
            if field.get('name') is None:
                raise ValueError("No name specified for field")
            if field.get('type') is None:
                raise ValueError("No type specified for field")

            # Check if size was specified, otherwise infer it
            if field.get('size') is None:
                field['size'] = sizeInference[field['type']] # Change in place
            
            # Push into a new list
            parsedfields.append(field)

        else: 
            raise TypeError("Field must be just a string or a dict")

    return parsedfields
            

#%% Simple test of a parser
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()

    with open(args.input_file, "r") as fid:
        desc = load(fid, Loader=Loader)

    print(desc)

