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


import ipaddress
import ctypes
import sys
from ctypes import wintypes

import ifaddr._shared as shared

from ctypes.wintypes import DWORD, BYTE, BOOL, UINT, ULONG

CHAR = ctypes.c_char
time_t = ctypes.c_ulong
POINTER = ctypes.POINTER
PULONG = POINTER(ULONG)


NO_ERROR=0
ERROR_BUFFER_OVERFLOW = 111
MAX_ADAPTER_NAME_LENGTH = 256
MAX_ADAPTER_DESCRIPTION_LENGTH = 128
MAX_ADAPTER_ADDRESS_LENGTH = 8
AF_UNSPEC = 0
ERROR_SUCCESS = 0x00000000


class SOCKET_ADDRESS(ctypes.Structure):
    _fields_ = [('lpSockaddr', ctypes.POINTER(shared.sockaddr)),
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


class _IP_ADDR_STRING(ctypes.Structure):
    pass


IP_ADDR_STRING = _IP_ADDR_STRING
PIP_ADDR_STRING = POINTER(_IP_ADDR_STRING)


class IP_ADDRESS_STRING(ctypes.Structure):
    _fields_ = [
        ('String', CHAR * (4 * 4))
    ]


PIP_ADDRESS_STRING = POINTER(IP_ADDRESS_STRING)
IP_MASK_STRING = IP_ADDRESS_STRING
PIP_MASK_STRING = POINTER(IP_ADDRESS_STRING)

IP_ADDR_STRING._fields_ = [
    ("Next", POINTER(_IP_ADDR_STRING)),
    ("IpAddress", IP_ADDRESS_STRING),
    ("IpMask", IP_MASK_STRING),
    ("Context", DWORD)
]


class _IP_ADAPTER_INFO(ctypes.Structure):
    pass


IP_ADAPTER_INFO = _IP_ADAPTER_INFO
PIP_ADAPTER_INFO = POINTER(_IP_ADAPTER_INFO)

IP_ADAPTER_INFO._fields_ = [
    ("Next", POINTER(_IP_ADAPTER_INFO)),
    ("ComboIndex", DWORD),
    ("AdapterName", CHAR * (MAX_ADAPTER_NAME_LENGTH + 4)),
    ("Description", CHAR * (MAX_ADAPTER_DESCRIPTION_LENGTH + 4)),
    ("AddressLength", UINT),
    ("Address", BYTE * MAX_ADAPTER_ADDRESS_LENGTH),
    ("Index", DWORD),
    ("Type", UINT),
    ("DhcpEnabled", UINT),
    ("CurrentIpAddress", PIP_ADDR_STRING),
    ("IpAddressList", IP_ADDR_STRING),
    ("GatewayList", IP_ADDR_STRING),
    ("DhcpServer", IP_ADDR_STRING),
    ("HaveWins", BOOL),
    ("PrimaryWinsServer", IP_ADDR_STRING),
    ("SecondaryWinsServer", IP_ADDR_STRING),
    ("LeaseObtained", time_t),
    ("LeaseExpires", time_t)
]

iphlpapi = ctypes.windll.LoadLibrary("Iphlpapi")


GetAdaptersInfo = iphlpapi.GetAdaptersInfo
GetAdaptersInfo.restype = ULONG
GetAdaptersInfo.argtypes = [PIP_ADAPTER_INFO, PULONG]


def enumerate_interfaces_of_adapter(nice_name, address):

    # Iterate through linked list and fill list
    addresses = []
    while True:
        addresses.append(address)
        if not address.Next:
            break
        address = address.Next[0]

    for address in addresses:
        ip = shared.sockaddr_to_ip(address.Address.lpSockaddr)
        network_prefix = address.OnLinkPrefixLength
        yield shared.IP(ip, network_prefix, nice_name)


def get_adapters(include_unconfigured=False):

    # Call GetAdaptersAddresses() with error and buffer size handling

    addressbuffersize = wintypes.ULONG(15*1024)
    retval = ERROR_BUFFER_OVERFLOW
    while retval == ERROR_BUFFER_OVERFLOW:
        addressbuffer = ctypes.create_string_buffer(addressbuffersize.value)
        retval = iphlpapi.GetAdaptersAddresses(wintypes.ULONG(AF_UNSPEC),
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
        if sys.version_info[0] > 2:
            # We don't expect non-ascii characters here, so encoding shouldn't matter
            name = name.decode()
        nice_name = adapter_info.Description
        index = adapter_info.IfIndex

        if adapter_info.FirstUnicastAddress:
            ips = enumerate_interfaces_of_adapter(adapter_info.FriendlyName, adapter_info.FirstUnicastAddress[0])
            ips = list(ips)
            additional_info = get_additional_adapter_info(name)
            gateways = additional_info.pop('gateways')

            for i, ip in enumerate(ips):
                try:
                    if isinstance(ip.ip, tuple):
                        ip_network = ipaddress.ip_interface(ip.ip[0]).network
                    else:
                        ip_network = ipaddress.ip_interface(ip.ip).network
                except ipaddress.AddressValueError:
                    continue

                for gateway in gateways:
                    gate_network = ipaddress.ip_interface(gateway.decode('utf-8')).network

                    if (
                        gate_network.version == ip_network.version and
                        gate_network.netmask == ip_network.netmask
                    ):
                        ip.gateways += [gateway]
            result.append(
                shared.Adapter(name, nice_name, ips,
                               index=index, **additional_info, gateways=gateways)
            )
        elif include_unconfigured:
            result.append(shared.Adapter(name, nice_name, [],
                                         index=index, gateways=gateways))

    return result


def get_additional_adapter_info(name):
    adapter_list = (IP_ADAPTER_INFO * 1)()
    buf_len = ULONG(ctypes.sizeof(adapter_list))
    rc = GetAdaptersInfo(ctypes.byref(
        adapter_list[0]),
        ctypes.byref(buf_len)
    )

    if rc == ERROR_BUFFER_OVERFLOW:
        adapter_list = (IP_ADAPTER_INFO * ctypes.sizeof(IP_ADAPTER_INFO))()

        buf_len = ULONG(ctypes.sizeof(adapter_list))
        rc = GetAdaptersInfo(
            ctypes.byref(adapter_list[0]),
            ctypes.byref(buf_len)
        )

    if rc == ERROR_SUCCESS:
        for a in adapter_list:
            if a.AdapterName == name:
                gateway_list = a.GatewayList
                gateways = ()
                while True:
                    if gateway_list:
                        gateways += (gateway_list.IpAddress.String,)
                    else:
                        break

                    gateway_list = gateway_list.Next

                result = dict(
                    gateways=gateways,
                    dhcp_enabled=bool(a.DhcpEnabled),
                    wins_enabled=bool(a.HaveWins)
                )

                if a.HaveWins:
                    result['wins_primary_server'] = a.PrimaryWinsServer
                    result['wins_secondary_server'] = a.SecondaryWinsServer

                if a.DhcpEnabled:
                    result['dhcp_server'] = a.DhcpServer
                    result['dhcp_lease_obtained'] = a.LeaseObtained
                    result['dhcp_lease_expires'] = a.LeaseExpires
                return result

        return dict(gateways=())

    else:
        raise ctypes.WinError()
