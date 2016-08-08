# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)
    
"""
#import logging
import os
import re

from RuckusAutoTest.models import Test

from contrib.download import image_resolver as imgres

class CB_Scaling_Download_ZD_Image(Test):
    
    required_components = []
    parameter_description = {'zd_build_stream':'build stream of ZoneDirector',
                             'zd_bno':'build no of ZoneDirector',                             
                             }

    def config(self, conf):
        self.errmsg = ""
        self.passmsg = ""        
        self.conf = conf        
        self.conf.update(self.carrierbag)        
    
    def test(self):
        self.download_zdimage(self.conf)
        self.carrierbag['image_file_path'] = self.conf['zd_img_file_path']        
        self.passmsg = "ZoneDirector image location:[%s], build stream[%s], build no[%s]" % \
        (self.conf['zd_img_file_path'], self.conf['zd_build_stream'], self.conf['zd_bno'])
        
        return ('PASS', self.passmsg)        
    
    def cleanup(self):
        pass

    def download_zdimage(self, conf):
        """
        download zd3k image from lhotse
        """
        #cwang@2010-09-16, doesn't download if exists.
        chk_name = "%s.%s.tar.gz" % (conf['zd_build_stream'], conf['zd_bno'])
        if not os.path.exists(chk_name):            
            fname = imgres.download_build(conf['zd_build_stream'], conf['zd_bno'])
        else:
            fname = chk_name
#        img_filename = imgres.get_image(fname, filetype="^zd3k_(\d+.){5}ap_(\d+.){5}img$")
        
        img_filename = self.escape(os.path.realpath(fname))
#        logging.info("zd image file[%s]" % img_filename)
        conf['zd_img_file_path'] = img_filename      

    def escape(self, file_path):
        expr = "[/|\\^\\\\]"
        return re.sub(expr, "\\\\", file_path)    
        