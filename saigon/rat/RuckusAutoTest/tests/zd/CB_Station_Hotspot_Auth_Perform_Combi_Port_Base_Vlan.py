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
       -            
   3. Cleanup:
       - 
    How it was tested:
        
       
Create on Nov 28, 2011
@author: jluh@ruckuswireless.com
'''

import logging

import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_Station_Hotspot_Auth_Perform_Combi_Port_Base_Vlan(Test):
  required_components = ['Station']
  parameters_description = {}
  
  
  def _init_params(self, conf):
       self.conf = {'sta_tag': '',
                    'check_status_timeout':120, 
                    'dest_ip': '172.16.10.252', 
                    'ping_timeout_ms': 10000,
                    'wlan_cfg': {},
                    'hotspot_perform_cfg': {'username': "ras.local.user",
                                            'password': "ras.local.user",
                                            'redirect_url': "",
                                            'browser_tag': "browser",
                                            'browser_name': "firefox",
                                            'original_url': 'http://172.16.10.252/',
                                            'expected_data': "It works!",
                                            'tries': 3,
                                            'timeout': 15,
                                            }, 
                  }
       if conf.has_key('hotspot_perform_cfg'):
           self.conf['hotspot_perform_cfg'].update(conf['hotspot_perform_cfg'])
       if conf.has_key('wlan_cfg'):
           self.conf['wlan_cfg'].update(conf['wlan_cfg'])
       if conf.has_key('sta_tag'):
           self.conf['sta_tag'] = conf['sta_tag']
       if conf.has_key('ping_timeout_ms'):
           self.conf['ping_timeout_ms'] = conf['ping_timeout_ms']
       if conf.has_key('dest_ip'):
           self.conf['dest_ip'] = conf['dest_ip']
       if conf.has_key('check_status_timeout'):
           self.conf['check_status_timeout'] = conf['check_status_timeout']
       self.wlan_cfg = conf['wlan_cfg']
       self.dest_ip = self.conf['dest_ip']
       self.check_status_timeout = 120
       self.username = self.conf['hotspot_perform_cfg']['username']
       
       self.zd = self.testbed.components['ZoneDirector']

       self.errmsg = ''
       self.passmsg = ''
  
  
  def _retrieve_carribag(self, conf):
      self.target_station = self.carrierbag['Station'][self.conf['sta_tag']]['sta_ins']
  
  
  def _update_carribag(self):
      self.carrierbag['Station'][self.conf['sta_tag']]['sta_wifi_ip_addr'] = self.sta_wifi_ip_addr
      self.carrierbag['Station'][self.conf['sta_tag']]['sta_wifi_mac_addr'] = self.sta_wifi_mac_addr
      if not self.carrierbag.has_key('Browser'):
          self.carrierbag['Browser'] = {}
      
      self.carrierbag['Browser'].update({
           self.conf['hotspot_perform_cfg']['browser_tag']: {
               'browser_id': self.browser_id,
               'browser_name': self.conf['hotspot_perform_cfg']['browser_name'],
            }
        })
  
  def config(self, conf):
      self._init_params(conf)
      self._retrieve_carribag(conf)
  
  
  def test(self):
      self._associate_station_to_hotspot_wlan()
      if self.errmsg:
          return self.returnResult('FAIL', self.errmsg)
      self._renew_sta_wifi_ip()
      if self.errmsg:
          return self.returnResult('FAIL', self.errmsg)    
      self._verify_sta_info_on_zd_before_perform_auth()
      if self.errmsg:
          return self.returnResult('FAIL', self.errmsg)
      self._sta_ping_dest_ip_before_perform_auth()
      if self.errmsg:
          return self.returnResult('FAIL', self.errmsg)
      
      self.perform_hotspot_auth()
      if self.errmsg:
          return self.returnResult('FAIL', self.errmsg)
      self._verify_sta_info_on_zd_after_perform_auth()
      if self.errmsg:
          return self.returnResult('FAIL', self.errmsg)
      self._sta_ping_dest_ip_after_perform_auth()
      if self.errmsg:
          return self.returnResult('FAIL', self.errmsg)
      
      self._update_carribag()
         
      self.passmsg = "The Station can associate and authorize to the hotspot wlan normally."
      return self.returnResult('PASS', self.passmsg)
  
  
  def cleanup(self):
       pass


  def _associate_station_to_hotspot_wlan(self):
      #Update the step by Jacky Luh@2011-08-16
      if (self.wlan_cfg.has_key("wpa_ver") and self.wlan_cfg['wpa_ver'] == "WPA_Mixed") or \
         (self.wlan_cfg.has_key("encryption") and self.wlan_cfg['encryption'] == "Auto"):
          self.wlan_cfg['wpa_ver'] = self.wlan_cfg['sta_wpa_ver']
          self.wlan_cfg['encryption'] = self.wlan_cfg['sta_encryption']
          
      self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg, self.conf['check_status_timeout'])
      
      if self.errmsg:
          self.errmsg = tmethod.verify_wlan_in_the_air(self.target_station, self.wlan_cfg['ssid'])
     
     
  def _renew_sta_wifi_ip(self):
      (self.anOK, self.sta_wifi_ip_addr, self.sta_wifi_mac_addr) = \
      (self.anOK, self.xtype, self.errmsg) = \
       tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)

      if self.anOK:
          self.errmsg = ''
          return self.errmsg        
      elif self.xtype == 'FAIL':
          return self.errmsg
      else:
          raise Exception(self.errmsg)     
     
  
  def _verify_sta_info_on_zd_before_perform_auth(self):
      (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_unauthorized(self.zd, \
                                           self.sta_wifi_ip_addr, self.sta_wifi_mac_addr, \
                                           self.check_status_timeout)
      
      if not self.errmsg:
          logging.info("Client's status is unauthorized, detail [%s]" % self.client_info)
     
     
  def _sta_ping_dest_ip_before_perform_auth(self):
      self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.dest_ip, 
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])
      
      if not self.errmsg:
          logging.info("STA can not ping pass the dest ip, which like the expected result")
     
     
  def perform_hotspot_auth(self):
      self._start_browser()
      if self.errmsg:
          return
      self._perform_hotspot_auth()
      if self.errmsg:
          return
      self._close_browser()
      if self.errmsg:
          return
      
  def _perform_hotspot_auth(self):
    '''
    '''
    logging.info("Perform Hotspot Auth on the station %s" % self.conf['sta_tag'])

    try:
        arg = tconfig.get_hotspot_auth_params(self.zd, 
                                              self.conf['hotspot_perform_cfg']['username'], 
                                              self.conf['hotspot_perform_cfg']['password'], 
                                              self.conf['hotspot_perform_cfg']['redirect_url'],
                                              )
        if self.conf['hotspot_perform_cfg'].get('original_url'):
            arg['original_url'] = self.conf['hotspot_perform_cfg']['original_url']

        if self.conf['hotspot_perform_cfg'].get('expected_data'):
            arg['expected_data'] = self.conf['hotspot_perform_cfg']['expected_data']

        messages = self.target_station.perform_hotspot_auth_using_browser(self.browser_id, arg)
        messages = eval(messages)

        for m in messages.iterkeys():
            if messages[m]['status'] == False:
                self.errmsg += messages[m]['message'] + " "

            else:
                self.passmsg += messages[m]['message'] + " "

        if self.errmsg:
            return

        logging.info("Perform Hotspot Auth successfully on station [%s]." % self.conf['sta_tag'])

    except Exception, e:
        self.errmsg += e.message
        logging.info(self.errmsg)    
     
     
  def _start_browser(self):
        '''
        '''
        logging.info(
            "Trying to start the %s browser on the station %s" %
            (self.conf['hotspot_perform_cfg']['browser_name'], self.conf['sta_tag'])
        )

        try:
            self.browser_id = self.target_station.init_and_start_browser(
                self.conf['hotspot_perform_cfg']['browser_name'],
                self.conf['hotspot_perform_cfg']['tries'], 
                self.conf['hotspot_perform_cfg']['timeout'],
            )
            self.browser_id = int(self.browser_id)

            if not self.errmsg:
                logging.info("The %s browser on the station %s was started successfully with ID %s" % \
                    (self.conf['hotspot_perform_cfg']['browser_name'], self.conf['sta_tag'], self.browser_id))

        except Exception, ex:
            self.errmsg = ex.message
            logging.info(self.errmsg)   
            
            
  def _close_browser(self):
     '''
     '''
     logging.info("Trying to close the browser with ID %s on the station %s" % \
                 (self.browser_id, self.conf['sta_tag']))

     try:
         self.target_station.close_browser(self.browser_id)

         if not self.errmsg:
             logging.info("The browser with ID %s on the station %s was closed successfully" % \
                         (self.browser_id, self.conf['sta_tag']))

     except Exception, ex:
         self.errmsg = ex.message
         logging.info(self.errmsg)
     
     
  def _verify_sta_info_on_zd_after_perform_auth(self):
      (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_authorized(self.zd, \
                                           self.username, self.sta_wifi_mac_addr, \
                                           self.check_status_timeout)
      
      if not self.errmsg:
          logging.info("Client's status is authorized, detail [%s]" % self.client_info)
     
     
  def _sta_ping_dest_ip_after_perform_auth(self):
      self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.dest_ip, 
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])
      
      if not self.errmsg:
          logging.info("STA can ping pass the dest ip, which like the expected result")                   