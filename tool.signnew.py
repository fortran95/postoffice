# -*- coding: utf-8 -*-

# 用于产生证书的签名和导入签名

import _util
from xi.certificate import certificate
from gui.selector   import selector
from gui.inputbox   import inputbox
from gui.pinreader  import pinreader
import logging,os,sys,ConfigParser

log = logging.getLogger('xi.tool.signnew')

# Read In All Possible Certificates.

c = ConfigParser.ConfigParser()
c.read(_util.PATH_alias)
publiclist  = {}
privatelist = {}
for item in c.sections():
    if c.has_option(item,'Public'):
        publiclist[item] = c.get(item,'Public')
        if c.has_option(item,'Private'):
            privatelist[item] = c.get(item,'Private')

# Choose jobs

jobs = []
if len(privatelist) > 0:
    jobs.append(u'证书信任签署')
    jobs.append(u'证书吊销签署')
if len(publiclist) > 0:
    jobs.append(u'导入签署信息')

job = selector('选择任务：',jobs)

if job == False:
    exit()
else:
    jobid = jobs.index(job)


if jobid == 2: # 导入证书签名
    signtxt = inputbox('请将签名文本粘贴（Ctrl+V）到下面：','导入签名',True)
    print signtxt
else:
    if jobid == 0:
        pass
    elif jobid == 1:
        pass
    # 读入所有的证书信息
    signtarget = selector('请选择要签署的证书持有人：',publiclist.keys())
    if signtarget == False:
        exit()

    signwith   = selector('请选择要用作签署的私有证书：',privatelist.keys())
    if signwith == False:
        exit()

    trustlevel = 1 # FIXME ask user input.
    signlife   = 120 * 86400 # FIXME ask userinput

    log.info('[%s] is trying to sign [%s].',signwith,signtarget)

    signer = certificate()
    holder = certificate()

    def _pinreader(b=False,p1='',p2=''):
        msg = '即将签署以下证书：\n [%s]\n\n需要您输入密码解密以下证书：\n [%s]' % (signtarget,signwith)
        return pinreader(b,message=msg)
    
    holder.load_public_text  ( open( os.path.join(_util.BASEPATH,publiclist[signtarget]) ,'r').read() )
    try:
        signer.load_private_text (privatelist[signwith],_pinreader)
    except Exception,e:
        print "退出签署程序。密码错误或者用户手动取消。"
        log.warning('Sign process exited, either of a wrong passphrase, or had been cancelled manually.')

    signature = signer.sign_certificate(holder,trustlevel,signlife)
    print signature
