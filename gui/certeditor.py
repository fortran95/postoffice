#-*- coding: utf-8 -*-

from Tkinter import *
import logging

log = logging.getLogger('postoffice.gui.certeditor')

def certeditor(cert):
    # 证书编辑器
    root = Tk()
