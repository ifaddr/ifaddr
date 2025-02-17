Changelog
=========

Not released yet
----------------

Removed:

* Dropped Python 3.7 and 3.8 support

0.2.0
-----

* Added an option to include IP-less adapters, thanks to memory
* Fixed a bug where an interface's name was `bytes`, not `str`, on Windows
* Added an implementation of `netifaces.interfaces()` (available through
  `ifaddr.netifaces.interfaces()`)
* Added type hints

Backwards incompatible/breaking changes:

* Dropped Python 3.6 support

0.1.7
-----

* Fixed Python 3 compatibility in the examples, thanks to Tristan Stenner and Josef Schlehofer
* Exposed network interface indexes in Adapter.index, thanks to Dmitry Tantsur
* Added the license file to distributions on PyPI, thanks to Tomáš Chvátal
* Fixed Illumos/Solaris compatibility based on a patch proposed by Jorge Schrauwen
* Set up universal wheels, ifaddr will have both source and wheel distributions on PyPI from now on
