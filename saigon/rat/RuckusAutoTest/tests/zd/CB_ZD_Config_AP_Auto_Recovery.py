"""
Config AP Auto Recovery Option(AP reboots if disconnected from ZoneDirector for more than *** minutes):
    1) Enabled and set AP recovery time, default 30 min
	2) Disabled

Create on 2013-4-19
@author: kevin.tan@ruckuswireless.com

"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


class CB_ZD_Config_AP_Auto_Recovery(Test):
    def config(self, conf):
        self.conf={'recovery_enabled':True,
                   'recovery_time': '30',
                   }
        self.conf.update(conf)
        self.zd=self.testbed.components['ZoneDirector']

    def test(self):
        option = self.conf['recovery_enabled']
        r_time = self.conf['recovery_time']
        logging.info('Configure AP Auto Recovery Option to %s' % option)
        if option is True:
            logging.info('Recover time %s minutes' % r_time)

        try:
            lib.zd.ap.set_auto_recovery(self.zd, option, r_time)
        except:
            return ("FAIL", "Configure AP Auto Recovery Option failed")
                    
        return ("PASS", "Configure AP Auto Recovery Option successfully")

    def cleanup(self):
        pass

