# Jinja Auto-generated Packets

jagp helps you generate the source code needed to interact with buffers found in protocols. You define each packet and its components, and then you get headers that let you read/write individual fields and also read/write to raw buffers for further processing.

# Motivation

Why not use protobuf/kaitai-struct etc.? Kaitai-struct was the closest thing I could find that suited my needs, but it didn't offer write capabilities. The compiler itself was gargantuan and written in Scala(?), which I'm not familiar with. So instead of taking on the task of forking it and adding what I wanted, I decided to make my own with Python (which I'm more familiar with) and Jinja2's template engine.

If you find those other options more suited to your needs, please use those! My use-cases centre around a library that deals with DSP; I need to write code that interacts with bits received from the end of an RF receiver chain (demodulator output for example), or that needs to be sent to the beginning of an RF transmitter chain (modulator input for example). If this is you, then hopefully you will find this useful.

# How It Works

I borrowed a lot of inspiration from kaitai-struct. I use YAML to define packet and component structures here as well, although the syntax differs. There are 3 building blocks:

1. __Field__: This is the most low-level structure; it can be as small as 1 bit; components are generally defined as forward-lists of fields.
2. __Component__: This is a _natural_ grouping of fields. For example, the most common grouping of fields is into headers and payloads, since headers may be reused across multiple different payloads. Components can be fields of other components! For example, commonly used groups of fields that occur in various different payloads may be defined as a separate component and then reused (like a C struct or type).
3. __Packet__: This is the final grouping of components. Packets may also contain other packets; this describes the several layers that usually encapsulate each other in several headers.

# Defining the YAML

jagp will look for the ```components``` key in the YAML, and generate a C++ .h file for each item. The ```components``` key points to a dictionary of dictionaries (or mapping of mappings); each key will represent the name of the component.

```yaml
components: {
    ComponentA: { # Generates a ComponentA.h
        ...
    },

    ComponentB: { # Generates a ComponentB.h
        ...
    }
}
```

## Component

Within the component, the bare minimum is to define a ```fields``` key which points to a list (or sequence). Within the list, each item is either a simple string or a dictionary.

```yaml
ComponentA: {
    fields: [
        FieldA u8,
        FieldB b4,
        FieldC b2,
        FieldD b10,
        {
            name: FieldE,
            type: float
        },
        {
            name: FieldF,
            type # TODO: complete
        }
    ]
}
```