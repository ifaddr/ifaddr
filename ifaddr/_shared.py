# Copyright (C) 2014 Stefan C. Mueller

import ctypes
import socket
import ipaddress

class Adapter(object):
    """
    Represents a network interface device controller (NIC), such as a
    network card. An adapter can have multiple IPs.
    
    In Linux, the :attr:`name` is of the `eth0` or `eth0:1` style. 
    The :attr:`nice_name` is currently the same as :attr:`name`;
    This may change in future versions.
    Aliasing (multiple IPs per physical NIC) is implemented
    by creating 'virtual' adapters, each represented by an instance
    of this class. Each of those 'virtual' adapters can have both
    a IPv4 and an IPv6 IP address.
    
    In Windows, the :attr:`name` is a UUID in string representation,
    such as `{846EE342-7039-11DE-9D20-806E6F6E6963}`. The :attr:`nice_name`
    is the same as you would find in the system control panel, for example
    `Intel(R) 82579LM Gigabit Network Connection`. 
    """
    
    def __init__(self, name, nice_name, ips):
        
        #: Unique name that identifies the adapter in the system.
        #: For Linux is this of the form of `eth0` or `eth0:1`, for
        #: Windows it is a UUID in string representation, such as
        #: `{846EE342-7039-11DE-9D20-806E6F6E6963}`.
        self.name = name
        
        #: Human readable name of the adpater.
        self.nice_name = nice_name

        #: List of :class:`IP` instances in the order they were
        #: reported by the system.
        self.ips = ips
        
    def __repr__(self):
        return "Adapter(name={name}, nice_name={nice_name}, ips={ips})".format(
           name = repr(self.name),
           nice_name = repr(self.nice_name),
           ips = repr(self.ips)
        )


class IP(object):
    """
    Represents an IP address of an adapter.
    """
    
    def __init__(self, ip, network_prefix, nice_name):
        
        #: IP address. For IPv4 addresses this is a string in
        #: "xxx.xxx.xxx.xxx" format. For IPv6 addresses this
        #: is a three-tuple `(ip, flowinfo, scope_id)`, where
        #: `ip` is a string in the usual collon separated
        #: hex format.
        self.ip = ip
        
        #: Number of bits of the IP that represent the
        #: network. For a `255.255.255.0` netmask, this
        #: number would be `24`.
        self.network_prefix = network_prefix
        
        #: Human readable name for this IP. 
        #: In Linux is this currently the same as the adapter name.
        #: In Windows this is the name of the network connection
        #: as configured in the system control panel.
        self.nice_name = nice_name
        
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
    
    
    def __repr__(self):
        return "IP(ip={ip}, network_prefix={network_prefix}, nice_name={nice_name})".format(
            ip = repr(self.ip),
            network_prefix = repr(self.network_prefix),
            nice_name = repr(self.nice_name)                                                                          
        )


class Interface(object):
    
    def __init__(self, adapter, ip, network_prefix, nice_name):
        
        #: Name of the adapter to which this IP belongs
        self.adapter = adapter
        
        #: IP address in string representation
        self.ip = ip
        
        #: Number of bits of the network part (netmask)
        self.network_prefix = network_prefix
        
        #: Human readable name for this interface.
        self.nice_name = nice_name
        
    def __repr__(self):
        return "Interface(adapter={adapter}, ip={ip}, network_prefix={network_prefix}, nice_name={nice_name})".format(
            adapter=repr(self.adapter),
            ip=repr(self.ip),
            network_prefix=repr(self.network_prefix),
            nice_name=repr(self.nice_name)
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