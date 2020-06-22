# netifaces compatibility layer

import ifaddr


def interfaces():
    adapters = ifaddr.get_adapters(include_unconfigured=True)
    return [a.name for a in adapters]
