import logging
from random import randint

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_ap_group as apgcli

class CB_ZDCLI_New_AP_Group(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('set agroup configuration in zdcli')
        apgcli.new_ap_group(self.zdcli, self.conf)
        return self.returnResult('PASS', "ap group %s created"%self.conf['name'])
        
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        '''
        conf={  'name':'System Default',
                'description':'',
                'ip_mode':'',#ipv4, ipv6 or dual
                'radio2.4':{'channelization':'',
                           'channel':'',
                           'power':'',
                           '11n-only':'',#Auto,N/AC-only
                           'wlan-grp':'',
                           'admission-ctl':'',
                           },
                'radio5.0':{'channelization':'',
                           'channel':'',
                           'power':'',
                           '11n-only':'',
                           'wlan-grp':'',
                           'admission-ctl':'',
                           },
                'model':{'zf2942':{'max-client':'',
                                   'ext-antenna':{},
                                   'port':{},
                                   },
                         'zf7363':{'max-client':'',
                                   'ext-antenna':{},
                                    'port':{}
                                   }   
                         }
                'add_members':[]
                }
        '''
        self.errmsg = ''
        self.conf={'name':'New_ap_grp',
                   }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
        
    def _update_carrierbag(self):
        pass