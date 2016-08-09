'''
'''
import logging

from RuckusAutoTest.models import Test


class CB_Station_CaptivePortal_Download_File(Test):
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
        #TODO: save file to RatToolAgent, not absolute path
        self._perform_download_file()

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
            self.sta_tag_attr: "",
            self.browser_tag_attr: "browser",
            'validation_url': "http://172.16.10.252/authenticated/",
            'download_loc': r"//a[@id='logo']",
            'file_name': "logo.zip",
            'page_title': "Ruckus Automation Test",
        }
        self.conf.update(conf)

        self.sta_tag = self.conf[self.sta_tag_attr]

        self.zd = self.testbed.components['ZoneDirector']

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
            self.browser_id = browser_dict.get(self.browser_id_attr)

        if not self.browser_id:
            raise Exception("No Browser provided.")


    def _update_carrier_bag(self):
        '''
        '''


    def _perform_download_file(self):
        '''
        '''
        logging.info("Download the file %s to the station %s" %
                     (self.conf['file_name'], self.sta_tag))

        try:
            params = {
                'validation_url': self.conf['validation_url'],
                'download_loc': self.conf['download_loc'],
                'file_name': self.conf['file_name'],
                'page_title': self.conf['page_title'],
            }
            messages = self.sta.download_file_on_web_server(self.browser_id, **params)
            messages = eval(messages)

            for m in messages.iterkeys():
                if messages[m]['status'] == False:
                    self.errmsg += messages[m]['message'] + " "

                else:
                    self.passmsg += messages[m]['message'] + " "

            if self.errmsg:
                return

            self.passmsg += \
                "The file %s was downloaded successfully to the station [%s]." % \
                (self.conf['file_name'], self.sta_tag)
            logging.info(self.passmsg)

        except Exception, e:
            self.errmsg += e.message
            logging.info(self.errmsg)

