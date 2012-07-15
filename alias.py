# -*- coding: utf-8 -*-

# config/addressbook.txt 的解析器
# 用于输出：从一个应用的特定账户接受信息时，采用的证书
#           以及通过特定应用指定接受账户时，采用的证书
import ConfigParser,os,sys
from xi import certificate

BASEPATH = os.path.realpath(os.dirname(sys.argv[0]))

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
    except:
        pass
    return False

# 本函数可以根据配置文件返回证书实例
def get_cert(account,software,path='config/alias.cfg',secret=False):
    global BASEPATH
    secname = get_certsubject(account,software,path)
    if secname = False:
        return False
    cfg = ConfigParser.ConfigParser()
    try:
        cfg.read(path)
        ret = certificate.certificate()
        if secret:
            if cfg.has_option(secname,'Private'):
                filepath = os.path.join(BASEPATH,cfg.get(secname,'Private'))
                ret.load_private_text(filepath)# XXX pinreader
            else:
                return False
        else:
            if cfg.has_option(secname,'Public'):
                filepath = os.path.join(BASEPATH,cfg.get(secname,'Private'))
                ret.load_public_text(open(filepath,'r').read())

            elif cfg.has_option(secname,'Private'):
                filepath = os.path.join(BASEPATH,cfg.get(secname,'Private'))
                ret.load_private_text(filepath)# XXX pinreader

            else:
                return False
        return ret
    except:
        pass
    return False
if __name__ == "__main__":
    print get_certsubject('845044623','qq')
