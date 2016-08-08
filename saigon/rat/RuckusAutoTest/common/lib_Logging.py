# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
Support to generate and log the message follow format
"""

import logging

#
# LOG MESSAGE TEMPLATE
#

INFO_TYPE = {0: '',
             1: '[RESULT]',
             2: '[STATUS]'}

DEBUG_TYPE = {0: 'UNKNOW ERROR',
              1: 'ERROR',
              2: 'EXCEPTION'}

DEBUG_MSG = '[%s][%s][%s]: %s'

INFO_MSG = '[%s][%s]%s %s'

#
# PUBLIC FUNCTION
#

def log_info(obj_name, action, message, info_type = 0):
    msg = INFO_MSG % (obj_name.upper(), action.upper(), INFO_TYPE[info_type], message)
    logging.info(msg)

def log_debug(obj_name, action, message, debug_type = 0):
    msg = DEBUG_MSG % (obj_name.upper(), action.upper(), DEBUG_TYPE[debug_type], message)
    logging.debug(msg)
    
    if debug_type in [2]:
        raise Exception, msg