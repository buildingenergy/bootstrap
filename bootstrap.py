#!/usr/bin/env python
# bootstrap.py - Fancy one-line bootstrap magic for BE
# Installs command-line tools, brew, and flint by default

import sys, os, subprocess, tempfile

OSX_CLT_URLS = {
    "10.9": "http://adc-mirror.s3-us-west-2.amazonaws.com/command_line_tools_os_x_mavericks_for_xcode__late_october_2013.dmg",
    "10.8": "http://adcdownload.apple.com/Developer_Tools/command_line_tools_os_x_mountain_lion_for_xcode__october_2012/xcode451cltools_10_86938200a.dmg",
    "10.7": "http://adcdownload.apple.com/Developer_Tools/cltools_lion_from_xcode_4.5.1/xcode451cltools_10_76938201a.dmg",
    "10.6": "http://adcdownload.apple.com/Developer_Tools/command_line_tools_for_xcode_4.5_os_x_lion__september_2012/command_line_tools_for_xcode_4.5_os_x_lion.dmg",
}
VIRTUALBOX_URL = "http://dlc.sun.com.edgesuite.net/virtualbox/4.3.2/VirtualBox-4.3.2-90405-OSX.dmg"
VAGRANT_URL = "http://downloads.vagrantup.com/tags/v1.0.5"

def call(cmd, return_output=True):
    """
    Cheesy wrapper around subprocess to make life easier
    """
    cmd = "if [ -f ~/.flintrc ]; then . ~/.flintrc; fi; export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/share/python:$PATH; %s" % cmd
    try:
        if return_output: return subprocess.check_output(cmd, shell=True)
        else: return subprocess.call(cmd, shell=True, stdout=None, stderr=None)
    except subprocess.CalledProcessError: return None

def program_exists(cmd):
    """
    Uses `which` to determine whether a command is installed and accessible
    """
    return call("which %s" % cmd) not in ('', None)

def pkg_installed(pkg):
    """
    Uses pkgutil to check whether a pkg has been installed on the local system
    """
    return bool(call("pkgutil --pkgs | grep %s" % pkg))

def install_homebrew():
    """
    Uses the brew script to install homebrew
    """
    call("curl -fsSkL raw.github.com/mxcl/homebrew/go | ruby")
    if not program_exists("brew"): return False
    call("brew update")
    return True

def install_virtualbox():
    """
    Downloads virtualbox and installs it, with magic and ponies
    """
    destination = tempfile.mktemp(".dmg")
    call("curl -o %s %s" % (destination, VIRTUALBOX_URL))
    call("hdiutil attach -noautoopen %s" % destination)
    call("sudo -S installer -target / -pkg /Volumes/VirtualBox/VirtualBox.pkg")
    call("hdiutil detach /Volumes/VirtualBox")
    os.remove(destination)
    if os.path.exists("/Applications/VirtualBox.app"): return True
    return False

def install_cltools():
    """
    Downloads XCode CLI tools and installed them, with magic and ponies
    """
    if not OS_VERSION in OSX_CLT_URLS:
        print "Cannot find CLI Tools for Mac OS X %s" % OS_VERSION
        return False
    destination = tempfile.mktemp(".dmg")
    call("curl -o %s %s" % (destination, OSX_CLT_URLS[OS_VERSION]))
    call("hdiutil attach -noautoopen %s" % destination)
    call("sudo -S installer -target / -pkg /Volumes/Command\ Line\ Developer\ Tools/Command\ Line\ Tools\ \(OS\ X\ 10.9\).pkg")
    call("hdiutil detach /Volumes/Command\ Line\ Developer\ Tools")
    os.remove(destination)
    if pkg_installed("com.apple.pkg.CLTools_Executables"): return True
    return False

def install_puppet():
    """
    Uses the standard gem installer to install puppet
    """
    call("sudo gem install puppet")
    if not program_exists("puppet"): return False
    return True

def install_vagrant():
    """
    Uses the standard gem installer to install vagrant
    """
    call("sudo gem install vagrant")
    if not program_exists("vagrant"): return Fale
    return True

def install_python27():
    call("brew install python")
    if not os.path.exists("/usr/local/bin/python2.7"): return False
    return True

def install_pip():
    call("/usr/local/bin/easy_install-2.7 pip")
    if not os.path.exists("/usr/local/bin/pip"): return False
    return True

def install_git():
    call("brew install git")
    if not os.path.exists("/usr/local/bin/git"): return False
    return True

def install_gitflow():
    call("brew install git-flow")
    if not os.path.exists("/usr/local/bin/git-flow"): return False
    return True

def install_virtualenv():
    call("/usr/local/bin/pip install virtualenv")
    if not os.path.exists('/usr/local/lib/python2.7/site-packages') or not call("ls /usr/local/lib/python2.7/site-packages | grep virtualenv-"): return False
    return True

def install_virtualenvwrapper():
    call("/usr/local/bin/pip install virtualenvwrapper")
    if not os.path.exists('/usr/local/lib/python2.7/site-packages') or not call("ls /usr/local/lib/python2.7/site-packages | grep virtualenvwrapper-"): return False
    return True

def install_flint():
    call("/usr/local/bin/pip install git+ssh://git@github.com/buildingenergy/flint.git#egg=flint -q --upgrade")
    if not program_exists("use_flint"): return False
    return True

def configure_git():
    username = raw_input("Please enter your name: ")
    email    = raw_input("Please enter your email: ")
    call("git config --global user.name '%s'" % username)
    call("git config --global user.email %s" % email)

def configure_flint():
    flint_rc = """alias kill_pyc="find . -name '*.pyc' -delete"
    export BE_BOOTSTRAP_VERSION=1.2
    export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/share/python:/usr/local/share/npm/bin:$PATH
    if [ -f /usr/local/share/python/virtualenvwrapper.sh ]; then
        source /usr/local/share/python/virtualenvwrapper.sh
        fi
        source /usr/local/etc/flint/flint_wrapper.sh
        source /usr/local/etc/flint/flint_autocompletion.sh"""
    if not call("grep .flintrc ~/.bash_profile"):
        call("echo . ~/.flintrc >> ~/.bash_profile")
    f = open(os.path.join(os.path.expanduser("~"), ".flintrc"), 'w')
    f.write(flint_rc)
    f.close()

def main():
    global OS_VERSION, pw
    OS_VERSION = call("sw_vers -productVersion")[:-1]

    to_install = []

    # Check that we're actually a mac system
    if not OS_VERSION:
        print "Non-mac systems are not supported at this time."
        sys.exit(1)

    # Start with a sudo so we have credentials cached
    call('sudo echo')

    # Check that we can access BE code repos
    if call('ssh -q -o "StrictHostKeyChecking no" -T git@github.com 2> /dev/null', return_output=False) != 1:
        print 'ERROR: Cannot access BE code repos; are your keys present both locally and on github?'
        sys.exit(1)
    
    # Check that XCode tools are installed
    if not pkg_installed("com.apple.pkg.CLTools_Executables"): to_install.append("cltools")

    # Check for homebrew installation
    if not program_exists("brew"): to_install.append("homebrew")

    # Check for Virtualbox
    if not os.path.exists("/Applications/Virtualbox.app"): to_install.append("virtualbox")

    # Check for Puppet
    if not program_exists("puppet"): to_install.append("puppet")

    # Check for Vagrant
    if not program_exists("vagrant"): to_install.append("vagrant")

    # Check for Python2.7
    if not os.path.exists("/usr/local/bin/python2.7"): to_install.append("python27")

    # Check for pip
    if not os.path.exists("/usr/local/bin/pip"): to_install.append("pip")

    # Check for git
    if not os.path.exists("/usr/local/bin/git"): to_install.append("git")

    # Check for git-flow
    if not os.path.exists("/usr/local/bin/git-flow"): to_install.append("gitflow")

    # Check for virtualenv
    if not os.path.exists('/usr/local/lib/python2.7/site-packages') or not call("ls /usr/local/lib/python2.7/site-packages | grep virtualenv-"): to_install.append("virtualenv")

    # Check for virtualenvwrapper
    if not os.path.exists('/usr/local/lib/python2.7/site-packages') or not call("ls /usr/local/lib/python2.7/site-packages | grep virtualenvwrapper-"): to_install.append("virtualenvwrapper")

    # Check for flint
    if not os.path.exists('/usr/local/lib/python2.7/site-packages') or not call("ls /usr/local/lib/python2.7/site-packages | grep flint"): to_install.append("flint")

    # Do silly sublime packages
    # Do I really have to?

    # Check if we even need to continue bootstrapping
    if not to_install:
        print 'All dependencies seem to be installed already.'
    else:
        # Notify the user of pending installations
        print "The following dependencies were not found on your system, and will be installed:"
        for x in to_install: print "\t%s" % x

        # Install dependencies
        for dependency in to_install:
            func = globals()['install_%s' % dependency]
            print "### Installing %s ###" % dependency
            success = func()
            if not success:
                print "ERROR: Could not install %s" % dependency
                print "Aborting bootstrap process"
                sys.exit(1)

    if not os.path.exists("~/.flintrc"):
        print "### Configuring Flint ###"
        configure_flint()

    if not os.path.exists("~/.gitconfig"):
        print "### Configuring Git ###"
        configure_git()

    # Complete!
    print """###                Bootstrap Complete!                   ###

    You can now use flint to work on our codebase.
    To get started, reload your bash profile then start using flint!:

    source ~/.bash_profile
    flint help"""

if __name__ == '__main__': main()
