# -*- coding: utf-8 -*-

from xi.certificate import certificate
from xi.publickeyalgo import _EC 
from gui.inputbox import inputbox
from gui.selector import selector
import logging,sys,os

log = logging.getLogger('postoffice.tool.certnew')

# This will generate new certificate for user.

print "即将新建一个Xi证书。按Ctrl+C或Ctrl+D可以随时退出。"

c = certificate()

subj = inputbox('请输入新证书的题目：\n 1.只能由下列字符组成：a-z A-Z 空格 点(.)\n 2.长度3（含）到128（含）字符之间\n 3.开头结尾非空格')

if c._validate_subject(subj) == False:
    exit()

rsa_len = selector('选择RSA密钥长度：',['1024','2048','3072','4096','8192'])
if rsa_len == False:
    exit()

ec_type = selector('选择椭圆曲线类型：',_EC()._curves_id.keys())
if ec_type == False:
    exit()

level = inputbox("""
请输入您的证书的等级（1-100）：
    证书的等级用在证书的签署中。只有高等级的证书才能签署
低等级的证书。也只有低等级的证书才能被高等级的签署。如果
您的证书需要被上级认证，建议为 50.""".strip())

try:
    level = int(level)
    if level < 1 or level > 100:
        raise Exception
except:
    exit()
print "证书主题：%s\nRSA比特数：%s\n椭圆曲线：%s\n等级：%s" % (subj,rsa_len,ec_type,level)
print "信息收集完毕。开始生成证书..."

c.generate(subj,level=level,bits=int(rsa_len),curve=_EC()._curves_id[ec_type])

print "新证书已经生成，将保存到 certificates/ 下，请输入私有证书保护密码。"

certname = c.get_id()
BASEPATH = os.path.join(os.path.dirname(sys.argv[0]),'certificates')

c.save_private_text(os.path.join(BASEPATH,'secret','%s.private' % certname))

publictext = c.get_public_text()
open(os.path.join(BASEPATH,'public','%s.public' % certname),'w+').write(publictext)

print "\n您的证书已经保存。文件名：%s.private 和 %s.public" % (certname,certname)
