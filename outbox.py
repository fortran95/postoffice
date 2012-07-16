# -*- coding: utf-8 -*-

import letter,alias

def process_letter(l):
    sender   = alias.get_cert(l.attributes['SENDER'],l.attributes['VIA'],True)
    receiver = alias.get_cert(l.attributes['RECEIVER'],l.attributes['VIA'],False)

    if sender == False or receiver == False:
        raise Exception("Cannot find sender or/and receiver's certificate.")
    
    #检查对称密钥是否存在，然后发出交换申请+密文，或者直接用对称密钥+密文

l = letter.letter()
l.read('boxes/outgoing/queue/sample.letter')
process_letter(l)
