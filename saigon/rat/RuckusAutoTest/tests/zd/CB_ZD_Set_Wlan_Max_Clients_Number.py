import logging
from random import randint

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.wlan_zd import set_wlan_max_clients_number as web_set_number
from RuckusAutoTest.components.lib.zdcli.get_wlan_info import get_max_clients_number as cli_get_number

class CB_ZD_Set_Wlan_Max_Clients_Number(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('set wlan max clients number in web UI')
        web_set_number(self.zd,self.conf['wlan_name'],self.conf['number'])
        
        logging.info('get model max clients number in CLI')
        number=cli_get_number(self.zdcli,self.conf['wlan_name'])
        
        if number!=self.conf['number']:
            self.errmsg='max client number not match web set %s cli get %s,'%(self.conf['number'],number)
        if self.errmsg:
            return self.returnResult('FAIL',self.errmsg)
        return self.returnResult('PASS', "set max clients number in web successfully and verify in cli ok")
    
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf={'wlan_name':'',
                   'number':'512',
                   }
        self.conf.update(conf)
        if self.conf['number'].lower()=='random':
            self.conf['number']=str(randint(1,511))
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        
    def _update_carrierbag(self):
        pass