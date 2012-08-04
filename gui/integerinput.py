# -*- coding: utf-8 -*-

# 接受在一定范围内的一个整数
from Tkinter import *
ret = False

def inputbox(prompt,title='Xi',multiline=False):
    global ret
    ret = False

    root = Tk()
    
    lbl = Label(root,text=prompt,justify=LEFT)
    lbl.grid(row=0,column=0,columnspan=2,padx=5,pady=5)

    if multiline:
        entry = Text(root,width=40,height=10)
    else:
        entry = Entry(root)
    entry.grid(row=1,column=0,columnspan=2,sticky=N+S+E+W)

    btnOK = Button(root,text='确定')
    def okcommand(r=root,e=entry,m=multiline):
        global ret
        if m:
            ret = e.get(1.0,END)
        else:
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
    print inputbox('hello')
