import sys

sys.path += ['../../RatToolAgent']

import RatToolAgent as rta

id = rta.init_and_start_browser()

conf = {
            'validation_url': "http://172.16.10.252/authenticated/",
            'download_loc': r"//a[@id='logo']",
            'file_name': "logo.zip",
            'page_title': "Ruckus Automation Test",
        }

try:
    rta.download_file_on_web_server(id, conf.pop('validation_url'),
                                conf.pop('download_loc'),
                                conf.pop('file_name'),
                                **conf
                               )
except Exception, e:
    print '........................................'
    print 'Raise:' + e.message


rta.close_browser(id)

