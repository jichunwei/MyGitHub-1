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
import logging
import os
import re

from RuckusAutoTest.models import Test

from contrib.download import image_resolver as imgres

class CB_ZD_Download_Image(Test):
    
    required_components = []
    parameter_description = {'zd_build_stream':'build stream of Zone Director',
                             'zd_bno':'build no of Zone Director',                             
                             }

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):
        self._download_zd_image()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('zd_fw_upgrade_cfg'):
            self.conf['zd_fw_upgrade_cfg'] = self.carrierbag['zd_fw_upgrade_cfg']
    
    def _update_carrier_bag(self):
        self.carrierbag['image_file_path'] = self.image_file_path

    def _download_zd_image(self):
        '''
        Download ZD image from specified build server.
        '''
        try:
            logging.info('Get build server, stream and no information')
            if self.conf.has_key('zd_fw_upgrade_cfg'):
                up_flag = True
                if self.conf.has_key('up_flag'):
                    up_flag = self.conf['up_flag']
                model = 'zd'
                up_cfg = self.zd_fw_upgrade_cfg['up_cfg']
                build_server = self.zd_fw_upgrade_cfg['build_server']
                if up_cfg.has_key(model):
                    model_up_cfg = up_cfg[model]
                    if up_flag:
                        zd_build_stream = model_up_cfg['target_build_stream']
                        zd_bno = int(model_up_cfg['target_bno'])
                    else:
                        zd_build_stream = model_up_cfg['baseline_build_stream']
                        zd_bno = int(model_up_cfg['baseline_bno'])                                
                else:
                    model_up_cfg = {}
                    self.errmsg('No upgrade config for specified model %s' % (model,))
            else:
                zd_build_stream = self.conf['zd_build_stream']
                zd_bno = self.conf['zd_bno']
                if self.conf.has_key('build_server'):
                    build_server = self.conf['build_server']
                else:
                    build_server = None
            
            self.image_file_path = self._download_image(build_server, zd_build_stream, zd_bno)
            
            logging.info('The image file is %s' % self.image_file_path)
            self.passmsg = "Download and get image files for %s: location[%s], Build stream[%s], Build no[%s]" % \
                                (model, os.getcwd(), zd_build_stream, zd_bno)  
        except Exception, ex:
            self.errmsg = ex.message      

    def _escape(self, file_path):
        expr = "[/|\\^\\\\]"
        return re.sub(expr, "\\\\", file_path)        
    
    def _download_image(self, build_server, build_stream, fw_bno):
        '''
        Download image from build server based on build stream, build no,
        if the image does not exist in rat folder.
        Image file name format is <Build Stream>.<Build No>.tar.gz, in rat folder.
        '''
        chk_name = "%s.%s.tar.gz" % (build_stream, fw_bno)
         
        if not os.path.exists(chk_name):
            logging.info('Download the image [%s,%s] for ZD from %s' % (build_stream, fw_bno, build_server))
            if build_server:            
                fname = imgres.download_build(build_stream, fw_bno, build_server)
            else:
                fname = imgres.download_build(build_stream, fw_bno)
        else:
            logging.info('Image file exists in local')
            fname = chk_name          
              
        fw_tar_filename = self._escape(os.path.realpath(fname))
        
        #filetype='zd.+_.+.ap_.+\.img' #'.+\.Bl7$',
        #fw_img_full_path = imgres.get_image(fw_tar_filename, filetype = filetype)
        #fw_img_filename = fw_img_full_path.split("/")[-1]
        
        return fw_tar_filename  