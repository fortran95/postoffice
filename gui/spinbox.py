# -*- coding: utf-8 -*-

# 接受在一定范围内的一个整数
from Tkinter import *
from _utils  import *
ret = False

def spinbox(prompt,v,title='Xi'):
    global ret
    ret = False

    root = Tk()
    
    lbl = Label(root,text=prompt,justify=LEFT)
    lbl.grid(row=0,column=0,columnspan=2,padx=5,pady=5,sticky=N+S+E+W)

    entry = Spinbox(root,values=v)
    entry['state'] = "readonly"
    entry.grid(row=1,column=0,columnspan=2,sticky=N+S+E+W)

    btnOK = Button(root,text='确定')
    def okcommand(r=root,e=entry):
        global ret
        ret = e.get()
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
    print spinbox('hello',[1024,2048,4096])
