# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""
This script is used to add or delete radius users on the server.
There are two lists, one including the users to be created,the other including users to be deleted.
Input the users in this format:
[(user_name,password,use_mac,mac_format),(user_name,password,use_mac,mac_format),...]

"user_name" is the user you want to add.
It can be the sta_tag when you need to use the mac address as the username.

"password" is the password of the user.
Also,it can be the sta_tag, meaning that mac address will be used as password.

"use_mac" can be True or False,means whether or not use station mac as username.
When the value is True,user_name is the station tag.

"mac_format": can be None or 'dot1',
        'dot1' means to use the station's mac in 802.1 format,eg,4C-00-10-A2-27-F4.
        None means to use the station's mac in default format,eg,4c:00:10:a2:27:f4,, or use the string you specified.

Here is an example:
conf['add_user'] = [('ras.eap.user','ras.eap.user',False,None),('sta1','sta1',True,'dot1'),
                    ('sta2','my_pwd',True,None),('sta3','sta3',True,None)]
					
conf['del_user'] = [('ras.eap.user','ras.eap.user',False,None),('sta1','sta1',True,'dot1'),
                    ('sta2','my_pwd',True,None),('sta3','sta3',True,None)]
					
You can add some users and delete other users using just this one script.
Just provide the add_user list and del_user list

Author: chen.tao@odc-ruckuswireless.com
Since:2013-06-08
"""

import logging
import time
from RuckusAutoTest.models import Test

class CB_Server_Add_And_Delete_Radius_Users(Test):

    required_components = ['LinuxServer']
    parameters_description = {'add_user': 'the list of users to be added',
                              'del_user': 'the list of users to be deleted',}
    def config(self, conf):        
        self._initTestParameters(conf)
            
    def test(self):
        add_user_list = self.conf['add_user']
        del_user_list = self.conf['del_user']
        self._add_and_del_users(add_user_list,del_user_list)
        
        if self.passmsg:
            return self.returnResult('PASS', self.passmsg)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
       
    def oncleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.conf = {'add_user':[],
                     'del_user':[],} 
        self.conf.update(conf)
        self.server = self.testbed.components['LinuxServer'] 
        self.passmsg = ''
        self.errmsg = ''      
        
    def _add_and_del_users(self,add_user_list=[],del_user_list=[]):

        self.server.cmd('cd /etc/raddb')
        index = 0
        for user in add_user_list:
            if len(user) == 4:
                user = user + (None,None,False)
            elif len(user) == 5:
                user = user + (None,False)
            elif len(user) == 6:
                user = user + (False,)
            add_user_list[index] = user
            index += 1
        index = 0
        for user in del_user_list:           
            if len(user) == 4:
                user = user + (None,None,False)
            elif len(user) == 5:
                user = user + (None,False)
            elif len(user) == 6:
                user = user + (False,)
            del_user_list[index] = user
            index += 1

        for user_name,password,use_mac,mac_format,vlan,role,eap_type in add_user_list:
            if not user_name or not password:
                self.errmsg = 'Error:username or password is NULL'
                logging.info(self.errmsg)
                return self.errmsg
            if use_mac:        	
                if self.carrierbag.get(user_name):
                    logging.info('Will use station mac as username')
                    target_station = self.carrierbag[user_name]['sta_ins']
                    target_station_mac = target_station.get_wifi_addresses()[1]
                    if mac_format == 'dot1':
                        user_name = target_station_mac.replace(':','-')
                    else:
                        user_name = target_station_mac.lower().replace(':','')
#                else:
#                    self.errmsg = '[user_name]sta_tag: %s is not found in the carrier_bag.'%user_name
#                    logging.info(self.errmsg)
#                    return self.errmsg
                    
                if self.carrierbag.get(password):
                    logging.info('Will use station mac as password')
                    target_station = self.carrierbag[password]['sta_ins']
                    target_station_mac = target_station.get_wifi_addresses()[1]
                    if mac_format == 'dot1':
                        password = target_station_mac.replace(':','-')
                    else:
                        password = target_station_mac.lower().replace(':','')                    
#                else:
#                    self.errmsg = '[password]sta_tag: %s is not found in the carrier_bag.'%user_name
#                    logging.info(self.errmsg)
#                    return self.errmsg

            if eap_type:
                user_info = '%s User-Password == %s'%(user_name,password)
            else:
                user_info = '%s Auth-Type := Local, User-Password == %s'%(user_name,password)
            
            

            logging.info('user_info is:%s'%user_info)
            result = self.server.cmd("grep '^\(%s\)' users" %user_name)
            logging.info('result is:%s'%result)
            if user_info in result:
                logging.info('user:%s,password:%s already exists,do nothing'%(user_name,password))
                continue

            logging.info('adding user:%s,password:%s'%(user_name,password))
            cmd = 'echo %s >> users'%(user_info)
            self.server.cmd(cmd)

            if vlan:
                vlan_info = '\\\\tAcct-Interim-Interval = 180,'
                cmd = 'echo -e %s >> users'%(vlan_info)
                self.server.cmd(cmd) 
 
                vlan_info = '\\\\tTunnel-Type = VLAN,'
                cmd = 'echo -e %s >> users'%(vlan_info)
                self.server.cmd(cmd)

                vlan_info = '\\\\tTunnel-Medium-Type = IEEE-802,'
                cmd = 'echo -e %s >> users'%(vlan_info)
                self.server.cmd(cmd)                
                
                vlan_info = '\\\\tTunnel-Private-Group-ID = %s,'%vlan
                cmd = 'echo -e %s >> users'%(vlan_info)
                self.server.cmd(cmd)  
                
            if role:
                role_info = 'cisco-avpair = \\\"shell:roles=\\\\\\"%s\\\\\\"\\\"'%role               
                cmd = 'echo "        " %s >> users'%(role_info)
                self.server.cmd(cmd)
                
            result = self.server.cmd("grep '^\(%s\)' users" %user_name)
            logging.info('result is:%s'%result)

            if user_info in result:
                logging.info('user:%s,password:%s is added'%(user_name,password))
            else: 
                logging.info('user:%s is not added'%user_name)
                self.errmsg = 'user:%s is not added'%user_name
                return self.errmsg
            
        for user_name,password,use_mac,mac_format,vlan,role,eap_type in del_user_list:
            if not user_name or not password:
                self.errmsg = 'Error:username or password is NULL'
                logging.info(self.errmsg)
                return self.errmsg
            if use_mac:        	
                if self.carrierbag.get(user_name):
                    logging.info('Will use station mac as username')
                    target_station = self.carrierbag[user_name]['sta_ins']
                    target_station_mac = target_station.get_wifi_addresses()[1]
                    if mac_format == 'dot1':
                        user_name = target_station_mac.replace(':','-')
                    else:
                        user_name = target_station_mac.lower().replace(':','')
#                else:
#                    self.errmsg = '[user_name]sta_tag: %s is not found in the carrier_bag.'%user_name
#                    logging.info(self.errmsg)
#                    return self.errmsg
                    
                if self.carrierbag.get(password):
                    logging.info('Will use station mac as password')
                    target_station = self.carrierbag[password]['sta_ins']
                    target_station_mac = target_station.get_wifi_addresses()[1]
                    if mac_format == 'dot1':
                        password = target_station_mac.replace(':','-')
                    else:
                        password = target_station_mac.lower().replace(':','')                    
#                else:
#                    self.errmsg = '[password]sta_tag: %s is not found in the carrier_bag.'%user_name
#                    logging.info(self.errmsg)
#                    return self.errmsg        
                    
            user_info = '%s Auth-Type := Local, User-Password == %s'%(user_name,password)

            if vlan or role:
                result = self.server.cmd("grep -n -A 8 '^\(%s\)' users" %user_name)
            else:
                result = self.server.cmd("grep -n '^\(%s\)' users" %user_name)

            import re                
            logging.info('result is:%s'%result)
            user_info_re = "(\d+):%s"%user_name

            if len(result) > 1:            
                if not re.match(user_info_re,result[1]):
                    logging.info('user:%s,password:%s does not exist,do nothing'%(user_name,password))
                    continue
            else:
                logging.info('user:%s,password:%s does not exist,do nothing'%(user_name,password))
                continue

               
            logging.info('deleting user:%s,password:%s'%(user_name,password))
            match_line_start = int(re.match(user_info_re,result[1]).groups(0)[0])
            match_line_stop = match_line_start
            for i in result[2:]:
                if re.match("^(\d*)[-:][^\s]+.+",i):
                    match_line_stop = int(re.match("^(\d*)[-:][^\s]+.+",i).groups(0)[0]) - 1
                    break
                else:
                    match_line_stop += 1
                    
            logging.info('deleting line %s --- line %s'%(match_line_start,match_line_stop)) 
            cmd = "sed -i '%s,%sd' users"%(match_line_start,match_line_stop)
            self.server.cmd(cmd)            

            
            result = self.server.cmd("grep '^\(%s\)' users" %user_name)
            logging.info('result is:%s'%result)
            if user_info not in result:
                logging.info('Success,user:%s,password:%s is deleted'%(user_name,password))
            else:
                logging.info('user:%s is not deleted'%user_name)
                self.errmsg = 'user:%s is not deleted'%user_name
                return self.errmsg
        time.sleep(5)                        
        logging.info('restart radius to take effect!')
        self.server.cmd('su -\n')
        self.server.cmd('service radiusd restart')
        time.sleep(1)
        self.server.cmd('su root')
        self.passmsg = "All specified radius users have been added or deleted."
        return self.passmsg
