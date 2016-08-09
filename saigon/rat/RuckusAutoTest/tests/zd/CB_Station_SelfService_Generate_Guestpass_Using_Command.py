'''
Description:
    Station generate guest pass  with self service using command
    This ats usually generate max guestpass 
    ps:  zd 3k  max guestpass: 1w
         hour : about 4 hours
Create on 2015-4-15
@author: yanan.yu
'''
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib



class CB_Station_SelfService_Generate_Guestpass_Using_Command(Test):
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
   
        self._generate_guestpass_with_selfservice_using_command()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
 
        return self.returnResult("PASS", self.passmsg)

    def cleanup(self):
        '''
        '''
        pass
    

    def _init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'sta_ins':"",
            'sta_tag': "sta_1",
            'expect_guestpass_count':0,   
            'multi_guestpass_time_out':3600*5,
       }
        
        self.conf.update(conf)

        self.sta_tag = self.conf['sta_tag']
        self.zd = self.testbed.components['ZoneDirector']
        self.zd_ip = self.zd.ip_addr
        
        self.errmsg = ""
        self.passmsg = ""

    def _retrive_carrier_bag(self):
        '''
        '''
        self.sta = self.conf.get('sta_ins')
        if not self.sta and self.sta_tag:
            sta_dict = self.carrierbag.get(self.sta_tag)
            self.sta = sta_dict.get('sta_ins')

        if not self.sta:
            raise Exception("No station provided.")

            
    def _generate_guestpass_with_selfservice_using_command(self):
        
        logging.info("zd ip is %s"%self.zd_ip)
        
        arg = {'expect_guestpass_count':self.conf.get('expect_guestpass_count'),
               'zd_ip':self.zd_ip,
               'multi_guestpass_time_out':self.conf.get('multi_guestpass_time_out')
               }
        try:
            message = self.sta.generate_multi_guestpass_with_selfservice_using_command(arg)
            logging.info(message)
            messages = eval(message)
            
            if messages.get('status') == True:
                self.passmsg = messages.get('message')
            else:
                self.errmsg = messages.get('message')    
            
            
        except Exception, ex:
            self.errmsg += "exception,"+ex.message  
            
            

