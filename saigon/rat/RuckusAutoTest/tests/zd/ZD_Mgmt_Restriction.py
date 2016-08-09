'''
ZD Manageability
7.1 Basic Function
7.1.1    Restriction - Single
7.1.2    Restriction - Range
7.1.3    Restriction - Subnet
11.1.9   Deny-  Multicast IP addr / range / subnet

Single:
To verify the ZD management IP address can work properly when the remote PC
match the single IP address then it can access ZD. In other word, the remote PC
doesn't match the single IP then it could not access ZD.

1. Input a ip.addr (0.0.0.0) into the field.
2. Input an invalid ip.addr (255.255.255.255) into the field.
3. Input a subnet (10.1.1.0) into the field.
4. Create an entry with single IP x.x.x.x, verifing it only allows this
   single IP to manage ZD via HTTP/HTTPS, SSH and SNMP.

Range:
1. Input a range (0.0.0.0 ~ 255.255.255.255) into the field. (ZD should block)
2. Input a decrease range (10.1.1.200 ~ 10.1.1.100) into the field. (ZD should block)
3. Input a subnet (10.1.1.0 ~ 10.1.1.255) into the field. (ZD should block)
4. Create an entry with IP range x.x.x.x - x.x.x.x, verifing it only allows
   IP which in the range can manage ZD via HTTP/HTTPS, SSH and SNMP

Subnet:
1. Input a subnet (0.0.0.0 / 0) into the field. (ZD should block)
2. Input a specify ip (10.1.1.200 / 32) into the field. (ZD should block)
3. Input an invalid subnet (255.255.255.255 / 24) into the field. (ZD should block)
4. Create an entry with IP subnet x.x.x.x/x, verifing it only allows IP which
   in the subnet can manage ZD via HTTP/HTTPS, SSH and SNMP.

Deny - Multicast:
Verify the multicast ip should not be allowed to add-in and will have a
warning message.
1. IP addr : pick anyone between 224.0.0.1 ~ 239.255.255.255.
2. Range : 224.0.0.1 ~ 239.255.255.255
3. Subnet : 224.0.0.0 / 8 ; 239.255.0.0 / 16 ; 224.0.0.1 / 24 ;
   239.255.255.255 / 30


Implementation:
. the pass/fail is given on config so that the script just detect the pass/fail
  accordingly
. in wrong input cases, the entry is not created as well as a warning message is
  expected

config:
. params:
  . zd_mgmt
  . is_valid: boolean
. all entry removal

test:
. if is_valid:
  . entry can be created
  . lauch a webUI access and this can be accessible
. else:
  . error msg detected
  . entry is not created

clean up:
. all entry removal
. re_nav

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_zd_by_ip_addr

class ZD_Mgmt_Restriction(Test):

    def config(self, conf):
        '''
        . removing all mgmt access ctrl
        '''
        self.zd = self.testbed.components['ZoneDirector']
        self.p = conf
        logging.info('Removing all the current item in management access'
                     ' control list')
        lib.zd.sys.delete_all_mgmt_access_ctrls(self.zd)


    def test(self):
        '''
        . first create the mgmt access ctrl
        . then get all the mgmt access ctrl and make sure it is created correctly
        '''
        logging.info('Creating a ZD Management Access Control')
        try:
            lib.zd.sys.create_mgmt_access_ctrl(self.zd, self.p['zd_mgmt'])
        except:
            if self.p['is_valid']:
                return ['FAIL', 'Unable to create mgmt access control']

        self.zd.re_navigate()
        logging.info('Getting all of ZD Management Access Controls')
        mgmt_acs = lib.zd.sys.get_all_mgmt_access_ctrls(self.zd)

        if not self.p['is_valid']:
            if len(mgmt_acs) == 0:
                return ['PASS', 'No entry is created']
            else:
                return ['FAIL', 'Entry is created although invalid params given']

        if len(mgmt_acs) != 1:
            return ['FAIL',
                    'Expecting only one management access control.'
                    ' %s is found' % len(mgmt_acs)]

        mgmt_ac = lib.zd.sys.get_mgmt_access_ctrl(self.zd, self.p['zd_mgmt']['name'])
        if mgmt_ac != self.p['zd_mgmt']:
            return ['FAIL',
                    'The created Mgmt Access Ctrl is different from input']

        return self._test_launch_webui()


    def cleanup(self):
        '''
        . remove all the mgmt access ctrl
        '''
        logging.info('Removing all the current item in management access'
                     ' control list')
        lib.zd.sys.delete_all_mgmt_access_ctrls(self.zd)
        self.zd.re_navigate()


    def _test_launch_webui(self):
        try:
            zd = create_zd_by_ip_addr(self.zd.conf['ip_addr'])
            zd.destroy()
        except:
            return ['FAIL', 'Unable to launch ZD web UI']

        return ['PASS', 'Management Access Control is created successfully']

