import socket
from pprint import pprint

try:
    socket.if_nameindex
except AttributeError:
    pass
else:
    indexes_names = socket.if_nameindex()
    pprint(indexes_names)
    print()
    for index, name in indexes_names:
        try:
            indextoname_result = socket.if_indextoname(index)
        except OSError:
            indextoname_result = '<error>'
        try:
            nametoindex_result = socket.if_nametoindex(name)
        except OSError:
            nametoindex_result = '<error>'
        print('index %s, name %s, indextoname result %s, nametoindex result %s' % (index, name, indextoname_result, nametoindex_result))

print()
import ifaddr
pprint(list(ifaddr.get_adapters()))
