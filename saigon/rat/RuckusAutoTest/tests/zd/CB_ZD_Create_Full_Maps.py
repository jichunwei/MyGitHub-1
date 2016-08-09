'''
Description:
Created on 2010-8-16
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Create_Full_Maps(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):        
        self._create_full_maps()
        self._update_carrier_bag()
        
        return self.returnResult("PASS", "All of maps are created successfully")
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(num_of_maps = 40,
                         map_path = 'D:\\p4\\tools\\rat-branches\\saigon\\rat\\RuckusAutoTest\\scripts\\zd\\maps\\map_test.png',
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']   
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        self.errmsg = ''
        self.passmsg = ''

    def _create_full_maps(self):
        map_cnt = self.conf['num_of_maps']
        map_cfg = dict(name  = '', map_path = '')
        map_cfg['map_path'] = self.conf['map_path']
        map_list = []
        for i in range(1, map_cnt + 1):
            map_cfg_tmp = map_cfg.copy()
            map_cfg_tmp['name'] = 'Test_Maps_%d' % i
            map_list.append(map_cfg_tmp)
            
        for map in map_list:
            self.zd.create_map(map['name'], map['map_path'])
            logging.info('map [%s]create successfully' % map['name'])          
    
