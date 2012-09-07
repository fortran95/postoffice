# -*- coding: utf-8 -*-

# Command-line management tool.

from cmd import *
from _util import colorshell
import os,sys,argparse

import tool_selfcheck

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))

class postoffice_shell(Cmd):
    prompt = 'Xi.Postoffice > '

    def cmdloop(self, intro=None):
        selfcheck = self.do_selfcheck('silent')

        os.system('clear')

        emptyline = '*' + 78 * ' ' + '*'
        print '*' * 80
        print '*' + colorshell(' Welcome to Postoffice ',1,0).center(88,' ') + '*'
        print '* This is user interface to top-secret system Xi\'s frontend.' + 19 * ' ' + '*'
        print emptyline
        print "* %-76s *" % "Xi-System  Copyright (C) 2012  NERV"
        print "* %-76s *" % "This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'." # FIXME show w
        print "* %-76s *" % "This is free software, and you are welcome to redistribute it"
        print "* %-76s *" % "under certain conditions; type `show c' for details." # FIXME show c
        print emptyline
        print '* %-74s *' % 'To get help: %s' % colorshell('help',1,0)
        print '* %-66s *' % 'To exit: %s or %s or %s' % (colorshell('exit',1,0),colorshell('quit',1,0),colorshell('<Ctrl+D>',1,0))
        print emptyline
        print '* %-59s *' % 'System Checksum: %s' % colorshell(tool_selfcheck.friendly_display(selfcheck['total']).strip(),31,1)
        print '* %-56s *' % '%s checking system integrity with: %s' % (colorshell('ALWAYS remember',31,1),colorshell('selfcheck',1,0))
        print '*' * 80
        Cmd.cmdloop(self, intro)

    def do_issue(self,line):
        line = line.lower()
        if   line.startswith('cert'):
            self._run_python('tool_certnew.py')
        elif line.startswith('sign'):
            self._run_python('tool_signnew.py')
    def do_selfcheck(self,line):
        if line.lower().startswith('silent'):
            return tool_selfcheck.do(True)
        else:
            tool_selfcheck.do(False)

    def do_EOF(self,line) : os.system('clear'); self.do_selfcheck(''); exit()
    def do_exit(self,line): self.do_EOF(line)
    def do_quit(self,line): self.do_EOF(line)

    def _show_usage(self,cmdfmt,desc): print '%s: %s\n%s' % (colorshell('Usage',1,4),cmdfmt,desc)
    def _run_python(self,filename):
        global BASEPATH
        os.system('python ' + os.path.join(BASEPATH,filename))
    def help_issue(self)    : self._show_usage('issue cert|sign','generate new certificate, or sign a known certificate.')
    def help_EOF(self)      : self._show_usage('exit|quit|<Ctrl+D>','Exit this shell.')
    def help_help(self)     : self._show_usage('help [CommandName]','Show help on specific command or full document.')
    def help_selfcheck(self):
        self._show_usage('selfcheck',
            '''
Calculate and list checksums of basic system configurations.

  Root certificates, system programs and system configure files are monitored with this command. Each file is hashed with SHA-1, the resulting checksums joined and hashed with SHA-224. A short and easy to remember CRC32+ADLER32 checksum of these results is also provided.
  This command provides user with friendly parameters that cover entire system's status. System administrator should be familiar with the short CRC32+ADLER32 checksum of a well-configured system, while others recorded on the paper. So that if he found the short code being different one day, he could tell where in this system has been modified(thus making system potentially insecure) and fix that.
            '''.strip()
        )

    def help_exit(self): self.help_EOF()
    def help_quit(self): self.help_EOF()

    def default(self,line): print "Bad command: %s" % line
    def emptyline(self): pass

if __name__ == '__main__':
    os.system('clear')

    sh = postoffice_shell()

    sh.cmdloop()
