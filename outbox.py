# -*- coding: utf-8 -*-

import letter,alias,certmanager

def process_letter(l):
    sendercert_subject   = alias.get_certsubject(l.attributes['SENDER'],l.attributes['VIA'])
    receivercert_subject = alias.get_certsubject(l.attributes['RECEIVER'],l.attributes['VIA'])

    print sendercert_subject,'->',receivercert_subject
    # ȷ���˷����ߣ������ߣ�����Ӧ֤�����
    sendercert   = certmanager.find(sendercert_subject)
    receivercert = certmanager.find(receivercert_subject)
    
    #���Գ���Կ�Ƿ���ڣ�Ȼ�󷢳���������+���ģ�����ֱ���öԳ���Կ+����

l = letter.letter()
l.read('boxes/outgoing/queue/sample.letter')
process_letter(l)
