import platform
import os

if platform.system() == "Linux":
    #Linux client version
    ver = os.environ.get("LC_VER", "2.2")
    os_type = "Linux"
elif platform.system() == "Windows":
    ver = "unknown"
    os_type = "Windows"
else:
    ver = "unknown"
    os_type = "unknown"


# result format
def return_result(ok,result_type,data={},others={},caller={}):
    rslt = dict(success=ok,data=data,others=others,caller=caller, platform=os_type, version=ver)
    rslt['result_type'] = result_type
    return rslt


def return_info(data={},others={},caller={}):
    return return_result(True,"info-only",data,others,caller)


def return_pass(data={},others={},caller={}):
    return return_result(True,"pass",data,others,caller)


def return_fail(data={},others={},caller={}):
    return return_result(False,"fail",data,others,caller)


def return_error(data={},others={},caller={}):
    return return_result(False,"error",data,others,caller)

