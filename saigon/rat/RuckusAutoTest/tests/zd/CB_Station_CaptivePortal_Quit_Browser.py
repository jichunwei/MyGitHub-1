'''
'''
import logging

from RuckusAutoTest.models import Test


class CB_Station_CaptivePortal_Quit_Browser(Test):
    '''
    classdocs
    '''

    def config(self, conf):
        '''
        '''
        self._init_test_params(conf)
        self._retrive_carrier_bag()


    def test(self):
        '''
        '''
        self._close_browser()

        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)

        self._update_carrier_bag()

        return self.returnResult("PASS", self.passmsg)


    def cleanup(self):
        '''
        '''


    def _init_test_params(self, conf):
        '''
        '''
        self.carrierbag_keys = {
            'sta_tag_attr': "sta_tag",
            'sta_ins_attr': "sta_ins",
            'browser_tag_attr': "browser_tag",
            'browser_id_attr': "browser_id",
        }
        if conf.has_key('carrierbag_keys'):
            self.carrierbag_keys.update(conf['carrierbag_keys'])
            conf.pop('carrierbag_keys')

        self.sta_tag_attr = self.carrierbag_keys['sta_tag_attr']
        self.sta_ins_attr = self.carrierbag_keys['sta_ins_attr']
        self.browser_tag_attr = self.carrierbag_keys['browser_tag_attr']
        self.browser_id_attr = self.carrierbag_keys['browser_id_attr']

        self.conf = {
            self.sta_tag_attr: "sta1",
            self.browser_tag_attr: "browser",
        }
        self.conf.update(conf)

        self.sta_tag = self.conf[self.sta_tag_attr]
        self.browser_tag = self.conf[self.browser_tag_attr]
        self.browser_id = 0

        self.errmsg = ""
        self.passmsg = ""


    def _retrive_carrier_bag(self):
        '''
        '''
        self.sta = self.conf.get(self.sta_ins_attr)
        if not self.sta and self.sta_tag:
            sta_dict = self.carrierbag.get(self.sta_tag)
            self.sta = sta_dict.get(self.sta_ins_attr)

        if not self.sta:
            raise Exception("No station provided.")


        self.browser_id = self.conf.get(self.browser_id_attr)

        if not self.browser_id:
            browser_dict = self.carrierbag.get(self.conf[self.browser_tag_attr])
            if browser_dict:
                self.browser_id = browser_dict.get(self.browser_id_attr)
            else:
                self.browser_id = -1

        if not self.browser_id:
            raise Exception("No Browser provided.")


    def _update_carrier_bag(self):
        '''
        '''


    def _close_browser(self):
        '''
        '''
        logging.info(
            "Trying to close the browser with ID %s on the station %s" %
            (self.browser_id, self.sta_tag)
        )
        
        if self.browser_id != -1:
            try:
                self.sta.close_browser(self.browser_id)

                self.passmsg = \
                "The browser with ID %s on the station %s was closed successfully" % \
                (self.browser_id, self.sta_tag)
                logging.info(self.passmsg)

            except Exception, ex:
                self.errmsg = ex.message
                logging.info(self.errmsg)

