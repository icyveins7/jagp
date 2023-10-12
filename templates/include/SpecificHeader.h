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

private:
    {% for field in header.fields %}
    {{ field.type }} {{ field.name }};
    {% endfor %}
};