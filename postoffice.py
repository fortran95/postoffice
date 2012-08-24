# -*- coding: utf-8 -*-

# Command-line management tool.

from cmd import *
import os,argparse

class postoffice_shell(Cmd):
    prompt = 'Xi.Postoffice > '

    def do_issue(self,line):
        print line

    def do_EOF(self,line) : exit()
    def do_exit(self,line): self.do_EOF(line)
    def do_quit(self,line): self.do_EOF(line)

    def help_issue(self)  : print 'Issue: <issue certificate|signature>, generate new certificate, or sign a known certificate.'
    def help_EOF(self)    : print 'Sending an EOF(usually by pressing <CTRL+D>) or using command <quit>, <exit> will exit this shell.'
    def help_help(self)   : print 'Use <help command_name> to show help on commands.'

    def help_exit(self): self.help_EOF()
    def help_quit(self): self.help_EOF()

    def default(self,line): print "Bad command: %s" % line
    def emptyline(self): pass

if __name__ == '__main__':
    os.system('clear')

    sh = postoffice_shell()

    intro = '\n    Xi.Postoffice::Shell\n\n #IMPORTANT# Examine these checksums to check system integrity:\n  * Root Certificates:\n'

    sh.cmdloop(intro)
