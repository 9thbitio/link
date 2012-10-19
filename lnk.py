#!/usr/bin/env python

import sys
import os
from link import lnk
from optparse import OptionParser
from subprocess import Popen

parser = OptionParser()

parser.add_option("-i", "--install", dest="install", 
                  help="install this file in the wrappers directory")

parser.add_option("-r", "--install_git", dest="install_git",
                  help="install from git location into wrappers file")

parser.add_option("-g", "--global_install",
                  dest="global_install",action="store_true",  default=False,
                  help="If set to global it will be installed into link in site packages")

def get_shell_commands():
    lnk.run_command("find /usr/local/bin/ -perm -u+x,g+x ")

def get_from_git(location):
    """
    Run git and put the data in the plugins tmp directory.  
    From there install it
    """
    tmp = lnk.plugins_directory()
    name = location.split("/")[-1].split('.')[0]
    clone_to = '%s/%s' % (tmp, name)
    print "getting the plugin from git and placing in %s" % clone_to
    p = Popen("git clone %s %s" % (location ,clone_to), shell=True)
    p.wait()
    print "done getting file"
    return clone_to

class ShCmd(object):

    def __init__(self, command, directory):
        self.command = command
        self.directory = directory

class LnkSh(object):
    """
    lnk shell class.  Allows you to call either a shell command or
    a command configured in lnk.
    
        # start hbase from your shell
        shell> lnk dbs.hbase.stop
        stopping...
    
    """
    def __init__(self, options=None):
        self.options = self._parse_options(options)
        self.shell_commands = None
        self.path = os.environ.get("PATH", "")

    def _parse_options(self, options):
        """
        Options may come in as command line args.  need to change them
        into a dictionary.  Also removes any None's from the parser args because
        that means they aren't set and we don't want that overriding global args
        """
        if not options:
            return {}

        from optparse import Values
        #if straight from a parser use it's dictionary
        if isinstance(options, Values):
            #remove the nones
            return dict(
                        [(key, value) for key, value in
                            options.__dict__.iteritems()
                        if value!=None]
                       )
        return options
 
    
    def lookup_lnk(self):
        """
        Lookup to see if it's something lnk has configured
        """

    def get_shell_commands(self):
        """
        Get all executable commands in your PATH
        """
        self.shell_commands = {}
        command_dirs = self.path.split(":")
        #you want to look them up backwords so that commands in the beginning of
        #the path overwrite the ones in the back
        # PATH=/usr/bin:/usr/local/bin
        # we want to prefer those in /usr/bin
        command_dirs.reverse()
        #get all the commands
        commands = [os.listdir(dir) for dir in command_dirs] 
        commands = zip(commands, command_dirs)
        final_commands = []
        for cmds, dir in commands:
            final_commands.extend(
                [(cmd, dir) for cmd in cmds 
                    if os.access('%s/%s' % (dir, cmd), os.X_OK)]
            )
        
        #return an indexed map
        #this is where the overwritting hoppens.  dict creation prefers the
        #second instance
        return dict([(cmd, ShCmd(cmd, dir)) for cmd, dir in final_commands])
    
    def lookup_shell(self, command):
        """
        """
        if not self.shell_commands:
            self.shell_commands = self.get_shell_commands()

        print self.shell_commands

    def __call__(self, command, options=None):
        """
        call the actual command.  Override global options
        """
        _options = {}

        if options:
            _options = self.options.copy()
            _options.update(
                        self._parse_options(options)
                        )
        
        self.lookup_shell("thaseu")
        #TODO: Take care of aliases
        print _options
        print command
    

def main():
    """
    Take in user input.  Start up the vlnk shell
    """
    (options, args) = parser.parse_args()

    lnk_sh = LnkSh()
    lnk_sh(args, options)
    sys.exit()

    install_file = options.install
    install_git = options.install_git
    install_global = options.global_install
    
    #if 'commands' in args:
        #get_shell_commands(

    if install_file:
        lnk.install_plugin(install_file, install_global)
    elif install_git:
        install_file = get_from_git(install_git)
        #lnk.install_plugin(install_file, install_global)

if __name__ == '__main__':
    main()

