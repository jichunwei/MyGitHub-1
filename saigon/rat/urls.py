from django.conf.urls.defaults import *
from jsonrpc import jsonrpc_site

import RuckusAutoTest.views
import Testlink.views

from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover

admin.autodiscover()
dajaxice_autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^RuckusAutoTest/', include('RuckusAutoTest.foo.urls')),

    # Uncomment this for admin:
     (r'^admin/report/$', 'RuckusAutoTest.views.report'),
     (r'^admin/rat_tl/$', 'Testlink.views.bacthviewer'),
     (r'^admin/reportdetail/([^/]+)$', 'RuckusAutoTest.views.reportdetail'),
     (r'^admin/([^\/]+)/([^\/]+)/xls/$', 'RuckusAutoTest.views.export_xls_model'),
     #(r'^admin/', include('django.contrib.admin.urls')),
     (r'^admin/(.*)', admin.site.root),


    # allow non-admin user to access test results
     (r'^$', 'RuckusAutoTest.views.ratWorld'),
     (r'^report/$', 'RuckusAutoTest.views.ratWorld'),
     (r'^reportdetail/([^/]+)$', 'RuckusAutoTest.views.reportdetail'),

    # export report as xls files
     (r'^xls/report/$', 'RuckusAutoTest.views.export_xls_report'),
     (r'^xls/reportdetail/([^/]+)$', 'RuckusAutoTest.views.export_xls_reportdetail'),
     (r'^xls/([^\/]+)/([^\/]+)/$', 'RuckusAutoTest.views.export_xls_model'),
)

urlpatterns += patterns('',
    (r'^json/', jsonrpc_site.dispatch)
)

import settings
urlpatterns += patterns('',
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)
