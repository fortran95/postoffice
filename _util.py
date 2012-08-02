import uuid,time,random,logging,os,sys

BASEPATH       = os.path.realpath(os.path.dirname(sys.argv[0]))
PATH_log       = os.path.join(BASEPATH,'system.log')
PATH_alias     = os.path.join(BASEPATH,'config','alias.cfg')
PATH_certs_pub = os.path.join(BASEPATH,'certificates','public')
PATH_certs_prv = os.path.join(BASEPATH,'certificates','secret')
###################################################################################################

logging.basicConfig(
    filename    = PATH_log,
    level       = logging.INFO,
    format      = '[%(asctime)-19s][%(levelname)-8s] %(name)s (%(filename)s:%(lineno)d)\n  %(message)s\n',
    datefmt     = '%Y-%m-%d %H:%M:%S'
    )
#logging.setLoggerClass(ColoredLogger)

###################################################################################################
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
