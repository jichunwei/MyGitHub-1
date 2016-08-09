import logging
import re
import os
from tarfile import TarFile

from RuckusAutoTest import models

import multi_threads_downloader as downloader

def download_build(buildstream, bno, buildserver = 'lhotse'):
    """ 
        download build file from lhotse server and return the local file name of build.        
    """
    build_url = "http://%s/cgi-bin/build_info.pl?filename=www_%s" % (buildserver, buildstream)
    bs = models.BuildStream()
    build_list = bs.GetK2Builds(build_url)
    for build in build_list:
        if str(bno) == build['number']:                                
            logging.info("Download...")            
            fname = poll_data(build['URL'], "%s.%s.tar.gz" % (buildstream, build['number']))
            logging.info("Download the build finished")
            return fname
        
    raise Exception("haven't found the build:%d against %s" % (bno, build_url))

def poll_data(url, saveAs):
    filename = saveAs
    downloader.http_get(url, saveAs, 16)
    return filename

def get_image(filename, filetype=".+\.Bl7$"):
    logging.info("Target build image to upgrade is in gz file %s" % filename)
    # Untar image file to the build directory
    tar_file = TarFile.open(filename, 'r:gz')
    names = tar_file.getnames()
    pat_img = filetype
    img_filename = ''
    found = False
    for name in names :
    # begin with Odessa (7.0); version is prefix platform version 1k|3k
        match_obj = re.search(pat_img, name, re.I)
        if match_obj:
            img_filename = match_obj.group(0)
            tar_file.extract(img_filename)
            found = True
            break
        
    if not found:
        raise Exception("File [%s] not found" % filetype)
    
    logging.info("Target build image is %s" % img_filename)
    
    return img_filename
    
def mv_file(f, t, tname="rcks_fw.bl7"):
    if t :
        if os.path.exists(t):            
            fname = str(os.path.realpath(t)) + "\\" + str(tname)
            if os.path.isfile(fname):
                logging.info('remove old file[%s]' % fname)
                os.remove(fname)
                
            logging.info("move to [%s] from [%s]" % (fname, f))
            os.rename(f, fname)
            
        else:
            raise Exception("Invalid file path[%s]" % t)
    
        
