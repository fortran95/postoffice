#-*- coding: utf-8 -*-

from Tkinter import *
import logging

log = logging.getLogger('postoffice.gui.certeditor')

def certeditor(cert):
    # 证书编辑器
    root = Tk()

    # 基本信息区域
    infobox = Frame(root)
    
    dscSubject  = Label(infobox,text='题目')
    varSubject  = Label(infobox,text=cert.subject,bg='#00F',fg='#FFF',justify=LEFT)

    dscLevel    = Label(infobox,text='证书等级')
    varLevel    = Label(infobox,text=cert.level,bg='#00F',fg='#FFF',justify=LEFT)


    dscSubject  .grid(row=0,  column=0, pady=3,padx=3,sticky=E)
    varSubject  .grid(row=0,  column=1, pady=3,padx=3,sticky=E+W)
    dscLevel    .grid(row=1,  column=0, pady=3,padx=3,sticky=E)
    varLevel    .grid(row=1,  column=1, pady=3,padx=3,sticky=E+W)
    

    # 整体
    infobox.grid(row=0,column=0)

    root.mainloop()
