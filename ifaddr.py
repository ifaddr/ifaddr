# Copyright (C) 2014 Stefan C. Mueller


from ifaddr_win32 import enumerate_interfaces


print "\n".join(map(str,enumerate_interfaces()))