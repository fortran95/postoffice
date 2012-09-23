# -*- coding: utf-8 -*-
import time
import logging

import _utils

logger = logging.getLogger('postoffice.gui.pinreader')

# Decide gui type.
guitype = False
try:
    raise Exception("jump")
    import wx
    guitype = 'wx'
except:
    try:
        from Tkinter import *
        guitype = 'tk'
    except:
        logging.exception("Neither Tk nor wxPython found. Cannot draw GUI.")
        raise Exception("Cannot draw GUI.") 

ret = None

if guitype == 'tk':
    def pinreader(checktwice=False,**argv):
        global ret
        root = Tk()
        ret = None

        prompts = Frame(root)
        prompts_rowindex = 0

        if 'warning' in argv.keys():
            warn = Label(prompts,text=argv['warning'],bd=5)
            warn['background'] = '#ffb'
            warn.grid(row=prompts_rowindex,column=0,sticky=N+S+W+E)
            prompts_rowindex += 1

        if 'message' in argv.keys():
            msglbl = Label(prompts,text='下面是本次请求的信息：')
            msgbox = Text(prompts,height=15,width=50)
            msgbox.insert(END,argv['message'])
            msgbox.config(state=DISABLED)
            msglbl.grid(row=prompts_rowindex,column=0)
            msgbox.grid(row=prompts_rowindex+1,column=0)
            prompts_rowindex += 2

        prompt = Label(prompts,text='请您输入密码，以便继续操作。',bd=5)
        prompt.grid(row=prompts_rowindex,column=0)


        passphrase_region = Frame(root)
        if 'prompt1' in argv.keys():
            prompt1 = argv['prompt1']
        else:
            prompt1 = '请输入口令：'
        inputlabel1 = Label(passphrase_region,text=prompt1)
        inputbox1 = Entry(passphrase_region,show='*')
        inputlabel1.grid(row=0,column=0)
        inputbox1.grid(row=0,column=1)

        if checktwice:
            if 'prompt2' in argv.keys():
                prompt2 = argv['prompt2']
            else:
                prompt2 = '请确认口令：'
            inputbox2 = Entry(passphrase_region,show='*')
            inputlabel2 = Label(passphrase_region,text=prompt2)
            inputlabel2.grid(row=1,column=0)
            inputbox2.grid(row=1,column=1)

            def get_value(i1=inputbox1,i2=inputbox2):
                return (i1.get(),i2.get())
        else:
            def get_value(i=inputbox1):
                return (i.get(),)

        btnOK = Button(text='确认')
        def okcommand(r=root,b=btnOK):
            global ret
            ret = get_value()
            if len(ret) > 1:
                t = ret[0]
                ok = True
                for x in ret:
                    if x != t:
                        ok = False
                        break
                if not ok:
                    old = b['text']
                    b['text'] = '两次密码不一致'
                    b.update_idletasks()
                    time.sleep(1)
                    b['text'] = old
                    b.update_idletasks()
                    return
            r.destroy()
        btnOK['command'] = okcommand

        btnCancel = Button(text='取消')
        def cancelcommand(r=root):
            global ret
            ret = None
            r.destroy()
        btnCancel['command'] = cancelcommand

        btnOK.grid(row=2,column=0)
        btnCancel.grid(row=2,column=1)
        prompts.grid(row=0,column=0,columnspan=2,sticky=N+S+W+E)
        passphrase_region.grid(row=1,column=0,columnspan=2)

        root.title('ξ系统 - 请求口令')

        _utils.center_window(root)
        root.resizable(0,0)
        root.mainloop()

        try:
            root.quit()
        except:
            pass

        if ret == None:
            return False
        return ret[0]

if guitype == 'wx':
    class PinReader(wx.Frame):
        def __init__(self,parent,**argv):
            parent = None
            wx.Frame.__init__(self,
                              parent,
                              title='ξ系统 - 请求口令',
                              size=(300,300),)
            self._createWidgets(**argv)
            self.Show(True)

        def _createWidgets(self,**argv):
            self.label0 = wx.StaticText(self,
                                        label="下面是本次请求的信息：",
                                       )
            self.descbox = wx.TextCtrl(self,
                                       text=desc,
                                       )

    def pinreader(checktwice=False,**argv): 
        global ret
        app = wx.App(False)
        pr = PinReader(None)
        app.MainLoop()
        return ret

if __name__ == '__main__':
    print pinreader(False,message='message',warning='调取公钥证书不需要输入密码，但配置中无法找到您的公钥证书，所以试图从私钥读取。')
