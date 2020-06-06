# Copyright (C) 2015 Stefan C. Mueller

import netifaces
import unittest
import ifaddr
import ifaddr.netifaces


class TestIfaddr(unittest.TestCase):
    """
    Unittests for :mod:`ifaddr`.

    There isn't much unit-testing that can be done without making assumptions
    on the system or mocking of operating system APIs. So this just contains
    a sanity check for the moment.
    """

    def test_get_adapters_contains_localhost(self):

        found = False
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            for ip in adapter.ips:
                if ip.ip == "127.0.0.1":
                    found = True

        self.assertTrue(found, "No adapter has IP 127.0.0.1: %s" % str(adapters))


def test_netifaces_emulation():
    # address_families = ifaddr.netifaces.address_families
    # assert address_families == netifaces.address_families
    # for numeric, name in address_families.items():
    #     print(name, numeric)
    #     assert getattr(ifaddr.netifaces, name) == numeric
    #     assert getattr(ifaddr.netifaces, name) == getattr(netifaces, name)
    interfaces = ifaddr.netifaces.interfaces()
    assert interfaces == netifaces.interfaces()
    # TODO: implement those:
    # for interface in interfaces:
    #     print(interface)
    #     assert ifaddr.netifaces.ifaddresses(interface) == netifaces.ifaddresses(interface)
    # assert ifaddr.netifaces.gateways() == netifaces.gateways()
