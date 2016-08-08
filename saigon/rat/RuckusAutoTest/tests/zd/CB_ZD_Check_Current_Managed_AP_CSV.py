'''
Created on 2011-2-17
@author: liu.anzuo@odc-ruckuswireless.com

Description: This script is used to check currently managed ap CSV.

'''

key_list = [#('action',                 ),
            #('application_capability', 'Application Capability'),
            ('assoc_stas',             'Clients'),
            ('bonjour_check',          'Bonjour Gateway'),
            ('description',            'Description'),
            ('devname',                'Device Name'),
            ('extipport',              'External IP:Port'),
            ('ip',                     'IP Address'),
            #('ipv6',                   ),
            ('location',               'Location'),
            ('mac',                    'MAC Address'),
            ('mesh_mode',              'Mesh Mode'),
            ('mgmt_vlan',              'VLAN'),
            ('model',                  'Model'),
            ('radio_channel',          'Channel'),
            ('state',                  'Status')]

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import aps as web
from RuckusAutoTest.components.lib.zdcli import read_csv as csv
from RuckusAutoTest.common.utils import list_to_dict

class CB_ZD_Check_Current_Managed_AP_CSV(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        if self.conf.get('filter') == True:
            curr_managed_ap_info_web = web.get_ap_brief_by_mac_addr(self.zd, self.carrierbag.get('search_term'))
            if type(curr_managed_ap_info_web) != list:
                curr_managed_ap_info_web = [curr_managed_ap_info_web]
            curr_managed_ap_info_web = list_to_dict(curr_managed_ap_info_web, 'mac')
        else:
            curr_managed_ap_info_web = web.get_all_ap_briefs(self.zd)
        
        keys = self.zd.s.get_visible_tbl_hdrs_by_attr(web.locators['ap_tbl_loc'] % web.tbl_id['ap_summary'])
        for key in curr_managed_ap_info_web.keys():
            if curr_managed_ap_info_web.get(key).get('ipv6'):
                curr_managed_ap_info_web.get(key)['ip'] = curr_managed_ap_info_web.get(key).get('ip') + '/' + curr_managed_ap_info_web.get(key).get('ipv6')
            remove_item  = list(set(curr_managed_ap_info_web.get(key).keys()).difference(set(keys)))
            print remove_item
            for i in remove_item:
                curr_managed_ap_info_web.get(key).pop(i)

        curr_managed_ap_info_csv = csv.get_all_ap_briefs(self.file_path)
        logging.info("web info: %s" % curr_managed_ap_info_web)
        logging.info("csv info: %s" % curr_managed_ap_info_csv)
        
        self._compare_dict(curr_managed_ap_info_web, curr_managed_ap_info_csv)
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
            
        self.zd = self.testbed.components['ZoneDirector']
        self.file_path = self.carrierbag['csv_file_path']
        self.errmsg = ''
        self.passmsg = 'All fields in CSV file are corresponding to the ones in Web!'
        self.enable_columns = self.carrierbag.get('enalbe_columns')
    
        
    def _updateCarrierbag(self):
        pass
    
    def _compare_dict(self, web, csv):
        for key in web.keys():
            if self.enable_columns:
                if len(self.enable_columns) != len(web.get(key)):
                    self.errmsg = 'the column count shown on web(%s) is different with expect(%s)\n' \
                                    % (len(web.get(key)), len(self.enable_columns))
                    return
            for (i, j) in key_list:
                tmpweb = web.get(key).get(i)
                tmpcsv = csv.get(key).get(j)
#                print tmpweb.ljust(30), tmpcsv.ljust(30)
                if tmpweb != tmpcsv:
                    self.errmsg += "\n" + ("[%s %s] " % (key, j)).ljust(45) + ("web -- %s" % tmpweb).ljust(40) + ("csv -- %s" % tmpcsv).ljust(40)
        