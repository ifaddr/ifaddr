# Copyright (C) 2014 Stefan C. Mueller

import os
import ctypes.util
import ipaddress

from ifaddr_shared import sockaddr, Interface, sockaddr_to_ip, ipv6_prefixlength

class ifaddrs(ctypes.Structure):
    pass
ifaddrs._fields_ = [('ifa_next', ctypes.POINTER(ifaddrs)),
                    ('ifa_name', ctypes.c_char_p),
                    ('ifa_flags', ctypes.c_uint),
                    ('ifa_addr', ctypes.POINTER(sockaddr)),
                    ('ifa_netmask', ctypes.POINTER(sockaddr))]

libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

def enumerate_interfaces():
    
    
    addr = ctypes.POINTER(ifaddrs)()
    retval = libc.getifaddrs(ctypes.byref(addr))
    if retval != 0:
        eno = ctypes.get_errno()
        raise OSError(eno, os.strerror(eno))
    
    interfaces = []
    
    while addr:
        name = addr[0].ifa_name
        ip = sockaddr_to_ip(addr[0].ifa_addr)
        if ip:
            netmask = sockaddr_to_ip(addr[0].ifa_netmask)
            if isinstance(netmask, tuple):
                netmask = netmask[0]
                prefixlen = ipv6_prefixlength(ipaddress.IPv6Address(unicode(netmask)))
            else:
                prefixlen = ipaddress.IPv4Network(unicode('0.0.0.0/' + netmask)).prefixlen
            interface = Interface(name, ip, prefixlen, name)
            interfaces.append(interface)
        addr = addr[0].ifa_next
        
    
    return interfaces