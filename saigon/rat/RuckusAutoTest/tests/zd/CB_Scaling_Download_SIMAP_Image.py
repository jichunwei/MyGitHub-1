'''
Created on 2010-5-14

@author: lab
'''
import re
import os

from RuckusAutoTest.models import Test

from contrib.download import image_resolver as imgres

class CB_Scaling_Download_SIMAP_Image(Test):
    required_components = []
    parameter_description = {'simap_build_stream' :     'build stream of SIMAP',
                             'simap_bno'          :     'build no of SIMAP',
                             'file_path'          :     'The file path of tftp server respo.',
                             }

    def config(self, conf):
        self.errmsg = ""
        self.passmsg = ""        
        self.conf = conf        
        self.conf.update(self.carrierbag)
        
    def test(self):
        self.download_simage(self.conf)
        self.carrierbag['sim_version'] = self.conf['sim_version']
        self.carrierbag['file_path'] = self.conf['file_path']
        self.passmsg = "SIMAP image version is[%s]" % self.conf['sim_version']
        return ('PASS', self.passmsg)
    
    def cleanup(self):
        pass

    def download_simage(self, conf):
        """
        download simulator image from lhots
        """
        #cwang@2010-09-16, doesn't download if exists.
        chk_name = "%s.%s.tar.gz" % (conf['simap_build_stream'], conf['simap_bno'])
        if not os.path.exists(chk_name):
            fname = imgres.download_build(conf['simap_build_stream'], conf['simap_bno'])
        else:
            fname = chk_name
            
        img_filename = imgres.get_image(fname, filetype=".+\.Bl7$")
        expr = '^SIM-AP_([\d\.]+)\.Bl7$'
        res = re.match(expr, img_filename, re.I)
        
        if res:
            #bug in saigon
            v = res.group(1)
            conf['sim_version'] = v
    #            self.package_simap_cfg['version'] = self.sim_version
        else:
            errmsg = 'Haven\'t catched simap image from version server.'
            return {"ERROR":errmsg}
            
        if conf['file_path']:
            imgres.mv_file(img_filename, conf['file_path'], tname="rcks_fw.bl7")
            