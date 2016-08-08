'''
    Download HTTP URL file to local disk.
'''
import logging
import os

from RuckusAutoTest.models import Test
from contrib.download import multi_threads_downloader as download_hlp

class CB_ZD_Dowload_Http_Url(Test):
    
    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        if self.conf['skip_download']:
            return "PASS", "file already exist, do not need download"
        
        return "PASS", self.passmsg
    
        for url in self.conf['http_file_url_list']:
            file_name = url.split('/')[-1]
            
            if self.conf['local_file_path'][-1] == '\\':
                full_path = self.conf['local_file_path']+file_name
            else:
                full_path = self.conf['local_file_path']+'\\'+file_name
            
            res = self._download_file(url, full_path)
            if res == False:
                self.errmsg = 'Download file from Internet by HTTP URL failed' 
        
        if self.errmsg:
            return 'FAIL',self.errmsg
        return "PASS", self.passmsg

    def cleanup(self):
        self._update_carrier_bag()

    def _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        pass

    def _init_test_params(self, conf):
        self.conf={'skip_download': False}
        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''

    def _download_file(self, file_url, full_fname=None):
        """
        Download the target file from Internet.
        """
        logging.info('The file path and name %s' % file_url)
        logging.info('Please wait while downloading, it will take several second')
        fin = download_hlp.http_get(file_url, full_fname)        
        return fin
