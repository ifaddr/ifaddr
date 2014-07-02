'''
Created on 02.07.2014

@author: stefan
'''

import ifaddr

if __name__ == '__main__':
    
    
    print "\n".join(map(str, ifaddr.enumerate_interfaces()))