# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Nov 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
      'sta_tag': 'Station tag',
      'browser_tag': 'Browser tag',
      'ping_timeout_ms': 'Timeout for ping target ip',
      'target_ip_list': 'Target ip list, include ipv4 and ipv6',
      'allow': 'Is target ip pingable',
      'ping_target_ips': 'Ping target Ips or not',
      'download_file': 'Will download file from web server',
      'close_browser': 'If true, will close browser after download file',
      'web_ip_addr_list': 'Web server ip address list include ipv4 and ipv6',  #Or string.
      'validation_url': 'Validation url, will download file from this url/replace ip address with web ip address',
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - [Optional] Verify target ips can/can't ping successfully, default is True.
        - [Optional] Verify can download file from web server, default is True.
        - [Optional] Close browser, default is True.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If all steps works correctly: Ping target IPs, download file, close browser. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_Station_Ping_Targets_Download_File(Test):
    required_components = ['Station']
    parameters_description = {'sta_tag': 'Station tag',
                              'browser_tag': 'Browser tag',
                              'ping_timeout_ms': 'Timeout for ping target ip',
                              'target_ip_list': 'Target ip list, include ipv4 and ipv6',
                              'allow': 'Is target ip pingable',
                              'ping_target_ips': 'Ping target Ips or not',
                              'download_file': 'Will download file from web server',
                              'close_browser': 'If true, will close browser after download file',
                              'web_ip_addr_list': 'Web server ip address list include ipv4 and ipv6',  #Or string.
                              'validation_url': 'Validation url, will download file from this url/replace ip address with web ip address',
                              }    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            if self.conf['ping_target_ips']:
                self._ping_target_ips(self.conf['allow'])
            if self.conf['download_file'] and not self.errmsg:
                self._download_file_from_server()
            if self.conf['close_browser']:
                self._close_browser()

        except Exception, ex:
            self.errmsg = "Exception: %s" % ex.message
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = "The steps %s works correctly." % self.steps
            return  self.returnResult('PASS', self.passmsg)                     
    
    def cleanup(self):
        self._update_carribag()
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'sta_tag': 'sta_1',
                     'browser_tag': 'browser',
                     'ping_timeout_ms': 15 * 1000,
                     'target_ip_list': '192.168.0.252',
                     'allow': True,
                     'ping_target_ips': True,
                     'download_file': True,
                     'retries': 3,
                     'close_browser': False,
                     }
        
        download_conf = {'web_ip_addr_list': '172.16.10.252',  #Or string.
                         'validation_url': "http://%s/authenticated/",
                         }
        
        #Web page configuration, it is fixed and don't need to pass.
        web_page_conf = {'page_title': "Ruckus Automation Test",
                         'download_loc': r"//a[@id='logo']",
                         'download_file_name': "logo.zip",
                         }      
        
        self.conf.update(download_conf)
        self.conf.update(web_page_conf)
        self.conf.update(conf)
        
        #If target ip is disallowed, will not download file, and close browser.
        if self.conf['allow'] == False:
            self.conf['download_file'] = False
        
        if type(self.conf['target_ip_list']) != list:
            self.target_ip_list = [self.conf['target_ip_list']]
        else:
            self.target_ip_list = self.conf['target_ip_list']
        #conf_web_info
        if type(self.conf['web_ip_addr_list']) != list:
            self.web_ip_addr_list = [self.conf['web_ip_addr_list']]
        else:
            self.web_ip_addr_list = self.conf['web_ip_addr_list'] 
        
        self.errmsg = ''
        self.passmsg = ''
        self.steps = []        
    
    def _retrieve_carribag(self):
        sta_dict = self.carrierbag.get(self.conf['sta_tag'])
        if sta_dict:
            self.target_station = sta_dict['sta_ins']
        else:
            raise Exception("No station provided.")
        
        browser_dict = self.carrierbag.get(self.conf['browser_tag'])
        if browser_dict:
            self.browser_id = browser_dict.get('browser_id')
        else:
            if self.conf['download_file']:
                raise Exception("No Browser provided.")
            else:
                self.browser_id = None
                
    def _update_carribag(self):
        pass
            
    #-----------------Main validation steps method -------------------
    def _ping_target_ips(self, is_allow = True):
        '''
        Station ping target IPs.
        If is_allow, station should ping target IPs successfully.
        Else, station should not send traffic to target IPs.
        '''
        logging.info("Station ping target IP list: %s" % self.target_ip_list)
        errmsg = None
        passmsg = None
        
        try:
            retry_count = self.conf['retries']
            res_err = {}
            for target_ip in self.target_ip_list:
                if is_allow:
                    logging.info("Verify can ping target %s" % target_ip)
                    for index in range(1,retry_count+1):                        
                        err_msg = tmethod.client_ping_dest_is_allowed(self.target_station, 
                                                                      target_ip,
                                                                      ping_timeout_ms = self.conf['ping_timeout_ms'])
                        
                        if not err_msg:
                            break
                        else:
                            time.sleep(10)
                else:
                    logging.info("Verify can not ping target %s" % target_ip)
                    err_msg = tmethod.client_ping_dest_not_allowed(self.target_station, 
                                                                   target_ip,
                                                                   ping_timeout_ms = self.conf['ping_timeout_ms'])
                    
                if err_msg:
                    res_err.update({target_ip:err_msg})
            
            if res_err:
                errmsg = 'Ping target IP list failed: %s' % res_err
                
            if is_allow:
                passmsg = "The station could send traffic to destinations: %s" % self.target_ip_list
            else:
                passmsg = "The station could not send traffic to destinations: %s" % self.target_ip_list
        except Exception, ex:
            errmsg = ex.message
        
        if is_allow:    
            step_name = "Ping target IPs allowed"
        else:
            step_name = "Ping target IPs denied"        
        if errmsg:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg)            
        
    def _download_file_from_server(self):
        '''
        Download file from web server.
        '''
        logging.info("Download the file %s to the station %s from servers %s" % (self.conf['download_file_name'], self.conf['sta_tag'], self.web_ip_addr_list))
        
        errmsg = None
        passmsg = None

        try:
            errmsg = {}
            passmsg = {}
            
            if not '%s' in self.conf['validation_url']:
                logging.info("Download file from %s" % self.conf['validation_url'])                
                errmsg_item, passmsg_item = self._download_file(self.conf['validation_url'])
                
                if errmsg_item:
                    errmsg = errmsg_item
                else:
                    passmsg = passmsg_item
                passmsg = "The file %s was downloaded successfully to the station [%s] from servers %s: %s" % \
                       (self.conf['download_file_name'], self.conf['sta_tag'], self.conf['validation_url'], passmsg)
            else:
                for web_ip_addr in self.web_ip_addr_list:
                    
                    if utils.is_ipv6_addr(web_ip_addr):
                        validation_url = self.conf['validation_url'] % ("[%s]" % web_ip_addr)
                    else:
                        validation_url = self.conf['validation_url'] % web_ip_addr
                    
                    logging.info("Download file from %s" % web_ip_addr)
                    errmsg_item, passmsg_item = self._download_file(validation_url)
                    
                    if errmsg_item:
                        errmsg[web_ip_addr] = errmsg_item
                    else:
                        passmsg[web_ip_addr] = passmsg_item
                    
                passmsg = "The file %s was downloaded successfully to the station [%s] from servers %s: %s" % \
                             (self.conf['download_file_name'], self.conf['sta_tag'], self.web_ip_addr_list, passmsg)
                             
        except Exception, ex:
            errmsg = ex.message
            
        step_name = "Download file from server"
        if errmsg:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg)       
            
    def _download_file(self, validation_url):
        '''
        Download files and retry two times.
        '''
        retries = self.conf['retries']
        for i in range(1,retries+1):
            errmsg_item, passmsg_item = self._download_file_from_url(validation_url)
            
            if not errmsg_item:
                break;
            
        return errmsg_item, passmsg_item
    
    def _close_browser(self):
        '''
        Close browser.
        '''
        errmsg = None
        
        try:
            if self.browser_id:
                logging.info("Trying to close the browser with ID %s on the station %s" \
                                % (self.browser_id, self.conf['sta_tag']))
                self.target_station.close_browser(self.browser_id)

            passmsg = "The browser with ID %s on the station %s was closed successfully" \
                        %  (self.browser_id, self.conf['sta_tag'])            
        except Exception, ex:
            errmsg = ex.message
            
        step_name = "Close the browser"
        if errmsg:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg) 
            
    
    def _download_file_from_url(self, validation_url):
        params = {'validation_url': validation_url,
                  'download_loc': self.conf['download_loc'],
                  'file_name': self.conf['download_file_name'],
                  'page_title': self.conf['page_title'],}
                
        messages = self.target_station.download_file_on_web_server(self.browser_id, **params)
        messages = eval(messages)
        
        errmsg_item = ""
        passmsg_item = ""

        for m in messages.iterkeys():
            if messages[m]['status'] == False:
                errmsg_item += messages[m]['message'] + " "
            else:
                passmsg_item += messages[m]['message'] + " "
                
        return errmsg_item, passmsg_item