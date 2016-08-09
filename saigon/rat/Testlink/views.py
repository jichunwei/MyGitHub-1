# Create your views here.
from django.template import RequestContextfrom django.shortcuts import render_to_responsefrom django.shortcuts import HttpResponse

from Testlink import models as tl_m
from RuckusAutoTest import models as rat_m

def bacthviewer(request):
    """
    """
    batch_list = rat_m.Batch.objects.all()
    batch_list = batch_list.reverse()
    return render_to_response("admin/rat_tl/batchviewer.html",
                              {'batch_list':batch_list},
                               RequestContext(request, {}),
                             )