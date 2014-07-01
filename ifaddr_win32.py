# Copyright (C) 2014 Stefan C. Mueller

import ipaddress
import ctypes
from ctypes import wintypes

from ifaddr_shared import Interface

NO_ERROR=0
ERROR_BUFFER_OVERFLOW = 111
MAX_ADAPTER_NAME_LENGTH = 256
MAX_ADAPTER_DESCRIPTION_LENGTH = 128
MAX_ADAPTER_ADDRESS_LENGTH = 8
AF_INET = 2
AF_INET6 = 10


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
    
class SOCKET_ADDRESS(ctypes.Structure):
    _fields_ = [('lpSockaddr', ctypes.POINTER(sockaddr)),
               ('iSockaddrLength', wintypes.INT)]
    
class IP_ADAPTER_UNICAST_ADDRESS(ctypes.Structure):
    pass
IP_ADAPTER_UNICAST_ADDRESS._fields_ = \
    [('Length', wintypes.ULONG),
     ('Flags', wintypes.DWORD),
     ('Next', ctypes.POINTER(IP_ADAPTER_UNICAST_ADDRESS)),
     ('Address', SOCKET_ADDRESS),
     ('PrefixOrigin', ctypes.c_uint),
     ('SuffixOrigin', ctypes.c_uint),
     ('SuffixOrigin', ctypes.c_uint),
     ('DadState', ctypes.c_uint),
     ('ValidLifetime', wintypes.ULONG),
     ('PreferredLifetime', wintypes.ULONG),
     ('LeaseLifetime', wintypes.ULONG),
     ('OnLinkPrefixLength', ctypes.c_uint8),
     ]

class IP_ADAPTER_ADDRESSES(ctypes.Structure):
    pass
IP_ADAPTER_ADDRESSES._fields_ = [('Length', wintypes.ULONG),
                                 ('IfIndex', wintypes.DWORD),
                                 ('Next', ctypes.POINTER(IP_ADAPTER_ADDRESSES)),
                                 ('AdapterName', ctypes.c_char_p),
                                 ('FirstUnicastAddress', ctypes.POINTER(IP_ADAPTER_UNICAST_ADDRESS)),
                                 ('FirstAnycastAddress', ctypes.POINTER(None)),
                                 ('FirstMulticastAddress', ctypes.POINTER(None)),
                                 ('FirstDnsServerAddress', ctypes.POINTER(None)),
                                 ('DnsSuffix', ctypes.c_wchar_p),
                                 ('Description', ctypes.c_wchar_p),
                                 ('FriendlyName', ctypes.c_wchar_p)
                                 ]



iphlpapi = ctypes.windll.LoadLibrary("Iphlpapi")


def get_ip_from_address(address):
    generic = address.lpSockaddr
    if generic[0].sa_familiy == AF_INET:
        ipv4 = ctypes.cast(address.lpSockaddr, ctypes.POINTER(sockaddr_in))
        ippacked = bytes(bytearray(ipv4[0].sin_addr))
        ip = str(ipaddress.ip_address(ippacked))
        return ip
    elif generic[0].sa_familiy == AF_INET6:
        ipv6 = ctypes.cast(address.lpSockaddr, ctypes.POINTER(sockaddr_in6))
        flowinfo = ipv6[0].sin6_flowinfo
        ippacked = bytes(bytearray(ipv6[0].sin6_addr))
        ip = str(ipaddress.ip_address(ippacked))
        scope_id = ipv6[0].scope_id
        return (ip, flowinfo, scope_id)

def enumerate_interfaces_of_adapter(name, nice_name, address):
    
    # Iterate through linked list and fill list
    addresses = []
    while True:
        addresses.append(address)
        if not address.Next:
            break
        address = address.Next[0]
        
    for address in addresses:
        ip = get_ip_from_address(address.Address)
        network_prefix = address.OnLinkPrefixLength
        yield Interface(name, ip, network_prefix, nice_name)
    
    
def enumerate_interfaces():
    
    # Call GetAdaptersAddresses() with error and buffer size handling
    addressbuffersize = wintypes.ULONG(15*1024)
    addressbuffer = ctypes.create_string_buffer(addressbuffersize.value)
    retval = ERROR_BUFFER_OVERFLOW
    while retval == ERROR_BUFFER_OVERFLOW:
        retval = iphlpapi.GetAdaptersAddresses(wintypes.ULONG(AF_INET),
                                      wintypes.ULONG(0),
                                      None,
                                      ctypes.byref(addressbuffer),
                                      ctypes.byref(addressbuffersize))
    if retval != NO_ERROR:
        raise ctypes.WinError()
    
    # Iterate through adapters fill array
    address_infos = []
    address_info = IP_ADAPTER_ADDRESSES.from_buffer(addressbuffer)
    while True:
        address_infos.append(address_info)
        if not address_info.Next:
            break
        address_info = address_info.Next[0]
    
    
    # Iterate through unicast addresses
    result = []
    for adapter_info in address_infos:
        
        name = adapter_info.AdapterName
        nice_name = adapter_info.Description + " / " + adapter_info.FriendlyName
        
        if adapter_info.FirstUnicastAddress:
            ips = enumerate_interfaces_of_adapter(name, nice_name, adapter_info.FirstUnicastAddress[0])
            
            result.extend(ips)

    return result
