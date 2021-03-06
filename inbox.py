# -*- coding: utf-8 -*-
import letter,alias,keys,packager
import os,shutil,sys,json,logging
from _util import uniqid,splitjsons

# Process incoming(encrypted) letters.

def process_letter(l):
    sender       = alias.get_cert(l.attributes['SENDER'],l.attributes['VIA'],False)
    receiver_pub = alias.get_cert(l.attributes['RECEIVER'],l.attributes['VIA'],False)
    receiver_prv = None

    if sender == False or receiver_pub == False:
        raise Exception("Cannot find sender or/and receiver's certificate.")

    outputbuffer = []

    jsons = splitjsons(l.body.strip())
    k = keys.keys()

    for j in jsons:
        try:
            jp = json.loads(j)
        except Exception,e:
            print 'Error decoding json: %s' % e
            continue
        try:
            if   jp['Title'] == 'Intermediate_Key':
                if receiver_prv == None:
                    receiver_prv = alias.get_cert(l.attributes['RECEIVER'],l.attributes['VIA'],True)
                    if receiver_prv == False:
                        raise Exception("Cannot find receiver's private certificate.")
                k.load(jp,sender,receiver_prv)
            elif jp['Title'] == 'Message':
                outputbuffer.append(packager.depackage(k.decrypt(jp)))
        except Exception,e:
            raise Exception("%s" % e)

    return outputbuffer

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
PATH_log     = os.path.join(BASEPATH,'system.log')

BASEPATH = os.path.join(BASEPATH,'boxes','incoming')

PATH_queue   = os.path.join(BASEPATH,'queue')
PATH_error   = os.path.join(BASEPATH,'error')
PATH_handled = os.path.join(BASEPATH,'handled')

logging.basicConfig(filename=PATH_log,level=logging.INFO)
log = logging.getLogger('postoffice.inbox')

queued = os.listdir(PATH_queue)
for filename in queued:
    try:
        filepath = os.path.join(PATH_queue,filename)
        l = letter.letter()
        l.read(os.path.join(filepath))
        r = process_letter(l)
        
        ret = letter.letter()
        ret.attributes = {'TAG':l.attributes['TAG'],'VIA':l.attributes['VIA'],'SENDER':l.attributes['SENDER'],'RECEIVER':l.attributes['RECEIVER']}

        for i in r:
            ret.body += i + '\n\r'

        outputfilename = os.path.join(PATH_handled,l.attributes['VIA'] + '.' + uniqid())
        ret.write(outputfilename)

        log.info('Handled one letter: [%s] to [%s] via [%s] tagged [%s].',
            l.attributes['SENDER'],l.attributes['RECEIVER'],l.attributes['VIA'],l.attributes['TAG'])

    except Exception,e:
        
        log.exception("Error processing letter: %s",e)

        # Move to failed
        shutil.copy(filepath,os.path.join(PATH_error,filename))
    os.remove(filepath)
