#pragma once

#include <iostream>
#include <stdint.h>

class Header
{
public:
    {% if all_numExtraBits_zero %}
    Header(
        size_t numBytes,
        size_t numExtraBits
    ) : m_numBytes(numBytes), m_numExtraBits(numExtraBits)
    {
    }
    {% else %}
    Header(
        size_t numBytes
    ) : m_numBytes(numBytes)
    {
    }
    {% endif %}

    /// @brief Pure virtual method that writes the header's fields to the buffer
    /// @param buf Pointer to the start of the buffer. The header by definition begins at the start.
    /// @return Pointer to the next byte after the header.
    virtual uint8_t* write(uint8_t *buf) = 0;

    /// @brief Pure virtual method that reads the header's fields from the buffer
    /// @param buf Pointer to the start of the buffer. The header by definition begins at the start.
    /// @return Pointer to the next byte after the header.
    virtual uint8_t* read(uint8_t *buf) = 0;

    // TODO: implement read/write for headers that occupy sub-bytes

protected:
    size_t m_numBytes;
    {% if all_numExtraBits_zero %}
    size_t m_numExtraBits;
    {% endif %}

};