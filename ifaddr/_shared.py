# Copyright (c) 2014 Stefan C. Mueller

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


import ctypes
import socket
import ipaddress
import platform
import collections

class Adapter(collections.namedtuple('Adapter', ('name','nice_name','ips'))):
    """
    Represents a network interface device controller (NIC), such as a
    network card. An adapter can have multiple IPs.

    On Linux aliasing (multiple IPs per physical NIC) is implemented
    by creating 'virtual' adapters, each represented by an instance
    of this class. Each of those 'virtual' adapters can have both
    a IPv4 and an IPv6 IP address.
    """


class IP(collections.namedtuple('IP', ('ip','network_prefix','nice_name'))):
    """
    Represents an IP address of an adapter.
    """

    @property
    def is_IPv4(self):
        """
        Returns `True` if this IP is an IPv4 address and `False`
        if it is an IPv6 address.
        """
        return not isinstance(self.ip, tuple)

    @property
    def is_IPv6(self):
        """
        Returns `True` if this IP is an IPv6 address and `False`
        if it is an IPv4 address.
        """
        return isinstance(self.ip, tuple)


if platform.system() == "Darwin":
    
    # Darwin uses marginally different structures
    # than either Linux or Windows.
    # I still keep it in `shared` since we can use
    # both structures equally.
    
    class sockaddr(ctypes.Structure):
        _fields_= [('sa_len', ctypes.c_uint8),
                   ('sa_familiy', ctypes.c_uint8),
                   ('sa_data', ctypes.c_byte * 14)]
    
    class sockaddr_in(ctypes.Structure):
        _fields_= [('sa_len', ctypes.c_uint8),
                   ('sa_familiy', ctypes.c_uint8),
                   ('sin_port', ctypes.c_ushort),
                   ('sin_addr', ctypes.c_byte * 4),
                   ('sin_zero', ctypes.c_byte * 8)]
        
    class sockaddr_in6(ctypes.Structure):
        _fields_= [('sa_len', ctypes.c_uint8),
                   ('sa_familiy', ctypes.c_uint8),
                   ('sin6_port', ctypes.c_ushort),
                   ('sin6_flowinfo', ctypes.c_ulong),
                   ('sin6_addr', ctypes.c_byte * 16),
                   ('sin6_scope_id', ctypes.c_ulong)]

else:

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
