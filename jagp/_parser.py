from yaml import load, dump
from yaml import Loader, Dumper
import itertools
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

# ========================================================================================
def inferBitsType(size: int) -> str:
    """
    Given a size, this function returns the C++ data type that is the largest
    unsigned integer that can hold that size.

    Parameters
    ----------
    size : int
        The size of the bit field

    Returns
    -------
    str
        The C++ data type that can hold the specified size
    """
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
            "Bit fields larger than 64-bits not implemented")
    
    return inferredType


# ========================================================================================
def parse(desc: dict, verbose: bool=True) -> (dict, dict):
    """
    Parses a YAML description of a set of components and packets, and returns a
    tuple of two dictionaries: one containing the parsed components, and the other
    containing the parsed packets.

    Parameters
    ----------
    desc : dict
        The YAML description of the components and packets

    verbose : bool, optional
        Whether to print debug information during parsing, by default True

    Returns
    -------
    (dict, dict)
        A tuple of two dictionaries: the first containing the parsed components, and
        the second containing the parsed packets
    """
    parsedcomponents = dict()
    parsedpackets = dict()

    for component_name, component in desc['components'].items():
        if verbose:
            print("=== Parsing component '%s'" % (component_name))
        parsedcomponent = parse_component(component, verbose)
        pprint.pprint(parsedcomponent)
        parsedcomponents[component_name] = parsedcomponent

    # # Extract a list of all the parsed component names
    # for packet in desc['packets']:
    #     parsedpacket = parse_packet(packet, parsedcomponents, verbose)
    #     pprint.pprint(parsedpacket)
    #     parsedpackets.append(parsedpacket)

    return parsedcomponents, parsedpackets


# ========================================================================================
def parse_component(component: dict, verbose: bool=True) -> dict:
    """
    Parses a component dictionary from a YAML description, and returns a
    dictionary containing the parsed information.

    As part of the parsing, the 'numBytes' value is set based on the list of the
    parsed fields. However, this is ignored if it is already specified.

    Parameters
    ----------
    component : dict
        The component dictionary from the YAML description

    verbose : bool, optional
        Whether to print debug information during parsing, by default True

    Returns
    -------
    dict
        A dictionary containing the parsed information about the component
    """
    parsed = component
    # Iterate over the fields
    offset = 0 # Accumulated offset in bits
    requires_vector = False
    for i, field in enumerate(parsed['fields']):
        offset, parsed_field = parse_field(offset, field, verbose)
        parsed['fields'][i] = parsed_field # Overwrite the field
        if parsed_field.get('repeats') is not None:
            requires_vector = True

    # For now, offset must end at the byte
    if offset % 8 != 0:
        raise ValueError(
            "Offset (%d) is not a multiple of 8 bits" % (offset)
        )

    # Check numBytes and write if it doesn't exist
    totalNumBytes = sum([field['size'] for field in parsed['fields'] if field.get('repeats') is None]) // 8
    if parsed.get('numBytes') is None:
        parsed['numBytes'] = totalNumBytes
        if verbose:
            print("Total number of bytes inferred to be %d" % (parsed['numBytes']))
    else:
        if parsed['numBytes'] != totalNumBytes:
            raise ValueError(
                "Number of bytes specified (%d) does not match inferred (%d)" % (
                parsed['numBytes'], totalNumBytes)
            )
        
    # Check for valid sets of values
    if parsed.get('valid') is not None:
        # TODO
        pass

    # Set field to indicate if dynamic
    parsed['requires_vector'] = requires_vector

    # Iterate over the parsed fields and evaluate the expressions for repeated ones
    fieldnames = list()
    for i, field in enumerate(parsed['fields']):
        if field.get('repeats') is not None:
            # Search all previous fieldnames
            for prevname in fieldnames:
                if prevname in field.get('repeats'):
                    # Prefix with 'm_' for the templates
                    field['repeats'] = field['repeats'].replace(prevname, "m_"+prevname)
                    if verbose:
                        print("Prefixing field %s repeats expression m_%s" % (field['name'], prevname))
        # Append the current field name for next iterations
        fieldnames.append(field['name'])

    return parsed


# ========================================================================================
def parse_field(offset: int, field: str|dict, verbose: bool=True) -> dict:
    # Check if it's the shortcut string
    if isinstance(field, str):
        # Split into the name and the type
        splitfield = field.split(" ")
        name = splitfield[0] 
        typekey = splitfield[1] # Minimally there must be two parts to the shorthand string
        # The third part is the optional fixed value

        # Extract the size in bits
        size = int(typekey[1:])

        # Infer offsets
        byte_offset = offset // 8
        bit_offset = offset % 8

        # Then extract the type required
        if typekey[0] == 'b':
            inferredType = inferBitsType(size)
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
        if len(splitfield) > 2 and splitfield[2][:5] == 'fixed':
            fixedValue = int(splitfield[2][6:])
            field['fixed'] = fixedValue

        # Increment offset counter
        offset += size
        
    # Otherwise if it's already a dict
    elif isinstance(field, dict):
        # Expect to see the name and the type at minimum
        if field.get('name') is None:
            raise ValueError("No name specified for field")
        if field.get('type') is None:
            raise ValueError("No type specified for field")
        # Check if the type is bits, if so we allocate an appropriate type for it
        elif field.get('type') == 'bits':
            if field.get('size') is None:
                raise ValueError("Must specify size for 'bits' type")
            
            # Infer a holding type
            inferredType = inferBitsType(field.get('size'))
            if verbose:
                print("Field '%s' will be stored as %s" % (field['name'], inferredType))
            field['type'] = inferredType
        
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
    
    # Check if the field is repeatable
    if field.get('repeats') is not None:
        # TODO: for now we assume it must be aligned and byte-multiple
        if field['bit_offset'] != 0 or field['size'] % 8 != 0:
            raise NotImplementedError("Repeated fields must be byte-aligned and byte-multiple for now; may change in future")

    else:
        # At the end, mutate the field dict to check whether it has to be split across multiple bytes;
        # This helps the template in bit offset calculations (instead of doing messy math in the template itself)
        field['sections'] = list()
        remBits = field['size']
        # Handle initial offset
        if field['bit_offset'] != 0:
            field['sections'].append(min(8 - field['bit_offset'], field['size']))
            remBits -= field['sections'][0]
        while remBits > 0:
            nextCopy = min(8, remBits)
            field['sections'].append(nextCopy)
            remBits -= nextCopy

        # Slower to accumulate after, but easier to read
        field['sections'] = list(itertools.accumulate(field['sections']))
    
    return offset, field
    

# ========================================================================================
def parse_packet(packet: dict, component_list: list, verbose: bool=True) -> dict:
    # Not going to use the YAML ampersand/asterisk referencing system 
    # because it's confusing when there's a lot of components
    for i, component in enumerate(packet['components']):
        # Parse the short form string
        if isinstance(component, str):
            # Split into the name and the type
            component_name, component_type = component.split(" ")
            if verbose:
                print("Shortcut split: Component %s, type %s" % (component_name, component_type))

            # Construct the dictionary
            cdict = {
                'name': component_name,
                'type': component_type
            }

        elif isinstance(component, dict):
            cdict = component

        else:
            raise TypeError("Component must be just a string or a dict")
        
        # Check that the component type is valid
        if cdict['type'] not in component_list:
            raise ValueError("Component '%s' has an invalid type '%s'" % (
                cdict['name'], cdict['type']))
        
        # Write back to the components itself
        packet['components'][i] = cdict

    return packet

