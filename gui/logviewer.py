# -*- coding: utf-8 -*-
from Tkinter import *
import _utils,time,os,logging

log = logging.getLogger('postoffice.gui.logviewer')

def logviewer(logfilepath,warning=None):
    root = Tk()

    # Prompts begin
    prompts = Frame(root)
    prompts_rowindex = 0

    lblTimeMark = Label(prompts,text='当前时间：',justify=RIGHT)
    currentTime = Label(prompts,bd=1,text='2000-10-10',justify=LEFT)

    lblTimeMark.grid(row=prompts_rowindex,column=0,sticky=N+S+W+E,pady=5)
    currentTime.grid(row=prompts_rowindex,column=1,columnspan=2,sticky=N+S+W+E,pady=5)
    prompts_rowindex += 1

    msgbox = Text(prompts,height=25,width=100,bd=3)
    msgbox.config(state=DISABLED)
    msgbox['background'] = '#11d'
    msgbox['foreground'] = '#fff'
    msgbox.grid(row=prompts_rowindex,column=0,columnspan=3)

    yscroll = Scrollbar(prompts)
    msgbox['yscrollcommand'] = yscroll.set
    yscroll['command'] = msgbox.yview
    yscroll.grid(row=prompts_rowindex,column=3,sticky=N+S+W+E)

    prompts_rowindex += 1

    if warning != None:
        warn = Label(prompts,text=warning,bd=5)
        warn['background'] = '#ee2'
        warn['foreground'] = '#f00'
        warn.grid(row=prompts_rowindex,column=0,sticky=N+S+W+E)
        prompts_rowindex += 1

    prompts.grid(row=0,column=0,columnspan=2,sticky=N+S+W+E)
    # Prompts End

    def refresh(*args):
        if yscroll.get()[1] == 1.0:
            newcontent = ''
            if os.path.isfile(logfilepath):
                newcontent = open(logfilepath,'r').read()
            if newcontent != '':
                msgbox['state'] = NORMAL
                msgbox.delete(1.0,END)
                msgbox.insert(END,newcontent)
                msgbox['state'] = DISABLED
                msgbox.see(END)
            else:
                log.warning('No logfile found. Try logging to create one.')
        currentTime['text'] = time.strftime('%Y-%m-%d %H:%M:%S')
        root.after(500,refresh)

    root.after(0,refresh)

    root.title('ξ系统 - 系统日志')

    _utils.center_window(root)
    root.resizable(0,0)
    root.mainloop()

if __name__ == "__main__":
    print logviewer('报告')#,'日志空间即将不足，请考虑删除一部分。')
