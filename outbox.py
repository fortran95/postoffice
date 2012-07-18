# -*- coding: utf-8 -*-

import letter,alias,keys

def process_letter(l):
    sender   = alias.get_cert(l.attributes['SENDER'],l.attributes['VIA'],True)
    receiver = alias.get_cert(l.attributes['RECEIVER'],l.attributes['VIA'],False)

    if sender == False or receiver == False:
        raise Exception("Cannot find sender or/and receiver's certificate.")

    k = keys.keys()
    nkf = k.new(sender,receiver,True)
    #print nkf
    
    #���Գ���Կ�Ƿ���ڣ�Ȼ�󷢳���������+���ģ�����ֱ���öԳ���Կ+����

l = letter.letter()
l.read('boxes/outgoing/queue/sample.letter')
process_letter(l)
