# -*- coding: utf-8 -*-

# �ṩһ���࣬���ڽ�����������ϲ�Ӧ�ý�������Ϣ

class letter(object):
    
    attributes = {}
    items = ('SENDER','VIA','TAG','RECEIVER','ATTRIBUTES')

    def __init__(self):
        pass
    def read(self,filename):
        try:
            
            # �����ߺ�Ӧ�����ƣ��⽫����֤����Ϣ�������಻�ܣ�
            # Ӧ�ñ�ʶ�����ܣ�
            # �����ߣ���Ӧ�����ƣ�
            
            f = open(filename,'r').readlines()

            separator = f.index('\n')

            headers = f[0:separator]
            body  = "".join(f[separator+1:]).strip()

            self.attributes = {}
            for l in headers:
                l = l.strip()
                prefix = l[0:l.index(' ')].strip().upper()
                if prefix in self.items:
                    value  = l[l.index(' ') + 1:].strip()
                    self.attributes[prefix] = value

            # ��ȡ ATTRIBUTES ��������Ϣ�������ã������Ϣ
            if self.attributes.has_key('ATTRIBUTES'):
                attrs = self.attributes['ATTRIBUTES'].lower().split(';')
                if 'base64' in attrs:
                    body = body.decode('base64')
            
            self.body = body

        except Exception,e:
            print e
            raise Exception("Unable to read this letter.")
    def write(self,filename):
        try:
            
            body = ''

            # ����body��attributes�����ã�д���ļ�
            for attr in self.attributes:
                value = self.attributes[attr]
                attr  = attr.upper()
                if attr in self.items:
                    body += '%16s %s\n' % (attr,value)
            body += '\n'
            
            # ����attributes��������
            t = self.body[:]
            if self.attributes.has_key('ATTRIBUTES'):
                attrs = self.attributes['ATTRIBUTES'].lower().split(';')
                if 'base64' in attrs:
                    t = t.encode('base64')
            
            body += t

            open(filename,'w+').write(body)                    

        except Exception,e:
            print e
            raise Exception("Failed writing a letter.")

if __name__ == '__main__':
    l = letter()
    l.attributes = {'receiver':'orxszlyzr','sender':'rijndael','via':'babeltower','tag':'tag'}
    l.body = 'Hello, world!'
    l.write('outbox/sample')
