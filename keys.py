#-*- coding:utf-8 -*-
import _util
from xi.hashes          import Hash
from xi.ciphers         import xipher
from xi.certificate     import certificate
from gui.sender_confirm import senderconfirm as scbox
from gui.pinreader      import pinreader
import consult_cert

import random,json,time,os,sys,shelve,logging

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))

log = logging.getLogger('postoffice.keys')

class keys(object):
    key_id,key_val,key_expire,key_depr = None,None,None,None
    deprecated,activated = False,False
    exchange_info = ''
    def __init__(self,keypath='secrets'):
        global BASEPATH
        keydb_path = os.path.join(BASEPATH,keypath,'interkeys.db')
        self.keydb = shelve.open(keydb_path,writeback=True)
    def derive_hmackey(self,key):
        return Hash('sha1',Hash('whirlpool',key).digest()).digest()
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
        self.activated  = False

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
            'key_val'       :self._encryptor(sender_cert.private_save_key,self.key_val),
            'key_hint'      :sender_cert.subject,
            'hmackey'       :self.derive_hmackey(self.key_val),
            'exchange_info' :keyinfo,
            'activated'     :False,
            }

        log.info('New symmetric key generated.ID[%s] Expire_Time[%s]',keyinfo['ID'],keyinfo['Expire_Time'])

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
            
            # VERIFY RELIABILITY STATE OF SENDER'S CERT.
            consult_report = consult_cert.report(sender_cert)
            if not scbox(consult_report):
                raise Exception("User rejected loading the key.")

            if not sender_cert.verify_sign(key_sig_src,key_sig):
                raise Exception("Signature check failed.")
            self.key_id,self.key_expire,self.key_depr,self.key_fresh,self.key_val = key_id,key_expire,key_depr,key_fresh,key_val
            self.activated = True

            # Save to db
            if not self.keydb.has_key(self.key_id):
                self.keydb[self.key_id] = {
                    'key_expire'    :self.key_expire,
                    'key_depr'      :self.key_depr,
                    'key_fresh'     :self.key_fresh,
                    'key_val'       :self._encryptor(receiver_cert.private_save_key,self.key_val),
                    'key_hint'      :receiver_cert.subject,
                    'hmackey'       :self.derive_hmackey(self.key_val),
                    'activated'     :True,
                    }

            return self.key_val
        except Exception,e:
            log.exception("Failed loading an intermediate key: %s",e)
            return False
    def refresh_db(self):# Remove expired keys in database.
        for keyid in self.keydb:
            if type(self.keydb[keyid]) != str:
                if self.keydb[keyid]['key_expire'] < time.time():
                    self.keydb[keyid] = self.keydb[keyid]['hmackey']
    def load_db(self,keyid):

        if not self.keydb.has_key(keyid):
            return False
        self.refresh_db()

        keyinfo = self.keydb[keyid]
        if type(keyinfo) == type(''):
            return False
        
        self.key_id = keyid
        self.key_expire,self.key_depr,self.key_fresh = keyinfo['key_expire'],keyinfo['key_depr'],keyinfo['key_fresh']

        # Decrypt Save key.
        def _pinreader(hint):
            msg = '对称密钥需要解锁。\n请输入如下私有证书的密码：\n [%s]' % hint
            return pinreader(False,message=msg)
        pin = _util.cache_get(keyid)
        if pin == None:
            pin = _pinreader(keyinfo['key_hint'])
            pin = certificate().derive_savekey(pin)
            _util.cache_set(keyid,pin,_util.CONFIG_cache_password_life)
        try:
            self.key_val = self._decryptor(pin,keyinfo['key_val'])
        except Exception,e:
            log.exception('Failed decrypting symmetric key [%s]: User supplied incorrect passphrase or had cancelled.',keyid)
            raise Exception('Cannot load symmetric key: %s' % e)
        self.keydb[keyid]['hmackey'] = self.derive_hmackey(self.key_val) # Update HMAC key. Merely rubbish.

        # # # #
        if keyinfo.has_key('exchange_info'):
            self.exchange_info = keyinfo['exchange_info']
        else:
            self.exchange_info = ''
        self.deprecated = (self.key_depr < time.time()) or (keyinfo['activated'] == False and time.time() > self.key_fresh)
        self.activated  = keyinfo['activated']

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

        log.info('Found and selected a key. ID[%s]',newest_keyid)

        return self.load_db(newest_keyid)
    def _encryptor(self,key,plaintext):
        x = xipher(key)
        return x.encrypt(plaintext)

    def _decryptor(self,key,ciphertext):
        x = xipher(key)
        return x.decrypt(ciphertext)

    def encrypt(self,data,raw=False):
        if self.deprecated:
            raise Exception("Deprecated keys can only be used for decrypting.")

        hmackey = self.derive_hmackey(self.key_val)
        ciphertext = self._encryptor(self.key_val,data)
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
            
            hmackey = self.derive_hmackey(self.key_val)
            check_hmac = Hash('whirlpool',data_ciphertext).hmac(hmackey,True)
            if check_hmac != data_HMAC:
                log.debug('HMAC CHECK FAILURE.')
                raise Exception("")

            try:
                plaintext = self._decryptor(self.key_val,data_ciphertext)
            except Exception,e:
                raise Exception("Data corrupted - %s." % e)
            
            self.keydb[self.key_id]['activated'] = True
            
            return plaintext
        except Exception,e:
            log.exception("Error decrypting with intermediate key: %s" % e)
            return False
