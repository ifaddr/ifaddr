# Copyright (C) 2014 Stefan C. Mueller

import ctypes
import socket
import ipaddress

class Interface(object):
    
    def __init__(self, name, ip, network_prefix, nice_name):
        
        #: Name of this interface.
        self.name = name
        
        #: IP address in string representation
        self.ip = ip
        
        #: Number of bits of the network part (netmask)
        self.network_prefix = network_prefix
        
        #: Human readable name for this interface.
        self.nice_name = nice_name
        
    def __repr__(self):
        return "Interface(name={name}, ip={ip}, network_prefix={network_prefix}, nice_name={nice_name})".format(
            name=self.name,
            ip=self.ip,
            network_prefix=self.network_prefix,
            nice_name=self.nice_name
        )
        
        
class sockaddr(ctypes.Structure):
    _fields_= [('sa_familiy', ctypes.c_ushort),
               ('sa_data', ctypes.c_byte * 14)]

class sockaddr_in(ctypes.Structure):
    _fields_= [('sin_familiy', ctypes.c_ushort),
               ('sin_port', ctypes.c_ushort),
               ('sin_addr', ctypes.c_byte * 4),
               ('sin_zero', ctypes.c_byte * 8)]
    
class sockaddr_in6(ctypes.Structure):
    _fields_= [('sin6_familiy', ctypes.c_ushort),
               ('sin6_port', ctypes.c_ushort),
               ('sin6_flowinfo', ctypes.c_ulong),
               ('sin6_addr', ctypes.c_byte * 16),
               ('sin6_scope_id', ctypes.c_ulong)]
    
    
def sockaddr_to_ip(sockaddr_ptr):
    if sockaddr_ptr[0].sa_familiy == socket.AF_INET:
        ipv4 = ctypes.cast(sockaddr_ptr, ctypes.POINTER(sockaddr_in))
        ippacked = bytes(bytearray(ipv4[0].sin_addr))
        ip = str(ipaddress.ip_address(ippacked))
        return ip
    elif sockaddr_ptr[0].sa_familiy == socket.AF_INET6:
        ipv6 = ctypes.cast(sockaddr_ptr, ctypes.POINTER(sockaddr_in6))
        flowinfo = ipv6[0].sin6_flowinfo
        ippacked = bytes(bytearray(ipv6[0].sin6_addr))
        ip = str(ipaddress.ip_address(ippacked))
        scope_id = ipv6[0].sin6_scope_id
        return(ip, flowinfo, scope_id)
    else:
        return None


def ipv6_prefixlength(address):
    return sum(bin(ord(b)).count("1") for b in address.packed)