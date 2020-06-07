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


import sys
import os
import ctypes.util
import ipaddress
import collections
import socket

import ifaddr._shared as shared
#from ifaddr._shared import sockaddr, Interface, sockaddr_to_ip, ipv6_prefixlength

class ifaddrs(ctypes.Structure):
    pass
ifaddrs._fields_ = [('ifa_next', ctypes.POINTER(ifaddrs)),
                    ('ifa_name', ctypes.c_char_p),
                    ('ifa_flags', ctypes.c_uint),
                    ('ifa_addr', ctypes.POINTER(shared.sockaddr)),
                    ('ifa_netmask', ctypes.POINTER(shared.sockaddr))]

libc = ctypes.CDLL(ctypes.util.find_library("socket" if os.uname()[0] == "SunOS" else "c"), use_errno=True)

def get_adapters(include_unconfigured=False):

    addr0 = addr = ctypes.POINTER(ifaddrs)()
    retval = libc.getifaddrs(ctypes.byref(addr))
    if retval != 0:
        eno = ctypes.get_errno()
        raise OSError(eno, os.strerror(eno))

    adapters = collections.OrderedDict()

    def add_address(adapter_name, family, address):
        if not adapter_name in adapters:
            try:
                index = socket.if_nametoindex(adapter_name)
            except (OSError, AttributeError):
                index = None
            adapters[adapter_name] = shared.Adapter(adapter_name, adapter_name, [],
                                                    index=index)
        adapters[adapter_name].addresses.append((family, address))

    while addr:
        name = addr[0].ifa_name
        if sys.version_info[0] > 2:
            name = name.decode(encoding='UTF-8')
        address = shared.decode_address(addr[0].ifa_addr)
        if address and address[0] in {socket.AF_INET, socket.AF_INET6}:
            if addr[0].ifa_netmask and not addr[0].ifa_netmask[0].sa_familiy:
                addr[0].ifa_netmask[0].sa_familiy = addr[0].ifa_addr[0].sa_familiy
            netmask = shared.decode_address(addr[0].ifa_netmask)[1]
            if isinstance(netmask, tuple):
                netmask = netmask[0]
                if sys.version_info[0] > 2:
                    netmaskStr = str(netmask)
                else:
                    netmaskStr = unicode(netmask)
                prefixlen = shared.ipv6_prefixlength(ipaddress.IPv6Address(netmaskStr))
            else:
                if sys.version_info[0] > 2:
                    netmaskStr = str('0.0.0.0/' + netmask)
                else:
                    netmaskStr = unicode('0.0.0.0/' + netmask)
                prefixlen = ipaddress.IPv4Network(netmaskStr).prefixlen
            ip = shared.IP(address[1], prefixlen, name)
            add_address(name, address[0], ip)
        elif address and include_unconfigured:
            add_address(name, address[0], address[1])
        addr = addr[0].ifa_next

    libc.freeifaddrs(addr0)

    return adapters.values()
