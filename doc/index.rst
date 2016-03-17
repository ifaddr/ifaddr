

ifaddr - Enumerate IP addresses on the local network adapters
=============================================================

`ifaddr` is a small Python library that allows you to find all the
IP addresses of the computer. It is tested on **Linux**, **OS X**, and
**Windows**.

This library is open source and released under the MIT License.

You can install it with `pip install ifaddr`. It doesn't need to
compile anything, so there shouldn't be any surprises. Even on Windows.

----------------------
Let's get going!
----------------------

.. code-block:: python

   import ifaddr
   
   adapters = ifaddr.get_adapters()
   
   for adapter in adapters:
       print "IPs of network adapter " + adapter.nice_name
       for ip in adapter.ips:
           print "   %s/%s" % (ip.ip, ip.network_prefix)
   
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

  .. py:attribute:: name

    Unique name that identifies the adapter in the system.
    On Linux this is of the form of `eth0` or `eth0:1`, on
    Windows it is a UUID in string representation, such as
    `{846EE342-7039-11DE-9D20-806E6F6E6963}`.

  .. py:attribute:: nice_name

    Human readable name of the adpater. On Linux this
    is currently the same as :attr:`name`. On Windows
    this is the name of the device.

  .. py:attribute:: ips

    List of :class:`ifaddr.IP` instances in the order they were
    reported by the system.

.. autoclass:: ifaddr.IP

  .. py:attribute:: ip

        IP address. For IPv4 addresses this is a string in
        "xxx.xxx.xxx.xxx" format. For IPv6 addresses this
        is a three-tuple `(ip, flowinfo, scope_id)`, where
        `ip` is a string in the usual collon separated
        hex format.

  .. py:attribute:: network_prefix

        Number of bits of the IP that represent the
        network. For a `255.255.255.0` netmask, this
        number would be `24`.

  .. py:attribute:: nice_name

        Human readable name for this IP.
        On Linux is this currently the same as the adapter name.
        On Windows this is the name of the network connection
        as configured in the system control panel.

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


