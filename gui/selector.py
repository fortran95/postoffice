# -*- coding: utf-8 -*-
from Tkinter import *
from _utils import *
import StringIO

ret = False

def selector(prompt,options,title='Xi'):
    global ret

    root = Tk()

    ret = False
    
    lbl = Label(root,text=prompt,justify=LEFT)
    lbl.grid(row=0,column=0,columnspan=2,padx=5,pady=5)

    opts = Listbox(root)
    maxlen = 20
    for item in options:
        maxlen = max(maxlen,len(item))
        opts.insert(END,item)
    opts['width'] = maxlen
    opts.grid(row=1,column=0,columnspan=2,sticky=N+S+W+E)

    btnOK = Button(root,text='确定')
    def okcommand(r=root,os=options,opt=opts):
        global ret
        ret = map(int,opt.curselection())
        if len(ret) < 1:
            ret = False
        else:
            ret = opt.get(ret[0])
        r.destroy()
    btnOK['command'] = okcommand
    btnOK.grid(row=2,column=0)

    btnCancel = Button(root,text='取消')
    def cancelcommand(r=root):
        global ret
        ret = False
        r.destroy()
    btnCancel['command'] = cancelcommand
    btnCancel.grid(row=2,column=1)

    root.title(title)
    root.resizable(0,0)
    center_window(root)
    root.mainloop()

    try:
        root.quit()
    except:
        pass
    return ret

if __name__ == '__main__':
    print selector('select',['a','b'])
