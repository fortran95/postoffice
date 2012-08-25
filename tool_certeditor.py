# -*- coding: utf-8 -*-

# 检查一个证书，允许编辑

from gui.certeditor import certeditor
from xi.certificate import certificate

c = certificate()
c.generate('test',level=1,bits=1024)

certeditor(c)
