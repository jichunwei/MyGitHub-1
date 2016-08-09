# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""
This script is used to send disconnect message on radius server,and get the corresponding result.

Input: zd_ip_addr,shared_secret,type of disconnect message.
Output: the station is forced to disconnect or not.


Author: chen.tao@odc-ruckuswireless.com
Since:2013-05-19
"""
import re
import logging
from RuckusAutoTest.models import Test

class CB_Server_Send_Disconnect_Message(Test):

    required_components = ['LinuxServer']
    parameters_description = {'zd_ip_addr': 'the ip address of the zd',
                              'shared_secret': 'the shared secret of the radius server',
                              'choice': 'indicates the type of disconnect message to be sent',
                              'is_negative': 'negative test or not',
                              'sta_tag': 'the station tag',
                              'user_name': 'authentication username of the client'}

    def config(self, conf):        
        self._initTestParameters(conf)
            
    def test(self):
        result = self._send_radius_disconnect_message()
        pattern_success = 'Acct-Terminate-Cause = Admin-Reset'
        pattern_fail = 'Error-Cause = Session-Context-Not-Found'
        match_obj_success = re.search(pattern_success,result)
        match_obj_fail = re.search(pattern_fail,result)
        if not self.conf['is_negative']:
            if match_obj_success:
                return self.returnResult('PASS', 'Right,the client is forced to disconnect')
            elif match_obj_fail:
                return self.returnResult('FAIL', 'Wrong,the client is not forced to disconnect')
            else:
                return self.returnResult('FAIL', 'ZD does not response to the command or error occured')
        else:
            if match_obj_fail:
                return self.returnResult('PASS', 'Right,the client is not forced to disconnect')
            elif match_obj_success:
                return self.returnResult('FAIL', 'Wrong,the client is forced to disconnect')
            else:
                return self.returnResult('PASS', 'ZD does not response to the command or error occured')
            
    def oncleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.conf = {
                     'shared_secret':'1234567890',
                     'choice':'by_sta_mac',
                     'is_negative':False,
                     'sta_tag':'',
                     'user_name':''}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.conf['zd_ip_addr'] = self.zd.ip_addr
        self.server = self.testbed.components['LinuxServer']
        target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        target_station_mac = target_station.get_wifi_addresses()[1]
                
        if self.conf['sta_tag']:
            self.conf['sta_mac'] = target_station_mac
        #If mac address is used as the username:    
        if self.conf['choice']== 'by_user_name' and not self.conf['user_name']:
            #self.conf['user_name'] = target_station_mac.lower()
            #@author: chentao since: 2013-10-11 to adapt the behavior change of hotspot mac-bypass format                
            import itertools
            temp = target_station_mac.lower()
            temp = temp.split(':')
            self.conf['user_name'] = "".join(itertools.chain(temp))  
#@author: chentao since: 2013-10-11 to adapt the behavior change of hotspot mac-bypass format   
        if self.conf['choice']== 'by_user_name_dot1' and not self.conf['user_name']:
            self.conf['user_name'] = target_station_mac.upper().replace(':','-')    
        
    def _send_radius_disconnect_message(self):
    #cmd example:
    #echo Calling-Station-Id = "00-15-00-62-18-E0"|radclient -x 192.168.0.2:3799 disconnect "1234567890" 
    #echo User-Name = "ras.local.user"|radclient -x 192.168.0.2:3799 disconnect "1234567890"
    #echo Acct-Session-Id = "5074AE3E-00000001"|radclient -x 192.168.0.2:3799 disconnect "1234567890"
    #Send multiple attributes in one disconnect message:
    #echo Calling-Station-Id = "00-15-00-62-18-E0" >> /tmp/packet.txt
    #echo Acct-Session-Id= "5074AE3E-00000001" > /tmp/packet.txt
    #echo User-Name="ras.local.user" >> /tmp/packet.txt 
    #cat /tmp/packet.txt | radclient -x 192.168.0.2:3799 disconnect "1234567890"
        zd_ip_addr = self.conf['zd_ip_addr']
        shared_secret = self.conf['shared_secret']
        choice = self.conf['choice']
        logging.info("choice is: %s"%choice)        
        if choice == 'by_sta_mac':
            sta_mac = self.conf['sta_mac']
            cmd = 'echo Calling-Station-Id = "%s"|radclient -x %s:3799 disconnect "%s"'%(sta_mac,zd_ip_addr,shared_secret)
            logging.info("cmd is:%s"%cmd)            
        if choice == 'by_invalid_sta_mac':
            sta_mac = '00-00-00-00-00-00'
            cmd = 'echo Calling-Station-Id = "%s"|radclient -x %s:3799 disconnect "%s"'%(sta_mac,zd_ip_addr,shared_secret)

        choice_list = ['by_user_name','by_user_name_dot1','by_longest_user_name']            
        if choice in choice_list:
            user_name = self.conf['user_name']
            cmd = 'echo User-Name = "%s"|radclient -x %s:3799 disconnect "%s"'%(user_name,zd_ip_addr,shared_secret)
            logging.info("cmd is:%s"%cmd)  
            
        if choice == 'by_invalid_user_name':
            user_name = 'invalid.user'
            cmd = 'echo User-Name = "%s"|radclient -x %s:3799 disconnect "%s"'%(user_name,zd_ip_addr,shared_secret)

        if choice == 'by_invalid_suffix_user_name':
            user_name = self.conf['user_name'] + '.1'
            cmd = 'echo User-Name = "%s"|radclient -x %s:3799 disconnect "%s"'%(user_name,zd_ip_addr,shared_secret)
            logging.info("cmd is:%s"%cmd)  
            
        if choice == 'by_session_id':
            session_id = self.carrierbag['Radius_Acc']['Acct-Session-Id']    
            cmd = 'echo Acct-Session-Id = "%s"|radclient -x %s:3799 disconnect "%s"'%(session_id,zd_ip_addr,shared_secret)
            logging.info("cmd is:%s"%cmd)  
                        
        if choice == 'by_invalid_session_id':
            session_id = '11111111-11111111'
            cmd = 'echo Acct-Session-Id = "%s"|radclient -x %s:3799 disconnect "%s"'%(session_id,zd_ip_addr,shared_secret)

        if choice == 'by_invalid_format_session_id':
            id = self.carrierbag['Radius_Acc']['Acct-Session-Id']
            location = id.find('-')
            id = list(id)
            del id[location]
            session_id = ''.join(id)
            cmd = 'echo Acct-Session-Id = "%s"|radclient -x %s:3799 disconnect "%s"'%(session_id,zd_ip_addr,shared_secret)
            
#        if choice == 'by_all':
#            sta_mac = self.conf['sta_mac']
#            logging.info("Calling-Station-Id is %s"%sta_mac)
#            user_name = self.conf['user_name']
#            logging.info("User_Name is %s"%user_name)
#            session_id = self.carrierbag['Radius_Acc']['Acct-Session-Id']
#            logging.info("Acct-Session-Id is %s"%session_id)    
#            cmd1 = 'echo Calling-Station-Id = "%s" > /tmp/packet.txt'%sta_mac
#            self.server.cmd(cmd1)
#            cmd2 = 'echo Acct-Session-Id = "%s" >> /tmp/packet.txt'%session_id
#            self.server.cmd(cmd2)
#            cmd3 = 'echo User-Name = "%s" >> /tmp/packet.txt'%user_name
#            self.server.cmd(cmd3)
#            cmd  = 'cat /tmp/packet.txt | radclient -x %s:3799 disconnect "%s"'%(zd_ip_addr,shared_secret)

#        if choice == 'by_invalid_all':
#            sta_mac = '00-00-00-00-00-00'
#            logging.info("Calling-Station-Id is %s"%sta_mac)
#            user_name = 'invalid.user'
#            logging.info("User_Name is %s"%user_name)
#            session_id = '11111111-11111111'
#            logging.info("Acct-Session-Id is %s"%session_id)   
#            cmd1 = 'echo Calling-Station-Id = "%s" > /tmp/packet.txt'%sta_mac
#            self.server.cmd(cmd1)
#            cmd2 = 'echo Acct-Session-Id= "%s" >> /tmp/packet.txt'%session_id
#            self.server.cmd(cmd2)
#            cmd3 = 'echo User-Name="%s" >> /tmp/packet.txt'%user_name
#            self.server.cmd(cmd3)
#            cmd  = 'cat /tmp/packet.txt | radclient -x %s:3799 disconnect "%s"'%(zd_ip_addr,shared_secret)
            
        result =  self.server.cmd(cmd)
        return ''.join(result)