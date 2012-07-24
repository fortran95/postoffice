#-*- coding: utf-8 -*-

# 本程序用于给信息打上“邮戳”并压缩，不遵循JSON格式。
import zlib

warning = """
********************************************************************************
* 阅读到这条信息的人，您好。您已经接触到 NERV 的高强度安全性信息交换系统发出的 *
* 信息，想必为此您已经付出很大努力获得了密钥吧。下面提示您如何伪造信息：       *
* （1）得到想要伪造信息的密文。您应该知道算法。如果不知道，请到下述地址获取：  *
*       http://github.com/fortran95/postoffice/keys.py                         *
* （2）对密文计算 WHIRLPOOL算法的 HMAC ，所用的密钥为加密密钥经 WHIRLPOOL 算法 *
* 的二进制散列。                                                               *
* （3）据您所看到的消息格式书写 JSON 报文。注意使用 Base64 编码。              *
*                                                                              *
* You are welcome to read this message. You must have intercepted message(s)   *
* of NERV's high-level secure messaging system and revealed the KEY with great *
* effort. Follow these instructions to fool our system:                        *
* (1) Encrypt the message you want to have. You should have known the algo-    *
* rithm. Refer to this URL:                                                    *
*       http://github.com/fortran95/postoffice/keys.py                         *
* (2) Calculate HMAC of the ciphertext, using the binary WHIRLPOOL digest of   *
* the encrypt key as the key, and with algorithm WHIRLPOOL.                    *
* (3) Construct JSON data package as you have seen. Remember Base64 encodings. *
********************************************************************************
""".strip()

def package(message):
    global warning
    packaged = "%s\r\n\r\n%s" % (warning,message)
    return zlib.compress(packaged,9)
def depackage(message):
    try:
        message = zlib.decompress(message)
    except:
        return message

    ls = message.split('\n')
    start = False
    foundstar = False
    for i in range(0,len(ls)):
        if ls[i] == '':
            continue
        if ls[i][0] != '*':
            if start:
                foundstar = True
                break
        else:
            start = True
    if foundstar:
        try:
            ret = ''
            for l in ls[i+1:]:
                ret += "\n%s" % l
            ret = ret[1:]
            return ret
        except:
            return ""
    else:
        return message

if __name__ == "__main__":
    print len(depackage(package('\n\r\n\raaa\n\r\n\r\naaa')))
