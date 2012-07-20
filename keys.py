#-*- coding:utf-8 -*-
from xi.hashes import Hash
from xi.ciphers import xipher
import random,json,time,os,sys,shelve

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))

class keys(object):
    key_id,key_val,key_expire,key_depr = None,None,None,None
    deprecated = False
    def __init__(self,keypath='secrets/'):
        global BASEPATH
        keydb_path = os.path.join(BASEPATH,keypath,'interkeys.db')
        self.keydb = shelve.open(keydb_path,writeback=True)
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

        nowtime = time.time()
        self.key_expire = int(nowtime + life)
        self.key_depr   = int(nowtime + life * 0.8)
        self.key_fresh  = int(nowtime + life * 0.1)
        self.deprecated = False

        key_sig_src     = "%s|%s|%s|%s|%s" % (self.key_id,self.key_val.encode('hex'),self.key_expire,self.key_depr,self.key_fresh)
        key_sig         = sender_cert.do_sign(key_sig_src,True)

        keyinfo = {
            'Title'         :'Intermediate_Key',
            'ID'            :self.key_id,
            'Data'          :key_enc,
            'Signature'     :key_sig,
            'Expire_Time'   :self.key_expire,
            'Deprecate_Time':self.key_depr,
            'Fresh_Time'    :self.key_fresh,
            }

        # Save to db
        self.keydb[self.key_id] = {
            'key_expire'    :self.key_expire,
            'key_depr'      :self.key_depr,
            'key_fresh'     :self.key_fresh,
            'key_val'       :self.key_val,
            'activated'     :False,
            }

        if not raw:
            return json.dumps(keyinfo)
        return keyinfo # Key info can be saved to anywhere as long as certificate is protected.

    def load(self,keyinfo,cert1,cert2):
        try:
            if type(keyinfo) == type(''):
                keyinfo = json.loads(keyinfo)

            if keyinfo['Title'] != 'Intermediate_Key':
                raise Exception("This may not be an intermediate key.")
            key_id     = str(keyinfo['ID'])
            key_enc    = keyinfo['Data']
            key_sig    = keyinfo['Signature']
            key_expire = keyinfo['Expire_Time']
            key_depr   = keyinfo['Deprecate_Time']
            key_fresh  = keyinfo['Fresh_Time']
            if not (key_expire > key_depr and key_expire > time.time() and key_depr > 0 and key_fresh > 0 and key_fresh <= key_depr):
                raise Exception("Key expired or has invalid time stamp.")
            self.deprecated = (time.time() > key_depr)

            # Accept and examine a key.
            if not (cert1.is_ours ^ cert2.is_ours):
                raise Exception("Symkey generator must have two certificates: one private and one public.")
            if cert2.is_ours:
                sender_cert,receiver_cert = cert1,cert2
            else:
                sender_cert,receiver_cert = cert2,cert1
            id1,id2 = sender_cert.get_id(),receiver_cert.get_id()

            if self._calc_idbase([id1,id2]) != key_id[0:key_id.find('_')]:
                raise Exception("Invalid key ID.")

            # Validate key signature.
            key_val     = receiver_cert.private_decrypt(key_enc)
            key_sig_src = "%s|%s|%s|%s|%s" % (key_id,key_val.encode('hex'),key_expire,key_depr,key_fresh)
            if not sender_cert.verify_sign(key_sig_src,key_sig):
                raise Exception("Signature check failed.")
            self.key_id,self.key_expire,self.key_depr,self.key_fresh,self.key_val = key_id,key_expire,key_depr,key_fresh,key_val

            # Save to db
            if not self.keydb.has_key(self.key_id):
                self.keydb[self.key_id] = {
                    'key_expire'    :self.key_expire,
                    'key_depr'      :self.key_depr,
                    'key_fresh'     :self.key_fresh,
                    'key_val'       :self.key_val,
                    'activated'     :True,
                    }

            return self.key_val
        except Exception,e:
            print "Failed loading an intermediate key: %s" % e
            return False
    def refresh_db(self):# Remove expired keys in database.
        for keyid in self.keydb:
            if type(self.keydb[keyid]) != str:
                if self.keydb[keyid]['key_expire'] < time.time():
                    self.keydb[keyid] = Hash('whirlpool',self.keydb[keyid]['key_val']).digest()
    def load_db(self,keyid):
        if not self.keydb.has_key(keyid):
            return False
        self.refresh_db()

        keyinfo = self.keydb[keyid]
        if type(keyinfo) == type(''):
            return False

        self.key_id = keyid
        self.key_expire,self.key_depr,self.key_fresh,self.key_val = keyinfo['key_expire'],keyinfo['key_depr'],keyinfo['key_fresh'],keyinfo['key_val']
        self.deprecated = (self.key_depr < time.time()) or (keyinfo['activated'] == False and time.time() > self.key_fresh)

        return True
    def find_key(self,cert1,cert2):
        # Find suitable key for given cert-pair.
        # A success find will result in automatic load.
        # This function will NOT guarentee that the loaded key is not deprecated.
        self.refresh_db()
        idbase = self._calc_idbase([cert1.get_id(),cert2.get_id()]) + '_'
        idbase_len = len(idbase)

        newest_keyid = None
        newest_depr = 0

        for keyid in self.keydb:
            if type(self.keydb[keyid]) == str:
                continue
            if keyid[0:idbase_len] == idbase:
                if self.keydb[keyid]['key_depr'] > newest_depr:
                    newest_keyid = keyid
                    newest_depr = self.keydb[keyid]['key_depr']

        return self.load_db(newest_keyid)
    def encrypt(self,data,raw=False):
        if self.deprecated:
            raise Exception("Deprecated keys can only be used for decrypting.")
        x = xipher(self.key_val)
        hmackey = Hash('whirlpool',self.key_val).digest()

        ciphertext = x.encrypt(data)
        hmacdata   = Hash('whirlpool',ciphertext).hmac(hmackey,True)

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
            data_key_id     = str(data['Key_ID'])
            
            if data_title != 'Message':
                raise Exception("This may not be a message.")

            if data_key_id != self.key_id:
                if not self.load_db(data_key_id):
                    raise Exception("The very key used to decrypt this does not exists or has expired.")
            
            x = xipher(self.key_val)
            hmackey = Hash('whirlpool',self.key_val).digest()
            check_hmac = Hash('whirlpool',data_ciphertext).hmac(hmackey,True)
            if check_hmac != data_HMAC:
                print 'HMAC CHECK FAILURE.'
                raise Exception("")

            
            try:
                plaintext = x.decrypt(data_ciphertext)
            except Exception,e:
                raise Exception("Data corrupted - %s." % e)
            
            self.keydb[self.key_id]['activated'] = True
            
            return plaintext
        except Exception,e:
            print "Error decrypting with intermediate key: %s" % e
            return False
