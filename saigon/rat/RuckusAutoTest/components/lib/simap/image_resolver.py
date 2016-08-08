'''
Description:
    All of SimAP Images which can be fetched from Lhotse Server, simap_image_resover is used for downloading
    SimAP image and put it to hard disk(i.e: c:/).
Usage:
    tea.py <simap_image_resolver key/value pair> ...
    
    where <simap_image_resolver key/value pair> are:
        
        buildstream  :   catch it from lhotse
        bno          :   number of buildstream
        filepath      : 'which location will be saved to(save image file)'
        
    notes:
        if you haven't support filepath, system will save image file to current folder by default
    
Examples:
    tea.py simap_image_resolver te_root=u.zd.simap buildstream='SIM-AP_8.2.0.0_production' bno=4
    tea.py simap_image_resolver te_root=u.zd.simap buildstream='SIM-AP_8.2.0.0_production' bno=4 filepath='d:\'
    tea.py simap_image_resolver te_root=u.zd.simap buildstream='SIM-AP_8.2.0.0_production' bno=4 filepath='d:\' debug=True
    
Created on 2010-2-5    
@author: Administrator
'''
from contrib.download import image_resolver

def main(**kwargs):
    
    cfg = dict(buildstream='SIM-AP_8.2.0.0_production',
               bno=4,
               filepath='d:/',
               debug=False)
    cfg.update(kwargs)
    if cfg['debug']:
        import pdb
        pdb.set_trace()
        
    fname = image_resolver.download_build(cfg['buildstream'], cfg['bno'])
    img_filename= image_resolver.get_image(fname, filetype=".+\.Bl7$")
    filepath = cfg['filepath']
    if filepath:
        image_resolver.mv_file(img_filename, filepath,  tname="rcks_fw.bl7")
        
    return {'PASS':''}    
    