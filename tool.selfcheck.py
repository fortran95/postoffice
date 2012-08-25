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
    
def sumhashes(hashlist):
    hashlist.sort()
    return Hash('sha224',''.join(hashlist)).hexdigest()

def friendly_display(h,centerw=79):
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
    print "Self-checking, this may take a few minutes."
    for itemname, listp in items:
        print "Calcuating checksums: %s" % itemname
        result[itemname] = sumfiles(ls(listp))

    print colorshell("Compare following checksums with your paper records.",1,0)
    print "Mismatching tells that part's been modified. If you're not sure that's what you have done, be cautious using the entire system."
    print "If you are confident with system security, update your paper records."
    print ''
    i = 1
    for itemname in result:
        print "[%d] %s:\n %s" % (i, itemname, colorshell(friendly_display(result[itemname]),32,1))
        i += 1

if __name__ == '__main__':
    do()
