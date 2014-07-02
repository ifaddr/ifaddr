# Copyright (C) 2014 Stefan C. Mueller


import os

if os.name == "nt":
    from ifaddr_win32 import enumerate_interfaces
elif os.name == "posix":
    from ifaddr_posix import enumerate_interfaces
else:
    raise RuntimeError("Unsupported Operating System: %s" % os.name)

print "\n".join(map(str,enumerate_interfaces()))