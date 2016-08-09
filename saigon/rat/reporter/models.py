from django.db import models
from RuckusAutoTest import models as ratdb

class PhysicalTB(models.Model):
    """
    A Physical test bed information including IP address and port, 
    which will be used for pull data from others test beds. 
    """
    ipaddr = models.IPAddressField(unique=True)
    port = models.IntegerField(default=8009)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return '%s:%d' % (self.ipaddr, self.port)
        

class LogicalTB(models.Model):
    """
    A testbed info class that encapsulates common info and configuration.
    Real testbed class implementations will contain an instance of this class.
    Ideally this would be implemented as an abstract base class but django models doesn't currently support ABC's.
    """
    name         = models.CharField(unique=True, max_length=50,
                                    help_text='Unique name for this physical testbed')    
    physical       = models.ForeignKey(PhysicalTB)    
    location     = models.CharField(max_length=100)    
    owner        = models.EmailField("Owner Email",
                                     help_text='Address for reporting testbed problems.')    
    resultdist   = models.EmailField("Results Email",
                                     help_text='Default address for emailing batch results')    
    description  = models.TextField(blank=True)
    config       = models.TextField(blank=True,
                                    help_text='Basic testbed configuration parameters (e.g. DUT IP address) as a python dictionary string')
    
    suites       = models.ManyToManyField(ratdb.TestSuite, null=True,
                                          help_text="list of test suites to run for this batch",
                                          )

    def __unicode__(self):
        return self.name
    
    def suite_list(self):
        """return a list of suites for display purposes"""
        return ','.join([s.__unicode__() for s in self.suites.all()])    

class DailyStatus(models.Model):
    """
    Including PTB, LTB, Version, Status, Description, Report_Date, Owner.        
    """
#    logicaltb = models.ForeignKey(LogicalTB)
    ipaddr = models.IPAddressField() 
    name = models.CharField(max_length=50,
                                    help_text='Unique name for this logical TB')
    version = models.CharField(max_length=20,
                               help_text = "Show current version of\
                               ie. 9.7.0.0.24 logical testbed.",                               
                               )
    status = models.CharField(max_length=20,
                              help_text = "Display status of current test bed\
                              ie. PASS  90%, Fail 5%, ERROR 5%"
                              )
    description = models.CharField(max_length=100,
                                   help_text = "Comment for this test bed, bug \
                                   majority feature like SNMP/IPV6 etc." 
                                   )
    
#    report_date = models.DateTimeField(help_text="Finished test time.")
    
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    suites = models.TextField(blank=True)
    
    def __unicode__(self):
        return '%s#%s#%s' % (self.name, 
                           self.version,
                           self.status,                           
                           )
    
    class Meta:
        ordering = ('-version',)
    
#    def link2(self):
#        obj = PhysicalTB.objects.filter(self.ipaddr)
#        atag = "%s" % self.ipaddr
#        if obj:
#            obj = obj[0]
#            atag = "<a herf='http://%s:%s' target='_blank'>%s</a>"
        
#        unique_together = ("logicaltb", "version")    