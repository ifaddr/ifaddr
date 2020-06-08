# Copyright (C) 2015 Stefan C. Mueller

import pprint
import unittest
import ifaddr

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


try:
    import netifaces
except ImportError:
    pass
else:
    def test_compare_gateways():
        print('ifaddr')
        print('======')
        print('Interfaces:')
        adapters = ifaddr.get_adapters(include_unconfigured=True)
        for adapter in adapters:
            print('index %d name %s. Gateways:' % (adapter.index, adapter.nice_name))
            for gateway in adapter.gateways:
                print('* %s' % (gateway,))
            print('IP-s:')
            for ip in adapter.ips:
                print('* %s' % (ip,))
            print()
        print()

        print('netifaces')
        print('=========')
        print('Interfaces:')
        print()
        for interface in netifaces.interfaces():
            pprint.pprint(netifaces.ifaddresses(interface))
            print()
        print()
        print('Gateways:')
        pprint.pprint(netifaces.gateways())

        assert False
