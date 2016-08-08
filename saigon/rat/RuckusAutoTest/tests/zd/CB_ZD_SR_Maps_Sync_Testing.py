'''
Description:
Created on 2010-7-6
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging
import os

from RuckusAutoTest.models import Test

class CB_ZD_SR_Maps_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        self.default_map_size = self.active_zd.get_maps_info()[0]['size']
        if 'K' in self.default_map_size.upper():
            self.default_map_size = float(self.default_map_size.upper().split('K')[0])
        elif 'M' in self.default_map_size.upper():
            self.default_map_size = float(self.default_map_size.upper().split('M')[0]) * 1024
        else:
            self.default_map_size = float(self.default_map_size) / 1024        
                
    
    def test(self):
        passmsg = []
        self._test_maps_cfg_sync()
        if self.errmsg:
            return ("FAIL", self.errmsg)
        
        self.passmsg = 'Create/Delete map setting can be synchronized to standby ZD'
        logging.info(self.passmsg)        
        passmsg.append(self.passmsg)
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.conf = dict(img_list=[])
        self.format_list = ['.PNG', '.JPG', '.GIF']
        self.conf.update(conf)
        
        path = os.getcwd()+"\\RuckusAutoTest\\scripts\\zd\\maps\\"
        for idx in range(len(self.conf['img_list'])):
            print "before " + self.conf['img_list'][idx]
            self.conf['img_list'][idx] = path + self.conf['img_list'][idx].split("\\")[-1]
            print "after " + self.conf['img_list'][idx]
        
        self.errmsg = ''
        self.passmsg = ''
            
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']           
    
    def _update_carrier_bag(self):
        pass
    
    
    def _test_maps_cfg_sync(self):
        totalsize = self.default_map_size
        totalmap = 1        
        logging.info('Try to create multiple map file')
        map_name_list = []
        for img in self.conf['img_list']:
            totalsize = totalsize + float(os.path.getsize(img) / 1024)
            if totalsize < 2 * 1024:
                if os.path.splitext(img)[1].upper() not in self.format_list:
                    raise Exception('The file extension is not in %s.' % repr(self.format_list))
                else:
                    try:
                        map_name = 'Test_Map_%d' % totalmap                       
                        self.active_zd.create_map(map_name, img)
                        map_name_list.append(map_name)
                        totalmap += 1
                    except Exception, e:
                        if 'Create map error' in e.message:
                            return ('FAIL', e.message)
                        else:
                            raise
        if not self._verify_maps_list(): return False
        
        self.passmsg = "Created maps file have synchronized to standby ZD"
        logging.info(self.passmsg)
        
        logging.info('Try to delete map file')
        for map_name in map_name_list:            
            self.active_zd.delete_map(map_name)
        
        if not self._verify_maps_list(): return False
        
        self.passmsg = "Deleted maps file have synchronized to standby ZD"
        logging.info(self.passmsg)
                
    
    def _verify_maps_list(self):
        a_maps_list = self.active_zd.get_maps_info()
        s_maps_list = self.standby_zd.get_maps_info()
        for a_map in a_maps_list:
            for s_map in s_maps_list:
                if a_map['name'] == s_map['name']:
                    if not self._verify_dict(a_map, s_map):
                        return False
    
            
    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True
    
