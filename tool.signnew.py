# -*- coding: utf-8 -*-

# 用于产生证书的签名和导入签名

import _util
from xi.certificate import certificate
from gui.selector   import selector
from gui.inputbox   import inputbox
from gui.pinreader  import pinreader
import logging,os,sys,ConfigParser,json

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
    try:
        signparsed = json.loads(signtxt)
        certified  = signparsed['Content']['Certified_ID']
        issued     = signparsed['Content']['Issuer_ID']
    except:
        log.warning('Given signature cannot be parsed. Data may corrupted.')
        print '证书格式不正确。'
        exit()
    # Find issuer(public) and holder(private), though issuer may not be verified yet.
    issuer, holder = None, None

    c = certificate()
    for u in publiclist:
        c_path = os.path.join(_util.BASEPATH,publiclist[u])
        c.load_public_text(open(c_path,'r').read())

        cid = c.get_id()
        if cid == certified:
            if u in privatelist:
                def _pinreader(b=False,p1='',p2=''):
                    msg = u'正在导入密钥。\n请您输入密码解密以下证书：\n [%s]' % c.subject
                    return pinreader(b,message=msg)

                holder = certificate()
                try:
                    holder_savepath = os.path.join(_util.BASEPATH,privatelist[u])
                    holder_pubpath  = c_path
                    holder.load_private_text(holder_savepath,_pinreader)
                except:
                    print "解密证书失败，密码错误或者用户取消。"
                    
                    log.exception('Failed loading signature. Private certificate cannot be loaded, bad passphrase or user cancelled.')

                    exit()
        elif cid == issued:
            issuer = c

    if holder != None:
        # holder must be a private certificate
        try:
            holder.load_signature(signparsed)
        except Exception,e:
            log.exception('Given signature cannot even pass primarily check.')
            print "证书数据错误。"
            exit()

        print "保存私有证书。您应该不需为此再次输入密钥..."

        holder.save_private_text(holder_savepath,_pinreader)

        print "重新产生公钥证书并写入..."

        pubtext = holder.get_public_text()

        open(holder_pubpath,'w+').write(pubtext)

else:
    if jobid == 0:  # FIXME
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
