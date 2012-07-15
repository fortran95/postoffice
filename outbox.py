# -*- coding: utf-8 -*-

import letter,alias,certmanager

def process_letter(l):
    sendercert_subject   = alias.get_certsubject(l.attributes['SENDER'],l.attributes['VIA'])
    receivercert_subject = alias.get_certsubject(l.attributes['RECEIVER'],l.attributes['VIA'])

    print sendercert_subject,'->',receivercert_subject
    # 确定了发送者，接收者，检查对应证书情况
    sendercert   = certmanager.find(sendercert_subject)
    receivercert = certmanager.find(receivercert_subject)
    
    #检查对称密钥是否存在，然后发出交换申请+密文，或者直接用对称密钥+密文

l = letter.letter()
l.read('boxes/outgoing/queue/sample.letter')
process_letter(l)
