# -*- coding: utf-8 -*-

import os,sys,zlib
from xi.hashes import Hash
from _util import colorshell

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
def ls(parameters):
    global BASEPATH
    r2 = []
    for path, suffix in parameters:
        lst = os.listdir(os.path.join(BASEPATH,*path))
        r1 = []
        if suffix != None:
            for each in lst:
                if each.endswith(suffix): r1.append(each)
        else:
            r1 = lst
        r1.sort()
        for each in r1:
            r2.append(os.path.join(os.path.join(BASEPATH,*path),each))
    return r2

def sumfiles(filelist,include_list=True):
    global BASEPATH
    hashpart = []

    for each in filelist:
#        hashpart.append(Hash('whirlpool',open(each,'r').read()).hexdigest())  #
        filec = open(each,'r').read()
        hashinput = filec + ';' + str(len(filec))
        hashpart.append(Hash('sha1',hashinput).digest())

    if include_list:
        hashpart.append(Hash('sha1',' '.join(filelist)).digest())

    return Hash('sha224',''.join(hashpart)).hexdigest()
    
def sumhashes(hashlist):
    hashlist.sort()
    return Hash('sha224',''.join(hashlist)).hexdigest()

def friendly_display(h,centerw=80):
    h = h.upper()
    ret = ''
    while h != '':
        ret += h[0:4] + ' '
        h = h[4:]
    return ret.strip().center(centerw)

def do(silent=True):
    items = [
        ('Root public certificates', [(('xi','user','rootcerts'),None)]),
        ('Config Files'            , [(('config',),'alias.cfg')]),
        ('Kernel Programs'         , [(('xi',),'.py'),(('xi','ciphers'),'.py'),(('xi','hashes'),'.py'),(('',),'.py'),(('gui',),'.py')]),
    ]
    result = {}
    print "Self-checking, this may take a few minutes."
    for itemname, listp in items:
        print "Calculating checksums: %s" % itemname
        result[itemname] = sumfiles(ls(listp))

    hashsum = sumhashes(result.values())
    total = str(hex(zlib.crc32(hashsum) & 0xFFFFFFFF))[2:10] + str(hex(zlib.adler32(hashsum) & 0xFFFFFFFF))[2:10]

    if not silent:
        print colorshell("Compare following checksums with your paper records.",1,0)
        print "A mismatch is a sign of modification to the relative part."
        print "If you're not sure why mismatch, be cautious using the entire system."
        print "If you're confident with system security and integrity, update paper records.\n"

        print 'Total checksum (for quick examination): %s' % colorshell(friendly_display(total).strip(),32,1)
        i = 1
        for itemname in result:
            print "[%d] %s:\n%s" % (i, itemname, colorshell(friendly_display(result[itemname]),32,1))
            i += 1
    result = {'total':total,'parts':result}
    return result

if __name__ == '__main__':
    print do()
