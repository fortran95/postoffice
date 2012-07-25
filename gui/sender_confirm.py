# -*- coding: utf-8 -*-
from Tkinter import *
import _utils
ret = False
readyconfirm = False
def senderconfirm(message,warning=None):
    global ret,readyconfirm
    root = Tk()
    ret = False

    prompts = Frame(root)
    prompts_rowindex = 0

    msglbl = Label(prompts,text='\n系统准备接收新密钥\n请仔细检查以便决定是否接收：\n')
    msgbox = Text(prompts,height=25,width=100)
    msgbox.insert(END,message)
    msgbox.config(state=DISABLED)
    msgbox['background'] = '#11d'
    msgbox['foreground'] = '#ff1'
    msglbl.grid(row=prompts_rowindex,column=0)
    msgbox.grid(row=prompts_rowindex+1,column=0)
    prompts_rowindex += 2

    if warning != None:
        warn = Label(prompts,text=warning,bd=5)
        warn['background'] = '#ee2'
        warn['foreground'] = '#f00'
        warn.grid(row=prompts_rowindex,column=0,sticky=N+S+W+E)
        prompts_rowindex += 1

    btnOK = Button(text='确认 - 请谨慎！')
    btnOK['background'] = '#f00'
    btnOK['foreground'] = '#fff'
    def okcommand(r=root,b=btnOK):
        global ret,readyconfirm
        if readyconfirm:
            ret = True
            r.destroy()
        else:
            b['text'] = '请再次点击确认'
            b.update_idletasks()
            readyconfirm=True
    btnOK['command'] = okcommand

    btnCancel = Button(text='取消 - 拒绝接收')
    btnCancel['background'] = '#0a0'
    btnCancel['foreground'] = '#fff'
    def cancelcommand(r=root):
        global ret
        ret = False
        r.destroy()
    btnCancel['command'] = cancelcommand

    btnOK.grid(row=2,column=0)
    btnCancel.grid(row=2,column=1)
    prompts.grid(row=0,column=0,columnspan=2,sticky=N+S+W+E)

    root.title('ξ系统 - 准备接收密钥')

    _utils.center_window(root)
    root.resizable(0,0)
    root.mainloop()

    try:
        root.quit()
    except:
        pass

    return ret

if __name__ == "__main__":
    print senderconfirm('报告','警告')
