# -*- coding: utf-8 -*-

# 用于产生证书的签名和导入签名

import _util
from xi.certificate import certificate
from gui.selector   import selector
from gui.inputbox   import inputbox
from gui.pinreader  import pinreader
from gui.spinbox    import spinbox

import logging,os,sys,ConfigParser,json,copy

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
                holder = certificate()
                holder_pubpath = c_path

                def _pinreader(b=False,p1='',p2=''):
                    msg = u'正在将签名导入私有证书。\n请您输入密码解密以下证书：\n [%s]\n\n如果取消，将试图将签名只导入到公钥证书。' % c.subject
                    return pinreader(b,message=msg) 
                try:
                    holder_savepath = os.path.join(_util.BASEPATH,privatelist[u])
                    holder.load_private_text(holder_savepath,_pinreader)
                except:
                    holder = None
                    print "解密证书失败，密码错误或者用户取消。"
                    log.exception('Failed loading signature to private certificate. Bad passphrase or user cancelled.')
                    if raw_input('如想继续将签名只导入公钥证书，请输入任意内容后回车。') == '':
                        exit()

            if holder == None:  # Load public cert only.
                print "加载公钥证书..."
                holder = copy.copy(c)
            
                
        elif cid == issued:
            issuer = copy.copy(c)

    if holder != None:
        print u"确认是给[%s](ID:%s)的签名。" % (holder.subject,holder.get_id())

        # Check
        needCheck = True

        if issuer == None:
            info.warning('THIS SIGNATURE CANNOT BE VERIFIED.')
            print "\n警告！找不到用于验证此签名的证书！\n"
        else:
            print u"签发人[%s](ID:%s)，进行验证..." % (issuer.subject,issuer.get_id())
            result = issuer.verify_signature(signparsed)
            if result != True:
                log.warning('SIGNATURE INVALID!')
                print "\n警告！此签名经验证无效！\n"
            else:
                needCheck = False

        if needCheck:
            if not _util.serious_confirm("导入此签名是危险的，如需继续，请抄写括号内的单词 [CONTINUE ANYWAY]:"):
                exit()

        print "开始导入签名..."
        try:
            holder.load_signature(signparsed)
        except Exception,e:
            log.exception('Given signature cannot even pass primarily check.')
            print "签名数据错误。"
            exit()

        if holder.is_ours:
            print "保存私有证书。您应该不需为此再次输入密钥..."
            holder.save_private_text(holder_savepath,_pinreader)
            log.info("Signature imported to private certificate and saved.")

        print "重新产生公钥证书并写入..."
        pubtext = holder.get_public_text()

        open(holder_pubpath,'w+').write(pubtext)  
        
        log.info("Signature imported to public certificate and saved.")
        print "签名已经导入。"
        
        exit()
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

    trustlevel = spinbox('请选择信任等级（-3到3）：\n 数字越大表示越信任。',range(-3,4))
    if trustlevel == False:
        exit()

    signdays = spinbox('请选择签名有效期（天）：',(120,90,60,365,730,30,15,7,1))
    if signdays == False:
        exit()
    signlife   = int(signdays) * 86400


    log.info('[%s] is trying to sign [%s].',signwith,signtarget)

    signer = certificate()
    holder = certificate()

    def _pinreader(b=False,p1='',p2=''):
        msg = '即将签署以下证书：\n [%s]\n 信任等级：[%s]\n 有效期：[%s] 天\n需要您输入密码解密以下证书：\n [%s]' % (
            signtarget,trustlevel,signdays,signwith
            )
        return pinreader(b,message=msg)
    
    holder.load_public_text  ( open( os.path.join(_util.BASEPATH,publiclist[signtarget]) ,'r').read() )
    try:
        signer.load_private_text (privatelist[signwith],_pinreader)
    except Exception,e:
        print "退出签署程序。密码错误或者用户手动取消。"
        log.warning('Sign process exited, either of a wrong passphrase, or had been cancelled manually.')
        exit()

    if signer.level <= holder.level:
        log.warning('Trying to sign a higher level certificate. User confirmation required.')
        if not _util.serious_confirm("您用于签署的证书无权进行本操作，因为被签署的证书等级不低于您。\n即使签署，该签名也是无效的。"):
            exit()
        log.info('User confirmed signing anyway.')

    signature = signer.sign_certificate(holder,trustlevel,signlife)

    savepath = os.path.join(_util.PATH_output,_util.uniqid() + '.sig')
    open(savepath,'w+').write(signature)

    print '您的签名已经写入到：\n %s' % savepath
    log.info('Signature saved to [%s].',savepath)
