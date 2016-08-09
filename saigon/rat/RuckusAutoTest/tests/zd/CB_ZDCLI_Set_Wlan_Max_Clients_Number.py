import logging
from random import randint

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.wlan_zd import get_wlan_max_clients_number as web_get_number
from RuckusAutoTest.components.lib.zdcli.set_wlan import set_max_client as cli_set_number

class CB_ZDCLI_Set_Wlan_Max_Clients_Number(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('set wlan max clients number in ClI (%s)'%self.conf['number'])
        try:
            cli_set_number(self.zdcli,self.conf['wlan_name'],self.conf['number'])
        except Exception,e:
            if self.conf['number'] == '0' and 'The Max. client value must be a number between 1 and 512.' in e.message:
                pass
            elif int(self.conf['number']) > 512 and 'The Max. client value must be a number between 1 and 512.' in e.message:
                pass
            else:
                raise Exception(e.message)
        
        logging.info('get model max clients number in Web')
        number=web_get_number(self.zd,self.conf['wlan_name'])
        
        if not self.set_correct_value:
            self.conf['number']=self.carrierbag['wlan_max_client_number']
        
        if number!=self.conf['number']:
            self.errmsg='max client number not match cli set %s web get %s,'%(self.conf['number'],number)
        if self.errmsg:
            return self.returnResult('FAIL',self.errmsg)
        
        if self.set_correct_value:
            self._update_carrierbag()
        return self.returnResult('PASS', "set max clients number in web successfully and verify in cli ok")
    
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf={'wlan_name':'',
                   'number':'512',#1-512,random,lower,higher
                   }
        self.conf.update(conf)
        if self.conf['number'].lower()=='random':
            self.conf['number']=str(randint(1,511))
        elif self.conf['number'].lower() == 'lower':
            self.conf['number']=str(0)
        elif self.conf['number'].lower() == 'higher':
            self.conf['number']=str(randint(513,65535))
            
        if int(self.conf['number'])<=512 and int(self.conf['number'])>=1:
            self.set_correct_value=True
        else:
            self.set_correct_value=False
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        
    def _update_carrierbag(self):
        self.carrierbag['wlan_max_client_number']=self.conf['number']
        pass