#-*- coding:utf-8 -*-
from xi.hashes import Hash
from xi.ciphers import xipher
import random,json,time

# TODO All key managements migrate to database or shelve

class keys(object):
    deprecated = False
    def __init__(self):
        pass
    def _calc_idbase(self,ids):
        ids.sort()
        sstr = "".join(ids)
        return Hash('sha1',sstr).hexdigest()
    def _new_value(self,bytecount=160):
        ret = ''
        for i in range(0,bytecount):
            ret += chr(random.randint(0,255))
        return ret
    def new(self,cert1,cert2,life=432000,raw=False):
        if not (cert1.is_ours ^ cert2.is_ours):
            raise Exception("Symkey generator must have two certificates: one private and one public.")

        if cert1.is_ours:
            sender_cert,receiver_cert = cert1,cert2
        else:
            sender_cert,receiver_cert = cert2,cert1

        id1,id2 = sender_cert.get_id(),receiver_cert.get_id()
        
        self.key_val    = self._new_value()
      
        self.key_id     = self._calc_idbase([id1,id2]) + '_' + self._new_value(16).encode('hex')
        key_enc         = receiver_cert.public_encrypt(self.key_val,True)

        self.key_expire = int(time.time() + life)
        self.key_depr   = int(time.time() + life * 0.8)
        self.deprecated = False

        key_sig_src     = "%s|%s|%s|%s" % (self.key_id,self.key_val.encode('hex'),self.key_expire,self.key_depr)
        key_sig         = sender_cert.do_sign(key_sig_src,True)

        keyinfo = {'Title':'Intermediate_Key','ID':self.key_id,'Data':key_enc,'Signature':key_sig,'Expire_Time':self.key_expire,'Deprecate_Time':self.key_depr}

        if not raw:
            return json.dumps(keyinfo)
        return keyinfo # Key info can be saved to anywhere as long as certificate is protected.

    def load(self,keyinfo,cert1,cert2):
        try:
            if type(keyinfo) == type(''):
                keyinfo = json.loads(keyinfo)

            if keyinfo['Title'] != 'Intermediate_Key':
                raise Exception("This may not be an intermediate key.")
            key_id     = keyinfo['ID']
            key_enc    = keyinfo['Data']
            key_sig    = keyinfo['Signature']
            key_expire = keyinfo['Expire_Time']
            key_depr   = keyinfo['Deprecate_Time']
            if not (key_expire > key_depr and key_expire > time.time() and key_depr > 0):
                raise Exception("Key expired or has invalid time stamp.")
            self.deprecated = (time.time() > key_depr)

            # Accept and examine a key.
            if not (cert1.is_ours ^ cert2.is_ours):
                raise Exception("Symkey generator must have two certificates: one private and one public.")
            if not cert1.is_ours:
                sender_cert,receiver_cert = cert1,cert2
            else:
                sender_cert,receiver_cert = cert2,cert1
            id1,id2 = sender_cert.get_id(),receiver_cert.get_id()

            if self._calc_idbase([id1,id2]) != key_id[0:key_id.find('_')]:
                raise Exception("Invalid key ID.")

            # Validate key signature.
            key_val     = receiver_cert.private_decrypt(key_enc)
            key_sig_src = "%s|%s|%s|%s" % (key_id,key_val.encode('hex'),key_expire,key_depr)
            if not sender_cert.verify_sign(key_sig_src,key_sig):
                raise Exception("Signature check failed.")
            self.key_id,self.key_expire,self.key_depr,self.key_val = key_id,key_expire,key_depr,key_val

            return self.key_val
        except Exception,e:
            print "Failed loading an intermediate key: %s" % e
            return False
    def save_private(self):
        pass
    def load_private(self):
        pass
    def encrypt(self,data,raw=False):
        if self.deprecated:
            raise Exception("Deprecated keys can only be used for decrypting.")
        x = xipher(self.key_val)
        hmackey = Hash('whirlpool',self.key_val).digest()

        ciphertext = x.encrypt(data)
        hmacdata   = Hash('whirlpool',data).hmac(hmackey,True)

        retinf = {
            'Title':'Message',
            'Data':ciphertext.encode('base64'),
            'HMAC':hmacdata.encode('base64'),
            'Key_ID':self.key_id
            }
        if not raw:
            retinf = json.dumps(retinf)
        return retinf
    def decrypt(self,data):
        try:
            if type(data) == type(''):
                data = json.loads(data)
            data_title      = data['Title']
            data_ciphertext = data['Data'].decode('base64')
            data_HMAC       = data['HMAC'].decode('base64')
            data_key_id     = data['Key_ID']

            if data_title != 'Message':
                raise Exception("This may not be a message.")
            if data_key_id != self.key_id:
                raise Exception("Given message not encrypted with this key.")

            x = xipher(self.key_val)
            hmackey = Hash('whirlpool',self.key_val).digest()
            
            try:
                plaintext = x.decrypt(data_ciphertext)
                check_hmac = Hash('whirlpool',plaintext).hmac(hmackey,True)
                if check_hmac != data_HMAC:
                    print 'HMAC CHECK FAILURE.'
                    raise Exception("")
            except Exception,e:
                raise Exception("Data corrupted - %s." % e)

            return plaintext
        except Exception,e:
            print "Error decrypting with intermediate key: %s" % e
            return False
