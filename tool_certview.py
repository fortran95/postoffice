#-*- coding: utf-8 -*-
import os
import sys

from xi.certificate import certificate

if len(sys.argv) < 2:
    print "Usage: python tool_certview.py PATH_FOR_CERTIFICATE"
    exit()
path = sys.argv[1]
if not os.path.isfile(path):
    print "Bad path specified."
    exit()

try:
    c = certificate()
    c.load_public_text(open(path,'r').read())
except:
    try:
        c = certificate()
        c.load_private_text(path)
    except:
        print "Cannot load certificate."
        exit()

def friendly_hash(i):
    i = i.upper()
    r = ''
    while i:
        r += i[0:2] + ' '
        i = i[2:]
    return r.strip()

print "0.00.01 证书类型 :: %s" % (bool(c.is_ours) and '私有' or '公开')
print "0.00.02 ID       :: %s" % friendly_hash(c.get_id())
print "0.00.03 证书主题 :: %s" % c.subject
print "0.00.04 等级     :: %s" % c.level

i = 0
for sig in c.signatures:
    i += 1
    headnum = "1.%2s" % str(i).zfill(2)
    print ""
    print "%s.01 签名类型 :: %s" % (headnum, sig['Content']['Title'] == 'New_Signature' and '新签名' or '撤销签名')
    print "%s.02 签发者ID :: %s" % (headnum, friendly_hash(sig['Content']['Issuer_ID']))
    print "%s.03 信任等级 :: %s" % (headnum, sig['Content']['Trust_Level'])
    print "%s.04 签发时刻 :: %s" % (headnum, sig['Content']['Issue_UTC'])
    print "%s.05 到期时刻 :: %s" % (headnum, sig['Content']['Valid_To'])
    print "%s.06 摘要算法 :: %s" % (headnum, sig['Content']['Cert_Hash_Algorithm'].upper())
