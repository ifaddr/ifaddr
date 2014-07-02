'''
Created on 02.07.2014

@author: stefan
'''

import ifaddr

adapters = ifaddr.get_adapters()

for adapter in adapters:
    print "IPs of network adapter " + adapter.nice_name
    for ip in adapter.ips:
        print "   IP %s/%s" % (ip.ip, ip.network_prefix)