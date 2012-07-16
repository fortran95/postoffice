# -*- coding: utf-8 -*-

# config/addressbook.txt �Ľ�����
# �����������һ��Ӧ�õ��ض��˻�������Ϣʱ�����õ�֤��
#           �Լ�ͨ���ض�Ӧ��ָ�������˻�ʱ�����õ�֤��
import ConfigParser,os,sys
from gui import pinreader
from xi import certificate

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))

def get_certsubject(account,software,path='config/alias.cfg'):
    cfg = ConfigParser.ConfigParser()
    try:
        cfg.read(path)
        software = software.lower()
        for sec in cfg.sections():
            itms = cfg.items(sec)
            for item in itms:
                if item[0].lower() == software:
                    values = item[1].split(' ')
                    for value in values:
                        if value.lower().strip() == account:
                            return sec
                    break
    except Exception,e:
        print "Error in get_certsubject: %s" % e
    return False

# ���������Ը��������ļ�����֤��ʵ��
def get_cert(account,software,secret=False,path='config/alias.cfg'):
    global BASEPATH
    secname = get_certsubject(account,software,path)
    if secname == False:
        return False
    cfg = ConfigParser.ConfigParser()
    try:
        cfg.read(path)
        ret = certificate.certificate()
        if secret:
            if cfg.has_option(secname,'Private'):
                filepath = os.path.join(BASEPATH,cfg.get(secname,'Private'))
                ret.load_private_text(filepath,pinreader.pinreader)
            else:
                return False
        else:
            if cfg.has_option(secname,'Public'):
                filepath = os.path.join(BASEPATH,cfg.get(secname,'Public'))
                ret.load_public_text(open(filepath,'r').read())

            elif cfg.has_option(secname,'Private'):
                filepath = os.path.join(BASEPATH,cfg.get(secname,'Private'))
                ret.load_private_text(filepath,pinreader.pinreader)

            else:
                return False
        return ret
    except Exception,e:
        print "Error loading certificate: %s" % e
    return False
if __name__ == "__main__":
    c = get_cert('744831409','qq',True)
    print c.get_public_text()
