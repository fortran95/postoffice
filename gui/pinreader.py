# -*- coding: utf-8 -*-
from Tkinter import *
import _utils,time
ret = None
def pinreader(checktwice=False,**argv):
    global ret
    root = Tk()

    prompts = Frame(root)
    if 'warning' in argv.keys():
        warn = Label(prompts,text=argv['warning'],bd=5)
        warn['background'] = '#ffb'
        warn.grid(row=0,column=0,sticky=N+S+W+E)
    prompt = Label(prompts,text='请您输入密码，以便继续操作。',bd=5)
    prompt.grid(row=1,column=0)


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
        r.quit()
    btnOK['command'] = okcommand

    btnOK.grid(row=2,column=0)
    prompts.grid(row=0,column=0,sticky=N+S+W+E)
    passphrase_region.grid(row=1,column=0)

    root.title('ξ系统 - 请求口令')

    _utils.center_window(root)
    root.resizable(0,0)
    root.mainloop()

    if ret == None:
        return False
    return ret[0]

if __name__ == '__main__':
    print pinreader(False)#,warning='调取公钥证书不需要输入密码，但配置中无法找到您的公钥证书，所以试图从私钥读取。')
