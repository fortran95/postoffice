# -*- coding: utf-8 -*-

import letter,alias,keys,packager
import os,shutil,sys,json,logging
from _util import uniqid

def process_letter(l):
    sender_pub = alias.get_cert(l.attributes['SENDER'],l.attributes['VIA'],False)
    receiver   = alias.get_cert(l.attributes['RECEIVER'],l.attributes['VIA'],False)

    if sender_pub == False or receiver == False:
        raise Exception("Cannot find sender or/and receiver's certificate.")

    outputbuffer = []

    k = keys.keys()
    do_gen = False

    if not k.find_key(sender_pub,receiver):
        do_gen = True
    elif k.deprecated:
        do_gen = True
    if do_gen:

        sender_prv = alias.get_cert(l.attributes['SENDER'],l.attributes['VIA'],True)
        if sender_prv == False:
            raise Exception("Cannot find sender's private certificate.")
        newkeystr = k.new(sender_prv,receiver,432000,False)
        outputbuffer.append(newkeystr)
    elif k.activated == False and k.deprecated == False and k.exchange_info != '': # Try Key Exchange
        outputbuffer.append(json.dumps(k.exchange_info))

    trans = k.encrypt(packager.package(l.body),False)
    outputbuffer.append(trans)

    return outputbuffer

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))

BASEPATH = os.path.join(BASEPATH,'boxes','outgoing')

PATH_queue   = os.path.join(BASEPATH,'queue')
PATH_error   = os.path.join(BASEPATH,'error')
PATH_handled = os.path.join(BASEPATH,'handled')

log = logging.getLogger('postoffice.outbox')

queued = os.listdir(PATH_queue)
for filename in queued:
    try:
        filepath = os.path.join(PATH_queue,filename)
        l = letter.letter()
        l.read(os.path.join(filepath))
        r = process_letter(l)
        
        ret = letter.letter()
        ret.attributes = {'TAG':l.attributes['TAG'],'SENDER':l.attributes['SENDER'],'RECEIVER':l.attributes['RECEIVER'],'VIA':l.attributes['VIA']}

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
