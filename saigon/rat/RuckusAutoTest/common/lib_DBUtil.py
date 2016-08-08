import time

# corner cases:
#
#   dbu.text_field_as_struct('','')        -->> ''
#   dbu.text_field_as_struct("[u'']", '')  -->> ''
#   dbu.text_field_as_struct('','helo')    -->> u"['helo']"
#   dbu.text_field_as_struct('helo', '')   -->> u"['helo']"
#
def text_field_as_struct(target, text):
    if len(text.strip()) == 0 and len(target.strip()) == 0:
        return ''
    if type(target) in [list, dict]:
        return _as_struct(target, text)

    try:
        field = eval(target)
        field = _as_struct(field, text)
    except:
        if type(target) in [str, unicode] and len(target.strip()) > 0:
            if len(text.strip()) > 0:
                field = [target, text]
            else:
                field = [target]
        elif len(text.strip()) > 0:
            field = [text]
        else:
            field = ''
    # to avoid display [u'']
    if field:
        return unicode(field)
    return ''

def _as_struct(field, text):
    if type(field) == list:
        if len(field) == 1 and not field[0]:
            # it is ['u'']; treat it as blank information
            return ''
        field.append(text)
    elif type(field) == dict:
        ctime = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        field[ctime] = unicode(text)
    else:
        field = str(field) + "\n" + text
    return field

# base_time = time.time()
# do-something-wonderful ...
# testrun.message = text_field_as_dict(testrun.message, message, base_time)
def text_field_as_dict(target, text, base_time):
    e_minutes = int(round(((time.time() - base_time) / 60.0)))
    time_started = time.strftime("%y%m%d-%H%M", time.localtime(base_time))
    new_pair = {time_started:[e_minutes, text]}
    try:
        field = eval(target)
        if type(field) in [dict]:
            field.update(new_pair)
        else:
            field = new_pair
    except:
        field = new_pair
        
    return str(field)

