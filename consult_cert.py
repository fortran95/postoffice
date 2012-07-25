#-*- coding: utf-8 -*-
from xi.securelevel import securelevel as sl
import os,sys

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
ROOTCERTPATH = os.path.join(BASEPATH,'xi','user','rootcerts')
got_rootcerts = {}

def draw_certbox(cert,isroot,indent=0,trustlevel=None,width=42):
    subject = cert.subject
    if len(subject) > width - 4:
        subject = subject[0:width - 8] + '...'
    fid = cert.get_id()
    showid1,showid2 = '',''
    for i in range(0,len(fid)/2):
        if i <= len(fid) / 4 - 1:
            showid1 += fid[i*2:i*2+2] + ' '
        else:
            showid2 += fid[i*2:i*2+2] + ' '
    indents = ' ' * indent
    if trustlevel != None:
        ret = indents + '+' + ('| TrustLevel ' + str(trustlevel) + ' |').center(width - 2,'-') + '+\n'
    else:
        ret = indents + '+' + '-' * (width-2) + '+\n'
    ret += indents + '| Subject:' + ' ' * (width-11) + '|\n'
    ret += indents + '|  ' + subject + ' ' * (width - 4 - len(subject)) + '|\n'
    ret += indents + '| FingerPrint:  ' + showid1 + ' ' * (width - 17 - len(showid1)) + '|\n'
    ret += indents + '|' + ' ' * 15 + showid2 + ' ' * (width - 17 - len(showid2)) + '|\n'
    if isroot == True:
        ret += indents + '| ' + ' Root Certificate Confirmed '.center(width-4,':') + ' |\n'
    elif isroot == False:
        ret += indents + '| ' + ' CAUTION: NOT root certificate! '.center(width-4,':') + ' |\n'

    ret += indents + '+' + '-' * (width-2) + '+\n'

    return ret

def printbox(consultant,result,indent,trustlevel=None):
    global got_rootcerts
    ret = ''
    for each in result:
        certid     = each[0:each.find('.')]
        trustlevel = each[each.find('.') + 1:]
        cert       = consultant.indexes[certid][0]
        isroot     = consultant.indexes[certid][1]
        if type(result[each]) == bool:
            ret += draw_certbox(cert,isroot,indent,trustlevel)
            if isroot:
                got_rootcerts[certid] = cert
        else:
            if isroot == False:
                isroot = None
            ret += draw_certbox(cert,isroot,indent,trustlevel)
            ret += printbox(consultant,result[each],indent + 5)
    return ret

def report(sendercert):
    global BASEPATH, ROOTCERTPATH,got_rootcerts
    ret = ''
    got_rootcerts = {}
    consultant = sl(ROOTCERTPATH)
    consultant.initilize([
        os.path.join(BASEPATH,'xi','user','usercerts'),
        os.path.join(BASEPATH,'certificates','public'),
    ])
    conr = consultant.consult(sendercert)

    if conr != True and conr != False:
        conrboxes = printbox(consultant,conr,2)
        authmsg = u' 本证书经过如下根证书签署：\n'
        for x in got_rootcerts:
            authmsg += '  [%s]' % got_rootcerts[x].subject + '\n'
        authmsg += u' 具体关系图为：\n'
        authmsg += conrboxes
    elif conr == True:
        authmsg = u' 这是一个根证书，可以相信。'
    elif conr == False:
        authmsg = u' 本证书携带的签名不能辨认，无法确认其可信性。'


    ret = u"""
证书信息
========
%s
认证意见
========
%s
    """ % (draw_certbox(sendercert,None),authmsg)

    return ret.strip()

if __name__ == '__main__':
    from xi.certificate import certificate as certi
    x = certi()
    x.load_public_text(open(os.path.join(BASEPATH,'xi','user','usercerts','sl.pub')).read())
    boxstr = report(x)

    from gui.sender_confirm import senderconfirm as sc
    print sc(boxstr)
