# Copyright (C) 2014 Stefan C. Mueller

import os

from ifaddr._shared import Adapter, IP

if os.name == "nt":
    from ifaddr._win32 import get_adapters
elif os.name == "posix":
    from ifaddr._posix import get_adapters
else:
    raise RuntimeError("Unsupported Operating System: %s" % os.name)

__all__ = ['Adapter', 'IP', 'get_adapters']
