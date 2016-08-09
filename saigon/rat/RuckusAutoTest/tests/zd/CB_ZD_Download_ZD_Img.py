'''
by West.li@2012.2.1
download ZD image from build server 
'''
from RuckusAutoTest.models import Test
from contrib.download import multi_threads_downloader as download_hlp
from RuckusAutoTest.tests.zd.lib.upgrade_parameter_def import upgrade_parameter
import logging
import os
from RuckusAutoTest import models as build_access

class CB_ZD_Download_ZD_Img(Test):
    
    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        if self.conf['skip_download']:
            return "PASS", "img already exist,no need download"
            
        self.base_build_url=self._get_build_url(self.conf['base_build_stream'], self.conf['base_build_no'])
        logging.info('the basic build url is: %s' % self.base_build_url )
        self.base_buile_file_name=self.base_build_url.split('/')[-1]
        self.target_build_url=self._get_build_url(self.conf['target_build_stream'], self.conf['target_build_no'])
        logging.info('the target build url is: %s' % self.target_build_url )
        self.target_buile_file_name=self.target_build_url.split('/')[-1]
        
        if not self._download_build(self.base_build_url,self.base_buile_file_name):
            self.errmsg='download base build failed'
        elif not self._download_build(self.target_build_url,self.target_buile_file_name):
            self.errmsg='download target build failed'
        else:
            self.passmsg='download zd img(%s and %s) successful' %(self.base_buile_file_name,self.target_buile_file_name)
            
        self._update_carrier_bag()
        if self.errmsg:
            return 'FAIL',self.errmsg
        return "PASS", self.passmsg

    def cleanup(self):
        pass

    def _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        self.carrierbag['base_build_file']   = os.path.join(os.getcwd(), self.base_buile_file_name)
        self.carrierbag['target_build_file'] = os.path.join(os.getcwd(), self.target_buile_file_name)

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf={}
        self.conf['base_build_stream']   = self.carrierbag['base_build_stream']
        self.conf['base_build_no']       = self.carrierbag['base_build_no']
        self.conf['target_build_stream'] = self.carrierbag['target_build_stream']
        self.conf['target_build_no']     = self.carrierbag['target_build_no']
        self.conf['skip_download']       = self.carrierbag['skip_download']
        self.conf.update(conf)

    def _get_build_url(self,build_stream, bno):
        """
        Return the URL of the expected build
        """
        return build_access.get_build_url(build_stream, bno)

    
    def _download_build(self,build_url,full_fname=None):
        """
        Download the target build from server base on the build url.
        """
        logging.info('The image_file[' + build_url + ']')
        logging.info('Please wait for downloading, It takes several minutes')
        fin = download_hlp.http_get(build_url, full_fname)        
        return fin
    
