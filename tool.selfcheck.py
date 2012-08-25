# -*- coding: utf-8 -*-

import os,sys
from xi.hashes import Hash
from _util import colorshell

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
def ls(parameters):
    global BASEPATH
    r2 = []
    for path, suffix in parameters:
        lst = os.listdir(path)
        r1 = []
        if suffix != None:
            for each in lst:
                if each.endswith(suffix): r1.append(each)
        else:
            r1 = lst
        r1.sort()
        for each in r1:
            r2.append(os.path.join(BASEPATH,path,each))
    return r2

def sumfiles(filelist):
    global BASEPATH
    hashpart = []

    for each in filelist:
        hashpart.append(Hash('whirlpool',open(each,'r').read()).hexdigest())

    return Hash('sha224',''.join(hashpart)).hexdigest()
    
def sumhashes(hashlist,algo='sha224'):
    hashlist.sort()
    return Hash(algo,''.join(hashlist)).hexdigest()

def friendly_display(h,centerw=80):
    h = h.upper()
    ret = ''
    while h != '':
        ret += h[0:4] + ' '
        h = h[4:]
    return ret.strip().center(centerw)

def do():
    items = [
        ('Root public certificates', [('xi/user/rootcerts',None)]),
        ('Kernel Programs'         , [('xi/','.py'),('xi/ciphers','.py'),('xi/hashes','.py'),('.','.py'),('gui/','.py')]),
    ]
    result = {}
    print colorshell("Self-checking, this may take a few minutes.",1,0)
    for itemname, listp in items:
        print "Calculating checksums: %s" % itemname
        result[itemname] = sumfiles(ls(listp))

    total = sumhashes(result.values(),'md5')

    print colorshell("Compare following checksums with your paper records.",1,0)
    print "A mismatch is a sign of modification to the relative part."
    print "If you're not sure why mismatch, be cautious using the entire system."
    print "If you're confident with system security and integrity, update paper records.\n"

    print 'Total checksum (for quick examination):'
    print colorshell(friendly_display(total),32,1)
    i = 1
    for itemname in result:
        print "[%d] %s:\n%s" % (i, itemname, colorshell(friendly_display(result[itemname]),32,1))
        i += 1

if __name__ == '__main__':
    do()
