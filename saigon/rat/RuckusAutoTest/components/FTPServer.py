# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
FTPServer component is used to when testbed need to download/upload file. 
For example: 
- Standalone RuckusAP needs to upload control file and image to FTP server before 
perform firmware update. 
Note: option overwrite file should be checked to avoid exception when upload control/image file that already existed

Examples:

    from ratenv import *
    # startup local TFTP server
    f = FTPServer.FTPServer(dict(ip_addr='localhost'))
    f.upload_file('testbuild.py')
    
"""
import os
import logging
import ftplib

from RuckusAutoTest.models import TestbedComponent, ComponentBase
from RuckusAutoTest.common import Ratutils as utils

class FTPServer(ComponentBase):

    def __init__(self, config):
        """
        initialize the default information that need to connect with FTP server
        """
        component_info = TestbedComponent.objects.get(name = 'FTPServer')
        ComponentBase.__init__(self, component_info, config)
        self.conf = dict(ip_addr = '192.168.0.20',
                         protocol = 'TFTP',
                         username = 'anonymous',
                         password = '',
                         rootpath = '',
                         init = True,
                         debug = 0,
                        )
        self.conf.update(config)
        if self.conf['init']: self.initialize()

    def initialize(self):
        self.ip_addr = self.conf['ip_addr']
        self.protocol = self.conf['protocol']
        self.username = self.conf['username']
        self.password = self.conf['password']
        self.rootpath = self.conf['rootpath'] 

    def verify_component(self):
        """ Perform sanity check on the component: can ping FTPServer """
        logging.info("Sanity check: Verify Test engine can ping FTPServer")
        # Can ping 
        if "Timeout" in utils.ping(self.ip_addr):
            raise Exception("FTPServer sanity check fails: cannot ping %s " % self.ip_addr)

            
    def upload_file(self, local_path):
        """
        The upload_file will detect the file type (binary/text) to use appropriate method in ftplib
        - local_path     : path + file name are uploaded
        - server_path    : path on FTP server where file is uploaded. By Default, it uses root folder         
        """
        try:
            ftpsrv = ftplib.FTP(self.ip_addr, self.username, self.password)
            # open local file to analyze file type, size        
            fp = open(local_path, "rb")            
            sfsize = os.path.getsize(local_path)            
            temp = fp.read(2048)
            fp.seek(0, 0)
            
            # check file type
            remote_file = '%s%s' % (self.rootpath, os.path.basename(local_path))
            logging.info("uploading file to %s server... " % self.protocol)            
            if temp.find('\0') != -1:
                ftpsrv.storbinary("STOR %s" % remote_file, fp)
            else:
                ftpsrv.storlines("STOR %s" % remote_file, fp)                           
            
            fp.close()
            ftpsrv.quit()
            logging.info("upload DONE")
        except:
            raise Exception("Connect to server %s with user name = %s, password = %s upload file %s" % \
                            (self.ip_addr, self.username, self.password, local_path))
            
    def get_ip_addr(self):     
        return self.ip_addr
    
    def get_protocol(self):
        return self.protocol
    
    def get_username(self):
        return self.username
    
    def get_password(self):
        return self.password
    
    def get_root_path(self):
        return self.rootpath  
