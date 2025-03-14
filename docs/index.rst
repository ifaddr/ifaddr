

ifaddr - Enumerate IP addresses on the local network adapters
=============================================================

`ifaddr` is a small Python library that allows you to find all the
IP addresses of the computer. It is tested on **Linux**, **OS X**, and
**Windows**. Other BSD derivatives like **OpenBSD**, **FreeBSD**, and
**NetBSD** should work too, but I haven't personally tested those.

This library is open source and released under the MIT License.

You can install it with `pip install ifaddr`. It doesn't need to
compile anything, so there shouldn't be any surprises. Even on Windows.

.. toctree::
    :maxdepth: 1

    changelog

----------------------
Let's get going!
----------------------

.. code-block:: python

   import ifaddr

   adapters = ifaddr.get_adapters()

   for adapter in adapters:
       print ("IPs of network adapter " + adapter.nice_name)
       for ip in adapter.ips:
           print ("   %s/%s" % (ip.ip, ip.network_prefix))

This will print:

.. code-block:: none

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

-----
API
-----

The library has only one function:

.. py:function:: ifaddr.get_adapters()

   Receives all the network adapters with their IP addresses.

   :returns: List of :class:`ifaddr.Adapter` instances in the order
     they are provided by the operating system.

And two simple classes:

.. autoclass:: ifaddr.Adapter
   :members: name, ips, nice_name, index, multicast

.. autoclass:: ifaddr.IP
   :members: ip, network_prefix, nice_name, is_IPv4, is_IPv6

-----------------------------------
Bug Reports and other contributions
-----------------------------------

This project is hosted here `ifaddr github page <https://github.com/smurn/ifaddr>`_.

------------
Alternatives
------------

Alastair Houghton develops `netifaces  <https://pypi.python.org/pypi/netifaces>`_
which can do  everything this library can, and more. The only drawback is that it needs
to be compiled, which can make the installation difficult.


