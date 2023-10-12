#pragma once

#include <stdint.h>
#include <iostream>
#include "Header.h"

// Temporary forward declarations
// class Payload;

class Packet 
{
public:
    Packet();
    ~Packet();

private:
    Header m_header;
    // Payload m_payload;
};
