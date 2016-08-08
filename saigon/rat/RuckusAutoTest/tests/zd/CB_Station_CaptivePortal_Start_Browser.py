'''
'''
import logging

from RuckusAutoTest.models import Test


class CB_Station_CaptivePortal_Start_Browser(Test):
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
        self._start_browser()

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
            'browser_name_attr': "browser_name",
        }
        if conf.has_key('carrierbag_keys'):
            self.carrierbag_keys.update(conf['carrierbag_keys'])
            conf.pop('carrierbag_keys')

        self.sta_tag_attr = self.carrierbag_keys['sta_tag_attr']
        self.sta_ins_attr = self.carrierbag_keys['sta_ins_attr']
        self.browser_tag_attr = self.carrierbag_keys['browser_tag_attr']
        self.browser_id_attr = self.carrierbag_keys['browser_id_attr']
        self.browser_name_attr = self.carrierbag_keys['browser_name_attr']

        self.conf = {
            self.sta_tag_attr: "sta1",
            self.browser_tag_attr: "browser",
            self.browser_name_attr: "firefox",
            'tries': 3,
            'timeout': 15,
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


    def _update_carrier_bag(self):
        '''
        '''
        self.carrierbag.update({
            self.conf[self.browser_tag_attr]: {
                self.browser_id_attr: self.browser_id,
                self.browser_name_attr: self.conf[self.browser_name_attr],
            }
        })


    def _start_browser(self):
        '''
        '''
        logging.info(
            "Trying to start the %s browser on the station %s" %
            (self.conf[self.browser_name_attr], self.sta_tag)
        )

        try:
            self.browser_id = self.sta.init_and_start_browser(
                self.conf[self.browser_name_attr],
                self.conf['tries'], self.conf['timeout'],
            )
            self.browser_id = int(self.browser_id)

            self.passmsg = \
                "The %s browser on the station %s was started successfully with ID %s" % \
                (self.conf[self.browser_name_attr], self.sta_tag, self.browser_id)
            logging.info(self.passmsg)

        except Exception, ex:
            self.errmsg = ex.message
            logging.info(self.errmsg)

