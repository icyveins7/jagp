#pragma once

#include "Header.h"

class {{ header.name }} : public Header
{
public:
    {% if header.usesExtraBits %}
    {{ header.name }}()
        : Header({{ header.numBytes }}, {{ header.numExtraBits }})
    {
    }
    {% else %}
    {{ header.name }}()
        : Header({{ header.numBytes }})
    {
    }
    {% endif %}

    {% for field in header.fields %}
    {{ field.type }} get{{ field.name }}(){ return {{ field.name }}; }
    void set{{ field.name }}({{ field.type }} value){ {{ field.name }} = value; }
    {% endfor %}

    virtual void write(uint8_t *buf) override
    {
        {% for field in header.fields %}
        {# Handle byte offsets #}
        {% if field.size % 8 != 0 %}
        std::memcpy(&buf[{{ field.byte_offset }}], &{{ field.name }}, sizeof({{ field.type }}));
        {# Handle bit offsets #}
        {% else %}
        buf[{{ field.byte_offset }}] |= buf[{{ field.byte_offset }}] // todo
        {% endif %}
        {% endfor %}
    }

    virtual void read(const uint8_t *buf) override
    {

    }

private:
    {% for field in header.fields %}
    {{ field.type }} {{ field.name }};
    {% endfor %}
};