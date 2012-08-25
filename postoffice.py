# -*- coding: utf-8 -*-

# Command-line management tool.

from cmd import *
from _util import colorshell
import os,sys,argparse

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))

class postoffice_shell(Cmd):
    prompt = 'Xi.Postoffice > '

    def cmdloop(self, intro=None):
        print '*' * 80
        print '*' + colorshell(' Welcome to Postoffice ',1,0).center(88,' ') + '*'
        print '* This is user interface to top-secret system Xi\'s frontend.' + 19 * ' ' + '*'
        print '*' + 78 * ' ' + '*'
        print '* %-74s *' % 'To get help: %s' % colorshell('help',1,0)
        print '* %-66s *' % 'To exit: %s or %s or %s' % (colorshell('exit',1,0),colorshell('quit',1,0),colorshell('<Ctrl+D>',1,0))
        print colorshell(' Attention! ',31).center(91,'*')
        print '* %-56s *' % '%s checking system integrity with: %s' % (colorshell('ALWAYS remember',33,1),colorshell('selfcheck',1,0))
        print '*' * 80
        Cmd.cmdloop(self, intro)

    def do_issue(self,line):
        print line
    def do_selfcheck(self,line): self._run_python('tool.selfcheck.py')

    def do_EOF(self,line) : exit()
    def do_exit(self,line): self.do_EOF(line)
    def do_quit(self,line): self.do_EOF(line)

    def _show_usage(self,cmdfmt,desc): print '%s: %s\n\n%s' % (colorshell('Usage',1,4),cmdfmt,desc)
    def _run_python(self,filename):
        global BASEPATH
        os.system('python ' + os.path.join(BASEPATH,filename))
    def help_issue(self)    : self._show_usage('issue certificate|signature','generate new certificate, or sign a known certificate.')
    def help_EOF(self)      : self._show_usage('exit|quit|<Ctrl+D>','Exit this shell.')
    def help_help(self)     : self._show_usage('help [CommandName]','Show help on specific command or full document.')
    def help_selfcheck(self): self._show_usage('selfcheck','Calculate and list checksums of basic system configurations.')

    def help_exit(self): self.help_EOF()
    def help_quit(self): self.help_EOF()

    def default(self,line): print "Bad command: %s" % line
    def emptyline(self): pass

if __name__ == '__main__':
    os.system('clear')

    sh = postoffice_shell()

    sh.cmdloop()
