# Copyright (C) 2014 Stefan C. Mueller

import os

from ifaddr._shared import Interface

if os.name == "nt":
    from ifaddr._win32 import enumerate_interfaces
elif os.name == "posix":
    from ifaddr._posix import enumerate_interfaces
else:
    raise RuntimeError("Unsupported Operating System: %s" % os.name)

__all__ = ['Interface', 'enumerate_interfaces']
