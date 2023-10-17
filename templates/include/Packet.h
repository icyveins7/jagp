#pragma once

#include <stdint.h>
#include <iostream>
#include <vector>

#include "Component.h"


/// @brief Packets are comprised of an ordered vector of Components.
/// Each Component may be individually defined,
/// or may be itself a Packet to allow for encapsulation of different layer payloads of a stack.
class Packet 
{
public:
    Packet();

private:
    std::vector<Component> components;
    
};
