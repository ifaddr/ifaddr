# Copyright (C) 2014 Stefan C. Mueller

class Interface(object):
    
    def __init__(self, name, ip, network_prefix, nice_name):
        
        #: Unique name of this interface.
        self.name = name
        
        #: IP address in string representation
        self.ip = ip
        
        #: Number of bits of the network part (netmask)
        self.network_prefix = network_prefix
        
        #: Human readable name for this interface.
        self.nice_name = nice_name
        
    def __repr__(self):
        return "Interface(name={name}, ip={ip}, network_prefix={network_prefix}, nice_name={nice_name})".format(
            name=self.name,
            ip=self.ip,
            network_prefix=self.network_prefix,
            nice_name=self.nice_name
        )
        