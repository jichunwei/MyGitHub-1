'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
   (1) _getInfoOnFile() to parse the Excel to get the expected channel range and txPower
   (2) _test_txPower(file_ctrcode) to compare and test the AP's txPower value from the AP shell cmd 'iwconfig'
      and the expected txPower value from the Excel file.     
   (3) _test_channel_range(_cfgChannelRange) to compare and test the AP's channel range from the ZDCli cmd
      and the expected channel range from the Excel file.     
          
   3. Cleanup:
       - 
    How it was tested:
    As the above "2. test"        
        
Create on 2013-7-22
@author: Xu, Yang
@since: 2013-7-22 
'''      
import logging
from xml.dom import minidom
import re
import traceback

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers

from RuckusAutoTest.common.Ratutils import *

from RuckusAutoTest.components.lib.apcli import shellmode as ap_shell
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import set_wlan
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

class CB_ZD_AP_CLI_Test_CountryCode_CR_Power(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(cc='BH',
                         ccalias='Bahrain',
                         # ap_tag = 'AP_01',
                         active_ap = 'AP_01',
                         # model = '73XX',
                         # filename = './RuckusAutoTest/common/Countrymatrix.xls'
                         model = 'zf7363',
                         # filename = './RuckusAutoTest/common/Country matrix 2012 03 12+KE.xls'
                         filename = './RuckusAutoTest/common/Countrymatrix.xls'
                         )
        self.conf.update(conf)
        logging.info('Load test configuration')
#        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        # self.cc = self.conf.get('cc')
        self.cc = str(conf['cc'])
        self.ccalias = self.conf.get('ccalias')
        
        ## self.ap_tag = self.conf.get('ap_tag')
        ## self.mac_addr = self.testbed.get_aps_sym_dict()[self.ap_tag]['mac']
        self.active_ap = self.conf.get('active_ap')
        self.mac_addr = self.testbed.get_aps_sym_dict()[self.active_ap]['mac']

        self.ap_model = ''
        self.ap_model = self.conf.get('model')

        # Match the parse_country_matrix_xsl(filename, ap_model)
        if not self.ap_model.lower().startswith('zf'):
            self.ap_model = 'zf' + self.ap_model

        self.filename = self.conf.get('filename')
   
        logging.info('Load test configuration DONE.')
        logging.info('Test info: %s' % pformat(conf))

    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):       
        try:        
            file_ctrcode = self._getInfoOnFile()
            print file_ctrcode
            ## {'5GHz': {'153': 14, '157': 14, '48': 14, '44': 14, '56': 14, '36': 14, '40': 14, '52': 14, '60': 14, '64': 14, '165': 14, '149': 14, '161': 14}, '2.4GHz': {'11': 17, '10': 17, '13': 17, '12': 17, '1': 17, '3': 17, '2': 17, '5': 17, '4': 17, '7': 17, '6': 17, '9': 17, '8': 17}}
            ## The above parse the Excel for _cfg including txPower to compare
            
            self.apins = tconfig.get_testbed_active_ap(self.testbed, self.mac_addr)


            msgPower = self._test_txPower(file_ctrcode)
            if msgPower:
                return self.returnResult('FAIL', msgPower)

     
            _cfgChannelRange = {}
            channelRange5G = file_ctrcode['5GHz'].keys()
            channelRange5G = [int(channel) for channel in channelRange5G]
            channelRange5G.sort()
            channelRange5G = [str(channel) for channel in channelRange5G]
            _cfgChannelRange['A/N'] = unicode(",".join(channelRange5G))
    
    
            channelRange2G = file_ctrcode['2.4GHz'].keys()
            channelRange2G = [int(channel) for channel in channelRange2G]
            channelRange2G.sort()
            channelRange2G = [str(channel) for channel in channelRange2G]
            _cfgChannelRange['B/G/N'] = unicode(",".join(channelRange2G))


            ## The above parse the Excel for _cfg including ChannelRange to compare
            msg = self._test_channel_range(_cfgChannelRange)
            if msg:
                return self.returnResult('FAIL', msg)
           
        except Exception, e:
            logging.debug(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
        
          
        
        return self.returnResult('PASS', 'Country Code %s txPower and ChannelRange Testing Pass' % self.ccalias)
    
    def cleanup(self):
        self._update_carribag()


    def _test_channel_range(self, expected_cfg = None):
        #Chico, 2015-6-17, first set channelization 20 to make all vaild channels displayed
        logging.info('Set channelization from Auto to 20')
        ap_cfg={'mac_addr':self.mac_addr, #@ZJ 20150716 fix error "FAIL     150714-0326: [0, 'mac_addr']" by liangaihua
                'radio_ng':{'channelization':'20'},
                'radio_na':{'channelization':'20'}
                }
        Helpers.zdcli.configure_ap.configure_ap(self.zdcli, ap_cfg)
        #Chico, 2015-6-17, first set channelization 20 to make all vaild channels displayed
        
        logging.info('Get channel range from ZDCLI.')
        # Get an and bgn values from the below to compare 
        # cmd_block = 'show ap mac $mac' %conf[actApMac]
        # zdcli.do_show(cmd_block) doCmd('show ap mac $mac') 
        # 'Channel Range': {'A/N': '36,40,44,48,149,153,157,161 (Disallowed= )','B/G/N': '1,2,3,4,5,6,7,8,9,10,11 (Disallowed= )'},
        apinfo = Helpers.zdcli.configure_ap.get_ap(self.zdcli, 
                                                   self.mac_addr)
        ## dict: {u'Device Name': u'RuckusAP', u'Radio a/n': {u'Call Admission Control': u'OFF', u'Channelization': u'Auto', u'Tx. Power': u'Auto', u'WLAN Group Name': u'Default', u'WLAN Services enabled': u'Yes', u'SpectraLink Compatibility': u'Disabled', u'Channel': u'Auto'}, u'Radio b/g/n': {u'Call Admission Control': u'OFF', u'Channelization': u'Auto', u'Tx. Power': u'Auto', u'WLAN Group Name': u'Default', u'WLAN Services enabled': u'Yes', u'SpectraLink Compatibility': u'Disabled', u'Channel': u'Auto'}, u'Location': u'', u'Channel Range': {u'A/N': u'36,40,44,48,52,56,60,64,149,153,157,161 (Disallowed= )', u'B/G/N': u'1,2,3,4,5,6,7,8,9,10,11,12,13 (Disallowed= )'}, u'Model': u'zf7363', u'Group Name': u'System Default', u'GPS': u'', u'Description': u'', u'LAN Port': {u'1': {u'Interface': u'eth1', u'Dot1x': u'None', u'Label': u'10/100 LAN2', u'LogicalLink': u'Down', u'PhysicalLink': u'Down'}, u'0': {u'Interface': u'eth0', u'Dot1x': u'None', u'Label': u'10/100 LAN1', u'LogicalLink': u'Up', u'Phys...

        cr_zdcli = apinfo['Channel Range']
        ## dict: {u'A/N': u'36,40,44,48,52,56,60,64,149,153,157,161 (Disallowed= )', u'B/G/N': u'1,2,3,4,5,6,7,8,9,10,11,12,13 (Disallowed= )'}
        
        an = cr_zdcli.get('A/N', None)

        # ',' in an match the ID output as below
        #Match ID (INDONESIA) Not support 5G Channel Range
        #In ZDCli, No 5g ChannelRange
        #Channel Range:
        #        B/G/N= 1,2,3,4,5,6,7,8,9,10,11,12,13 (Disallowed= )
        #        A/N=  (Disallowed= )         
        
        #Chico, 2015-6-17, correct scripts to include channels values from Disallowed
#        import re
        listActualAN = re.findall('\d+', an)
        '''
        "(Pdb) an  
         u'(Disallowed= )'"
        '''
        if not listActualAN:
            #@ZJ 20150813 ZF-14166 script optimization: Some ap e.g.t300 with some country-code has no outdoor channel in mode:5g.
            logging.info("No 5G channel is found inside AP, without enable indoor channel.")
            Helpers.zdcli.system.dot11_country_code_channel_mode_indoor(self.zdcli, self.cc)
            logging.info('Get channel range from ZDCLI, after enable indoor channel.')
            apinfo = Helpers.zdcli.configure_ap.get_ap(self.zdcli, self.mac_addr)
            cr_zdcli = apinfo['Channel Range']
            an = cr_zdcli.get('A/N', None)
            listActualAN = re.findall('\d+', an)
            if not listActualAN:
                return('No 5G channel is found inside AP.')
            #@ZJ 20150813 ZF-14166 script optimization: Some ap e.g.t300 with some country-code has no outdoor channel in mode:5g.

        listExpectedAN = expected_cfg['A/N'].split(',')
        #Chico, 2015-6-17, correct error message
        if not len(listExpectedAN):
            return "Current version of Country Code matrix doesn't define any channel specific, please check manually"
        #Chico, 2015-6-17, correct error message
        else:
            for channel in listActualAN:
                if channel not in listExpectedAN:
                    return "5G Channels: Actual Channel %s of actual Channel Range %s is NOT in Expected Channel Range %s" % (channel, listActualAN, listExpectedAN)        
            
        bgn = cr_zdcli.get('B/G/N', None)
        if bgn and ',' in bgn:
            bgn = bgn.split()[0]
            if bgn != expected_cfg['B/G/N']:
                return "2.4G Channels: Expected %s, actual %s" % (expected_cfg['B/G/N'], bgn)

        return None

            
    def _test_txPower(self, expected_cfg = None):
        txPowerDelta = 3
        #### for apins in self.testbed.components['AP']:
            #if apins.get_ip_addr() == ipaddr:
            #### if apins.get_base_mac().lower() == str(self.mac_addr):
                # Add sh_get_2radio_tx_power(self) in RuckusAP.py
                #dChanPower = apins.sh_get_2radio_tx_power()
        dChanPower=ap_shell.get_2radio_tx_power(self.apins)
                
        apChannel = dChanPower['2.4G']['Channel']
        if apChannel != '0':
            expectedChannelList = expected_cfg['2.4GHz'].keys()
            if apChannel not in expectedChannelList:
                return 'AP %s 2.4G is actual %s , actual Channel is Not in expected Channel list %s .' % (self.mac_addr, dChanPower['2.4G'], expectedChannelList)
            else:
                actualPower24 = dChanPower['2.4G']['Power']
                expectedPower24 = expected_cfg['2.4GHz'].get(apChannel)
                if actualPower24 > (expectedPower24 + txPowerDelta) or actualPower24 < (expectedPower24 - txPowerDelta):
                    return 'AP %s 2.4G is actual %s , is out of the range: expected txPower %s +- delta %s dBm. ' % (self.mac_addr, dChanPower['2.4G'], expectedPower24, txPowerDelta)

        apChannel = dChanPower['5G']['Channel']
        if apChannel != '0':
            expectedChannelList = expected_cfg['5GHz'].keys()
            if apChannel not in expectedChannelList:
                return 'AP %s 5G is actual %s , actual Channel is Not in expected Channel list %s .' % (self.mac_addr, dChanPower['5G'], expectedChannelList)
            else:
                actualPower5 = dChanPower['5G']['Power']
                expectedPower5 = expected_cfg['5GHz'].get(apChannel)
                if actualPower5 > (expectedPower5 + txPowerDelta) or actualPower5 < (expectedPower5 - txPowerDelta):
                    return 'AP %s 5G is actual %s , is out of the range: expected txPower %s +- delta %s dBm. ' % (self.mac_addr, dChanPower['5G'], expectedPower5, txPowerDelta)

        return None

    def _getInfoOnFile(self):   
        ## 'Test params' from that as ap.Countrycode_TxPower({'wlanlist': ['wlan0', 'wlan100'], 'model': '73XX', 'active_ap': 'AP_01', 'countrycode': u'AR', 'filename': './RuckusAutoTest/common/CountryMatrix.xls'})  
        country_matrix_res = parse_country_matrix_xsl(self.filename, self.ap_model)
        found_cc = dict()
        for each_cc in country_matrix_res:
            if each_cc['country'] == self.cc:
                found_cc = each_cc.copy()
                break
        del found_cc['country']

        # Information of CountryCode parsing from file
        logging.info("[Pre-defined TxPower]: ")
        for key, value in found_cc.iteritems():
            temp = sorted([int(x) for x in self._getDebugMsg(value).split(',') if x])
            for i in temp:
                logging.info("[Country code]: %s    [Radio]: %s    [Channel]: %s    [TxPower]: %s" %
                             (self.cc, key, i, value[str(i)]))

        return found_cc

    def _getDebugMsg(self, dictionary):
        msg = ""
        for key, value in dictionary.iteritems():
            msg += "%s," % key

        return msg.rstrip(',')

