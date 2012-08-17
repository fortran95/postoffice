# -*- coding: utf-8 -*-
import uuid,time,random,logging,os,sys,shelve

BASEPATH       = os.path.realpath(os.path.dirname(sys.argv[0]))
PATH_log       = os.path.join(BASEPATH,'system.log')
PATH_alias     = os.path.join(BASEPATH,'config','alias.cfg')
PATH_certs_pub = os.path.join(BASEPATH,'certificates','public')
PATH_certs_prv = os.path.join(BASEPATH,'certificates','secret')
PATH_cache     = os.path.join(BASEPATH,'secrets','cached.db')
PATH_output    = os.path.join(BASEPATH,'boxes','output')

CONFIG_cache_password_life = 3600
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

###################################################################################################
def cache_get(key):
    global PATH_cache
    c = shelve.open(PATH_cache,writeback=True)
    nowtime = time.time()
    for k in c:
        if c[k] == None:
            continue
        if c[k][1] < nowtime:
            c[k] = None
    if c.has_key(key):
        item = c[key]
        if item != None:
            return item[0]
    return None
def cache_set(key,value,life):
    global PATH_cache
    c = shelve.open(PATH_cache,writeback=True)
    nowtime = time.time()
    c[key] = (value,nowtime + life)
def cache_del(key):
    global PATH_cache
    c = shelve.open(PATH_cache,writeback=True)
    if c.has_key(key):
        c[key] = None
###################################################################################################
def serious_confirm(prompt):
    chk = raw_input("\n--- 严重警告 ---\n%s\n\n如仍想继续，请抄写括号内的单词 [CONTINUE ANYWAY]:" % prompt)
    if chk != 'CONTINUE ANYWAY':
        return False
    return True
