'''
Description:
    Verify the guest passes information in the record file.
       
Create on 2011-8-23
@author: serena.tan@ruckuswireless.com
'''


import csv
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Verify_GuestPass_In_Record_File(Test):
    required_components = []
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            if not self.expected_record_info:
                logging.info("Get all guest passes on WebUI")
                all_guestpass_info = ga.get_all_guestpasses(self.zd)

                all_guestpass_info_dict = {}
                for guest_full_name in all_guestpass_info.iterkeys():
                    all_guestpass_info_dict[guest_full_name] = ''
    
                logging.debug('All guest pass information on Zone Director WebUI are: %s' % all_guestpass_info_dict)
                self.expected_record_info = all_guestpass_info_dict
            
            record_file = open(self.file_path)
            reader = csv.reader(record_file)
            all_info_in_file = {}
            for row in reader:
                if row != ['Guest-Name', 'Key', 'Remarks', 'Expires']:
                    all_info_in_file[row[0]] = row[1]
                    
            record_file.close()
    
            logging.debug('All guest pass information in record file are: %s' % all_info_in_file)
            logging.debug('The expected guest pass information are: %s' % self.expected_record_info)
            
            errguest = []
            for guestname in self.expected_record_info.keys():
                if guestname not in all_info_in_file:
                    errguest.append(guestname)
                    
                elif self.expected_record_info[guestname]:
                    if all_info_in_file[guestname] != self.expected_record_info[guestname]:
                        errguest.append(guestname)
            
            if errguest:
                self.errmsg = 'The information of guest users %s are not correct in the record file'
                self.errmsg = self.errmsg % errguest
            
            else:
                self.passmsg = 'The information of guest users %s are correct in the record file' 
                self.passmsg = self.passmsg % self.expected_record_info.keys()
            
            
        except Exception, e:
            self.errmsg = 'Verify guest pass information in record file failed: %s' % e.message
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'expected_record_info': {}}
        self.conf.update(conf)
        
        self.expected_record_info = self.conf['expected_record_info']
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        if not self.expected_record_info:
            if self.carrierbag.has_key('gp_cfg') and self.carrierbag['gp_cfg'].has_key('expected_record_info'):
                self.expected_record_info = self.carrierbag['gp_cfg']['expected_record_info']
            
        self.file_path = self.carrierbag['existed_guest_pass_record_file']
  
    def _update_carribag(self):
        pass
