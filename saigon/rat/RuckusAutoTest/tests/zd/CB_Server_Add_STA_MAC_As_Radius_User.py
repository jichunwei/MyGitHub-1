'''
Created on Apr 22, 2014

@author: lz
'''
import logging
import time
from RuckusAutoTest.models import Test

class CB_Server_Add_STA_MAC_As_Radius_User(Test):

    required_components = ['LinuxServer']
    parameters_description = {'sta_tag': 'the station tag',
                              'mac_format_type': 'the mac format type, 1,2,3,4,5,6'}
    def config(self, conf):        
        self._initTestParameters(conf)
            
    def test(self):
        if self.mac_format_type != 'all_formats':
            self._add_user()
        else:
            all_formats = ['aabbccddeeff',
                           'AABBCCDDEEFF',
                           'aa:bb:cc:dd:ee:ff',
                           'AA:BB:CC:DD:EE:FF',
                           'aa-bb-cc-dd-ee-ff',
                           'AA-BB-CC-DD-EE-FF']
            for a_format in all_formats:
                self.mac_format_type = a_format
                self._add_user()
        if self.passmsg:
            return self.returnResult('PASS', self.passmsg)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
       
    def oncleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.conf = {'sta_tag':'',
                     'mac_format_type':'',} 
        self.conf.update(conf)
        self.server = self.testbed.components['LinuxServer'] 
        self.passmsg = ''
        self.errmsg = ''
        self.sta_tag = self.conf['sta_tag']
        self.mac_format_type = self.conf['mac_format_type']
        
    def _get_mac_user(self):
        if not self.sta_tag or not self.carrierbag.get(self.sta_tag):
            logging.info('No sta_tag is provided or cannot get station instance from carrierbag')
            return
        else:
            logging.info('Will use station mac as username')
            target_station = self.carrierbag[self.sta_tag]['sta_ins']
            target_station_mac = target_station.get_wifi_addresses()[1]
        if not self.mac_format_type:
            logging.info('No mac format type is provided!')
            return
        elif self.mac_format_type == 'aa:bb:cc:dd:ee:ff': 
            mac_addr = target_station_mac.lower()
        elif self.mac_format_type == 'AA:BB:CC:DD:EE:FF': 
            mac_addr = target_station_mac.upper()
        elif self.mac_format_type == 'aa-bb-cc-dd-ee-ff': 
            mac_addr = target_station_mac.lower().replace(':','-')
        elif self.mac_format_type == 'AA-BB-CC-DD-EE-FF': 
            mac_addr = target_station_mac.upper().replace(':','-')
        elif self.mac_format_type == 'aabbccddeeff': 
            mac_addr = ''.join(target_station_mac.lower().split(':'))
        elif self.mac_format_type == 'AABBCCDDEEFF': 
            mac_addr = ''.join(target_station_mac.upper().split(':'))
        return mac_addr
        
    def _add_user(self):
        user_name = password = self._get_mac_user()
        if not user_name:
            self.errmsg = 'Cannot add user, because no user can be parsed'
            return
        else:
            self.server.cmd('cd /etc/raddb') 
            user_info = '%s Auth-Type := Local, User-Password == %s'%(user_name,password)
            logging.info('user_info is:%s'%user_info)
            logging.info('Check if user %s exists in radius server'%(user_name))
            result = self.server.cmd("grep '^\(%s\)' users" %user_name)
            logging.info('result is:%s'%result)
            if user_info in result:
                logging.info('user:%s,password:%s already exists,deleting it'%(user_name,password))
                cmd = "sed -i '/^%s/d' users"%(user_info)
                self.server.cmd(cmd)
            logging.info('adding user:%s,password:%s'%(user_name,password))
            cmd = 'echo %s >> users'%(user_info)
            self.server.cmd(cmd)
            result = self.server.cmd("grep '^\(%s\)' users" %user_name)
            logging.info('result is:%s'%result)
            if user_info in result:
                logging.info('user:%s,password:%s is added'%(user_name,password))
            else: 
                logging.info('user:%s is not added'%user_name)
                self.errmsg = 'user:%s is not added'%user_name
                return self.errmsg
            time.sleep(5)                        
            logging.info('restart radius to take effect!')
            self.server.cmd('service radiusd restart')
            self.passmsg = "The specified radius user has been added."
            return
