import uuid,time,random,logging,os,sys

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
logging.basicConfig(filename=os.path.join(BASEPATH,'system.log'),level=logging.INFO)

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
            got = text[0:i]
            if got[0] in starts and got[-1] in ends:
                ret.append(got)
            text = text[i:].strip()
            i = 0
    return ret
