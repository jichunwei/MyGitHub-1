# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Common utility functions for developing IPTV test cases
   Every function here should be able to run on both windows and linux platform
   
   *Note*: only functions that used for IPTV test cases are put here. 
"""

#import random
#import string
#import sys
#import time
#import os
#import glob
import ConfigParser
#import socket
#import copy
#import re
#import logging
#
#from Ratutils import *


def parseCustomProfile(profile_file):
    """
    parsing Ruckus custom profile, it ignore line start with '#' and empty line
    
    Output:
    - return a list custom setting lines
    """
    fprofile = open(profile_file)
    custom_lines = []
    for line in fprofile.read().splitlines():
        if not line.startswith("#") and line.strip():
            custom_lines.append(line)
    fprofile.close()

    return custom_lines

def loadCustomConfigFile(filename):
    """
    read custom configuration file. It section store default value of one custom profile    
    
    Output: 
    - return a dictionary of default value for each customer name
    
    Ex: 
    - custom_cfg['singtel'] = {'countrycode':'SG', 
                               'home_login':'admin'}
    """
    cfg_info = dict()
    cp   = ConfigParser.ConfigParser()
    cp.read(filename)
    for s in cp.sections():
        cfg_info[s] = dict()
        for i in cp.items(s):
            if i[1].strip().startswith("{"):
                cfg_info[s][i[0]] = eval(i[1])
            else:
                cfg_info[s][i[0]] = i[1]
    return cfg_info
