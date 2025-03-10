ifaddr - Enumerate network interfaces/adapters and their IP addresses
=====================================================================

.. image:: https://github.com/ifaddr/ifaddr/workflows/CI/badge.svg
    :target: https://github.com/ifaddr/ifaddr/actions?query=workflow%3ACI+branch%3Amaster

.. image:: https://img.shields.io/pypi/v/ifaddr.svg
    :target: https://pypi.python.org/pypi/ifaddr

.. image:: https://codecov.io/gh/ifaddr/ifaddr/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/ifaddr/ifaddr

`ifaddr` is a small Python library that allows you to find all the Ethernet and
IP addresses of the computer. It is tested on **Linux**, **OS X**, and
**Windows**. Other BSD derivatives like **OpenBSD**, **FreeBSD**, and
**NetBSD** should work too, but I haven't personally tested those.
**Solaris/Illumos** should also work.

This library is open source and released under the MIT License. It works
with Python 3.9+.

You can install it with `pip install ifaddr`. It doesn't need to
compile anything, so there shouldn't be any surprises. Even on Windows.

Project links:

* `ifaddr GitHub page <https://github.com/smurn/ifaddr>`_
* `ifaddr documentation (although there isn't much to document) <https://ifaddr.readthedocs.io>`_
* `ifaddr on PyPI <https://pypi.org/project/ifaddr/>`_


----------------------
Let's get going!
----------------------

.. code-block:: python

    import ifaddr

    adapters = ifaddr.get_adapters()

    for adapter in adapters:
        print("IPs of network adapter " + adapter.nice_name)
        for ip in adapter.ips:
            print("   %s/%s" % (ip.ip, ip.network_prefix))

This will print::

    IPs of network adapter H5321 gw Mobile Broadband Driver
       IP ('fe80::9:ebdf:30ab:39a3', 0L, 17L)/64
       IP 169.254.57.163/16
    IPs of network adapter Intel(R) Centrino(R) Advanced-N 6205
       IP ('fe80::481f:3c9d:c3f6:93f8', 0L, 12L)/64
       IP 192.168.0.51/24
    IPs of network adapter Intel(R) 82579LM Gigabit Network Connection
       IP ('fe80::85cd:e07e:4f7a:6aa6', 0L, 11L)/64
       IP 192.168.0.53/24
    IPs of network adapter Software Loopback Interface 1
       IP ('::1', 0L, 0L)/128
       IP 127.0.0.1/8

You get both IPv4 and IPv6 addresses. The later complete with
flowinfo and scope_id.

If you wish to include network interfaces that do not have a configured IP
address, pass the `include_unconfigured` parameter to `get_adapters()`.
Adapters with no configured IP addresses will have an zero-length `ips`
property.  For example:

.. code-block:: python

    import ifaddr

    adapters = ifaddr.get_adapters(include_unconfigured=True)

    for adapter in adapters:
        print("IPs of network adapter " + adapter.nice_name)
        if adapter.ips:
            for ip in adapter.ips:
                print("   %s/%s" % (ip.ip, ip.network_prefix))
        else:
            print("  No IPs configured")

------------
Alternatives
------------

Alastair Houghton develops `netifaces  <https://pypi.python.org/pypi/netifaces>`_
which can do  everything this library can, and more. The only drawback is that it needs
to be compiled, which can make the installation difficult.

As of ifaddr 0.2.0 we implement the equivalent of `netifaces.interfaces()`. It's available through
`ifaddr.netifaces.interfaces()`.
