# netifaces compatibility layer
import ipaddress

import ifaddr

AF_UNSPEC = 0
AF_UNIX = 1
AF_INET = 2
AF_IMPLINK = 3
AF_PUP = 4
AF_CHAOS = 5
AF_NS = 6
AF_ISO = 7
AF_ECMA = 8
AF_DATAKIT = 9
AF_CCITT = 10
AF_SNA = 11
AF_DECnet = 12
AF_DLI = 13
AF_LAT = 14
AF_HYLINK = 15
AF_APPLETALK = 16
AF_ROUTE = 17
AF_LINK = 18
AF_COIP = 20
AF_CNT = 21
AF_IPX = 23
AF_SIP = 24
AF_NDRV = 27
AF_ISDN = 28
AF_INET6 = 30
AF_NATM = 31
AF_SYSTEM = 32
AF_NETBIOS = 33
AF_PPP = 34

address_families = {globals()[name]: name for name in dir() if name.startswith('AF_')}


def interfaces():
    adapters = ifaddr.get_adapters(include_unconfigured=True)
    return [a.name for a in adapters]


def ifaddresses(interface):
    adapters_by_name = {a.name: a for a in ifaddr.get_adapters(include_unconfigured=True)}
    adapter = adapters_by_name[interface]
    addresses = {}
    for ip in adapter.ips:
        print(ip)
        if ip.is_IPv4:
            i = ipaddress.IPv4Interface('%s/%s' % (ip.ip, ip.network_prefix))
            address = {'addr': str(i.ip), 'peer': str(i.ip), 'netmask': str(i.netmask)}
            addresses.setdefault(AF_INET, []).append(address)
        else:
            i = ipaddress.IPv6Interface('%s/%s' % (ip.ip[0], ip.network_prefix))
            address = {'addr': str(i.ip), 'peer': str(i.ip), 'flags': 0, 'netmask': '%s/%s' % (str(i.netmask), ip.network_prefix)}
            #addresses.setdefault(AF_INET6, []).append(address)
    return addresses
#-> Mapping[int, Sequence[Mapping[str, str]]]: ...
