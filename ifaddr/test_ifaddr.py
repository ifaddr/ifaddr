# Copyright (C) 2015 Stefan C. Mueller

import ipaddress
import sys
import unittest
from unittest import mock

import pytest

import ifaddr
import ifaddr.netifaces
from ifaddr._shared import ipv6_prefixlength

try:
    import netifaces
except ImportError:
    skip_netifaces = True
else:
    skip_netifaces = False


class TestIfaddr(unittest.TestCase):
    """
    Unittests for :mod:`ifaddr`.

    There isn't much unit-testing that can be done without making assumptions
    on the system or mocking of operating system APIs. So this just contains
    a sanity check for the moment.
    """

    def test_get_adapters_contains_localhost(self) -> None:
        found = False
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            for ip in adapter.ips:
                if ip.ip == '127.0.0.1':
                    found = True

        self.assertTrue(found, 'No adapter has IP 127.0.0.1: %s' % str(adapters))


@pytest.mark.skipif(skip_netifaces, reason='netifaces not installed')
def test_netifaces_compatibility() -> None:
    interfaces = ifaddr.netifaces.interfaces()
    assert interfaces == netifaces.interfaces()
    # TODO: implement those as well
    # for interface in interfaces:
    #     print(interface)
    #     assert ifaddr.netifaces.ifaddresses(interface) == netifaces.ifaddresses(interface)
    # assert ifaddr.netifaces.gateways() == netifaces.gateways()


def test_ipv6_prefixlength() -> None:
    assert (
        ipv6_prefixlength(ipaddress.IPv6Address('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')) == 128
    )
    assert ipv6_prefixlength(ipaddress.IPv6Address('ffff:ffff:ffff:ffff::')) == 64


def test_load_libc_falls_back_to_find_library() -> None:
    if sys.platform == 'win32':
        pytest.skip('POSIX-only libc loading')

    import ctypes
    import ctypes.util

    import ifaddr._posix

    real_libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)

    def fake_cdll(name: object, *args: object, **kwargs: object) -> object:
        # The process-wide handle does not expose getifaddrs here, so the
        # find_library fallback path must run.
        if name is None:
            return object()
        return real_libc

    with mock.patch.object(ifaddr._posix.ctypes, 'CDLL', side_effect=fake_cdll):
        libc = ifaddr._posix._load_libc()

    assert hasattr(libc, 'getifaddrs')
