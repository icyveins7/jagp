from yaml import load, dump
from yaml import Loader, Dumper
import argparse
import pprint

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
    "f64": "double"
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
    parsedcomponents = list()
    parsedpackets = list()

    for component in desc['components']:
        parsedcomponent, offset = parse_component(component, verbose)
        pprint.pprint(parsedcomponent)
        parsedcomponents.append(parsedcomponent)

    return parsedcomponents, parsedpackets



def parse_component(component: dict, verbose: bool=True) -> dict:
    parsed = component
    # Iterate over the fields
    offset = 0 # Accumulated offset in bits
    for i, field in enumerate(parsed['fields']):
        offset, parsed_field = parse_field(offset, field, verbose)
        parsed['fields'][i] = parsed_field # Overwrite the field

    # Check numBytes and write if it doesn't exist
    totalNumBytes = offset // 8 + (1 if offset % 8 != 0 else 0)
    if parsed.get('numBytes') is None:
        parsed['numBytes'] = totalNumBytes
        if verbose:
            print("component '%s': Total number of bytes inferred to be %d" % (parsed['name'], parsed['numBytes']))
    else:
        if parsed['numBytes'] != totalNumBytes:
            raise ValueError(
                "component '%s': Number of bytes specified (%d) does not match inferred (%d)" % (
                parsed['name'], parsed['numBytes'], totalNumBytes)
            )
        
    # Check for valid sets of values
    if parsed.get('valid') is not None:
        # TODO
        pass

    return parsed, offset


def parse_field(offset, field, verbose: bool=True) -> dict:
    # Check if it's the shortcut string
    if isinstance(field, str):
        # Split into the name and the type
        name, typekey = field.split(" ")

        # Extract the size in bits
        size = int(typekey[1:])

        # Infer offsets
        byte_offset = offset // 8
        bit_offset = offset % 8

        # Then extract the type required
        if typekey[0] == 'b':
            # Look at the size and extract the next largest one to contain it
            if size <= 8:
                inferredType = "uint8_t"
            elif size <= 16:
                inferredType = "uint16_t"
            elif size <= 32:
                inferredType = "uint32_t"
            elif size <= 64:
                inferredType = "uint64_t"
            else:
                raise NotImplementedError(
                    "%s: Bit fields larger than 64-bits not implemented" % (field['name']))
        else:
            # Extract from the mapping, should automatically throw for us if it doesn't exist
            inferredType = stdintDict[typekey]

        if verbose:
            print("Shortcut split: %s %s, size %d" % (
                name, inferredType, size
            ))

        # Change the field in-place
        field = {
            'name': name,
            'type': inferredType,
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
            field['size'] = sizeInference[field['type']] # Change in place
            if verbose:
                print("Field '%s' size inferred to be %d bits" % (field['name'], field['size']))

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
            # This would cause overlap with previous fields
            raise ValueError(
                "Field '%s' byte offset (%d) + bit offset (%d) is greater than the current offset (%d)" % (
                field['name'], byte_offset, bit_offset, offset)
            )
        elif byte_offset*8 + bit_offset != offset:
            # This implies there's some padding to be expected
            if verbose:
                print(
                    "Padding detected before field '%s': byte offset (%d) + bit offset (%d) is greater than expected" % (
                    field['name'], byte_offset, byte_offset)
                )
            # Move our internal offset to the specified value
            offset = byte_offset*8 + bit_offset
        else:
            # Otherwise increment the offset
            offset += field['size']
        
        # Write the offset values
        field['byte_offset'] = byte_offset
        field['bit_offset'] = bit_offset
            
    else: 
        raise TypeError("Field must be just a string or a dict")
    
    return offset, field
    