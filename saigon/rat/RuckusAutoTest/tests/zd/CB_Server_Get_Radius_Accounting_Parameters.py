# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""
This script is used to get the accounting information of a client.
Input:  None
Output: Result PASS(the information will be put in the carrierBag),or FAIL(some of the values can not be got).

Note:   This script "CB_ZD_Start_Radius_Server_Nohup" must be executed before this one.

Author: chen.tao@odc-ruckuswireless.com
Since:2013-05-17

Example:

#        User-Name = "ras.eap.user"
#        Acct-Status-Type = Start
#        Acct-Authentic = RADIUS
#        Framed-IP-Address = 192.168.0.125
#        Calling-Station-Id = "00-15-00-62-C6-E4"
#        NAS-IP-Address = 192.168.0.2
#        NAS-Port = 39
#        Called-Station-Id = "C0-8A-DE-3C-B8-BC:chentaohotspot"
#        NAS-Port-Type = Wireless-802.11
#        NAS-Identifier = "C0-8A-DE-3C-B8-BC"
#        Connect-Info = "CONNECT 802.11a/n"
#        Acct-Session-Id = "51A4FD44-00000039"
#        Acct-Multi-Session-Id = "c08ade3cb8bc00150062c6e45195ca700038"
#        Vendor-25053-Attr-3 = 0x6368656e74616f686f7473706f74

"""
import re
import logging
import traceback
from RuckusAutoTest.models import Test

class CB_Server_Get_Radius_Accounting_Parameters(Test):

    required_components = ['LinuxServer']
    parameters_description = {}
        
    def config(self,conf):        
        self._initTestParameters(conf)
            
    def test(self):
        try:
            log_data = self.server.get_radius_server_log_detail(clear_log=self.conf['clear_log'])
            logging.info('Radius accounting parameters retrieved on radius server is:%s'%log_data)
        except Exception, e:
            logging.error(traceback.format_exc())  
            return self.returnResult('FAIL', e.message)
        param_dict = self._parse_parameters(log_data)
        if param_dict:
            self.passmsg = 'Get Radius parameters successfully'
            self.carrierbag['Radius_Acc'] = param_dict
            return self.returnResult('PASS', self.passmsg)
        else:
            return self.returnResult('FAIL', self.errmsg)
                           
    def oncleanup(self):
        pass
    
    def _initTestParameters(self,conf):
        self.conf = {'clear_log':True}
        self.conf.update(conf)
        self.server = self.testbed.components['LinuxServer']
        self.errmsg = ''
        self.passmsg = ''

    def _parse_parameters(self,data):
        parameters = {'User-Name' : '',
                      'Acct-Status-Type' : '',
                      'Acct-Authentic' : '',
                      'Framed-IP-Address' : '',
                      'Calling-Station-Id' : '',
                      'NAS-IP-Address' : '',
                      'NAS-Port' : '',
                      'Called-Station-Id' : '',
                      'NAS-Port-Type' : '',
                      'NAS-Identifier' : '',
                      'Connect-Info' : '',
                      'Acct-Session-Id' : '',
                      'Acct-Multi-Session-Id' : '',
                      'Vendor-25053-Attr-3' : ''}
        for parameter in parameters.keys():
            print "Now getting the value of %s"%parameter
            pattern = '%s = (.+)'%parameter
            match_obj = re.search(pattern,data)
            if match_obj:
                result = match_obj.group(1).strip()
                parameters[parameter] = result.strip('"')
            else:
                if parameter == 'Acct-Session-Id':
                    parameters.pop(parameter)
                else:
                    self.errmsg = "Cannot get the value of %s"%parameter
                    logging.info(self.errmsg)
                    return None
        return parameters
