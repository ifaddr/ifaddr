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


import os
import ctypes.util
import ipaddress
import collections
import platform
import socket
import sys

from typing import Dict, Iterable, Optional

import ifaddr._shared as shared

# from ifaddr._shared import sockaddr, Interface, sockaddr_to_ip, ipv6_prefixlength

# To aid with platform-specific type-checking
assert sys.platform != 'win32'


class ifaddrs(ctypes.Structure):
    pass


ifaddrs._fields_ = [
    ('ifa_next', ctypes.POINTER(ifaddrs)),
    ('ifa_name', ctypes.c_char_p),
    ('ifa_flags', ctypes.c_uint),
    ('ifa_addr', ctypes.POINTER(shared.sockaddr)),
    ('ifa_netmask', ctypes.POINTER(shared.sockaddr)),
]

libc = ctypes.CDLL(
    ctypes.util.find_library('socket' if os.uname()[0] == 'SunOS' else 'c'), use_errno=True
)

if platform.system() == 'Darwin' or 'BSD' in platform.system():
    IFF_MULTICAST = 1 << 15
else:
    IFF_MULTICAST = 1 << 12

def get_interfaces_cmdline():
    import os, re, ipaddress
    ifaces = {}
    curr_iface_name = None
    curr_iface = None
    try:
        popen_pipe = os.popen('ifconfig')
    except:
        popen_pipe = []
    for line in os.popen('ifconfig'):
        match = re.match('^([a-zA-Z0-9]+):', line)
        if match:
            if curr_iface_name:
                ifaces[curr_iface_name] = curr_iface
            curr_iface_name = match.group(1)
            curr_iface = {'multicast': False}
            if 'MULTICAST' in line:
                curr_iface['multicast'] = True
            continue
        match = re.match('\ *inet ([0-9\.]+)  netmask ([0-9\.]+)', line)
        if match:
            curr_iface[2] = []
            curr_addr = {'addr': match.group(1), 'netmask': match.group(2)}
            match = re.match('.* broadcast ([0-9\.]+)', line)
            if match:
                curr_addr['broadcast'] = match.group(1)
            else:
                match = re.match('.*  destination ([0-9\.]+)', line)
                if match:
                    curr_addr['peer'] = match.group(1)
            curr_iface[2].append(curr_addr)
            continue
        match = re.match('\ *inet6 ([a-f0-9\.:]+)  prefixlen ([0-9]+)', line)
        if match:
            curr_iface[30] = []
            network = ipaddress.IPv6Network(f'{match.group(1)}/{match.group(2)}', strict=False)
            curr_addr = {'addr': match.group(1), 'prefix': match.group(2), 'netmask': f"{network.netmask.compressed}/{match.group(2)}"}
            match = re.match('.* scopeid ([0-9x]+)', line)
            if match:
                curr_addr['scope'] = int(match.group(1), base=16)

            curr_iface[30].append(curr_addr)
    if curr_iface_name and curr_iface_name not in ifaces:
        ifaces[curr_iface_name] = curr_iface
    return ifaces

def get_adapters(include_unconfigured: bool = False) -> Iterable[shared.Adapter]:
    addr0 = addr = ctypes.POINTER(ifaddrs)()
    retval = libc.getifaddrs(ctypes.byref(addr))
    ips: Dict[str, shared.Adapter] = collections.OrderedDict()

    def add_ip(adapter_name: str, multicast: bool, ip: Optional[shared.IP]) -> None:
        if adapter_name not in ips:
            index: Optional[int] = None
            try:
                index = socket.if_nametoindex(adapter_name)
            except (OSError, AttributeError):
                pass
            ips[adapter_name] = shared.Adapter(
                adapter_name, adapter_name, [], index=index, multicast=multicast
            )
        if ip is not None:
            ips[adapter_name].ips.append(ip)

    if retval != 0:
        eno = ctypes.get_errno()
        interfaces = get_interfaces_cmdline()
        for interface_name in interfaces.keys():
            for addr_family in (2, 10):
                if addr_family not in interfaces[interface_name]:
                    continue
                for addr in interfaces[interface_name][addr_family]:
                    if 'prefix' not in addr:
                        prefixlen = ipaddress.IPv4Network(addr['netmask']).prefixlen
                    else:
                        prefixlen = addr['prefix']
                    addr_object = ipaddress.ip_address(addr['addr'])
                    if isinstance(addr_object, ipaddress.IPv6Address):
                        scope = addr.get('scope', 0)
                        ip_obj = shared.IPv6Ext(addr_object.compressed, 0, scope)
                    else:
                        ip_obj = shared.IPv4Ext(addr_object.compressed)
                    ip = shared.IP(ip_obj, prefixlen, interface_name)
                    add_ip(interface_name, interfaces[interface_name]['multicast'], ip)
        return ips.values()

    while addr:
        name = addr.contents.ifa_name.decode(encoding='UTF-8')
        multicast = addr.contents.ifa_flags & IFF_MULTICAST > 0
        ip_addr = shared.sockaddr_to_ip(addr.contents.ifa_addr)
        if ip_addr:
            if addr.contents.ifa_netmask and not addr.contents.ifa_netmask.contents.sa_familiy:
                addr.contents.ifa_netmask.contents.sa_familiy = (
                    addr.contents.ifa_addr.contents.sa_familiy
                )
            netmask = shared.sockaddr_to_ip(addr.contents.ifa_netmask)
            if isinstance(netmask, shared.IPv6Ext):
                prefixlen = shared.ipv6_prefixlength(netmask.address)
            else:
                assert netmask is not None, (
                    f'sockaddr_to_ip({addr.contents.ifa_netmask}) returned None'
                )
                netmaskStr = str('0.0.0.0/' + str(netmask.address))
                prefixlen = ipaddress.IPv4Network(netmaskStr).prefixlen
            ip = shared.IP(ip_addr, prefixlen, name)
            add_ip(name, multicast, ip)
        else:
            if include_unconfigured:
                add_ip(name, multicast, None)
        addr = addr.contents.ifa_next

    libc.freeifaddrs(addr0)

    return ips.values()
