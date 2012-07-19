# -*- coding: utf-8 -*-

import letter,alias,keys

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

    trans = k.encrypt(l.body,False)
    outputbuffer.append(trans)

    return outputbuffer


l = letter.letter()
l.read('boxes/outgoing/queue/sample.letter')
try:
    r = process_letter(l)
    for i in r:
        print i
except:
    pass
