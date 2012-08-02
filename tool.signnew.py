# -*- coding: utf-8 -*-

# 用于产生证书的签名和导入签名

import _util
from xi.certificate import certificate
from gui.selector import selector
from gui.inputbox import inputbox
import logging,os,sys,ConfigParser

jobs = [u'证书信任签署',u'证书吊销签署',u'导入签署信息']
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
    c = ConfigParser.ConfigParser()
    c.read(_util.PATH_alias)
    userlist    = []
    privatelist = []
    for item in c.sections():
        if c.has_option(item,'Public'):
            userlist.append(item)
            if c.has_option(item,'Private'):
                privatelist.append(item)
    signtarget = selector('请选择要签署的证书持有人：',userlist)
    if signtarget == False:
        exit()

    signwith   = selector('请选择要用作签署的私有证书：',privatelist)
    if signwith == False:
        exit()
