import uuid,time,random
def uniqid():
    return str(uuid.uuid5(uuid.uuid4(),str(time.time())))
def splitjsons(text):
    ret = []
    text = text.strip()
    unbalance = 0
    starts = '{[('
    ends   = '}])'
    i      = 0
    while text != '':
        if text[i] in starts:
            unbalance += 1
        elif text[i] in ends:
            unbalance -= 1
        i += 1
        if unbalance == 0:
            ret.append(text[0:i])
            text = text[i:].strip()
            i = 0
    return ret
